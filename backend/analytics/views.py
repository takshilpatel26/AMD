"""
Analytics Views - API endpoints for consumption analytics, trends, and insights
Integrated with trained ML models for forecasting and anomaly detection
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg, Max, Min, Count
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from .models import EnergyForecast, ConsumptionPattern, EfficiencyScore, CarbonImpact
from .serializers import (
    EnergyForecastSerializer, ConsumptionPatternSerializer,
    EfficiencyScoreSerializer, CarbonFootprintSerializer,
    ConsumptionTrendSerializer, AnalyticsSummarySerializer
)
from meters.models import Meter, MeterReading, Alert
from .ml_service import get_ml_service
import logging

logger = logging.getLogger(__name__)


class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for analytics endpoints
    """
    permission_classes = [IsAuthenticated]
    
    def _get_user_meters(self):
        """Get all meters for current user"""
        return Meter.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get analytics summary
        GET /api/v1/analytics/summary/?days=7
        """
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        meters = self._get_user_meters()
        
        # Get readings for period
        readings = MeterReading.objects.filter(
            meter__in=meters,
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        )
        
        # Calculate aggregates
        total_energy = readings.aggregate(total=Sum('energy'))['total'] or 0
        avg_power = readings.aggregate(avg=Avg('power'))['avg'] or 0
        
        # Calculate cost (₹6 per kWh average)
        total_cost = Decimal(total_energy) * Decimal('6.00')
        
        # Get efficiency scores
        efficiency_scores = EfficiencyScore.objects.filter(
            meter__in=meters,
            date__gte=start_date,
            date__lte=end_date
        )
        avg_efficiency = efficiency_scores.aggregate(avg=Avg('score'))['avg'] or 0
        
        # Get carbon footprint
        carbon_data = CarbonImpact.objects.filter(
            meter__in=meters,
            date__gte=start_date,
            date__lte=end_date
        )
        total_carbon = carbon_data.aggregate(total=Sum('carbon_emitted'))['total'] or 0
        
        # Calculate potential savings
        total_wasted = efficiency_scores.aggregate(total=Sum('wasted_energy'))['total'] or 0
        potential_savings = Decimal(total_wasted) * Decimal('6.00')
        
        data = {
            'total_energy': round(total_energy, 2),
            'total_cost': total_cost,
            'avg_efficiency': round(avg_efficiency, 2),
            'total_carbon': round(total_carbon, 2),
            'potential_savings': potential_savings,
            'period_start': start_date,
            'period_end': end_date,
        }
        
        serializer = AnalyticsSummarySerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def consumption(self, request):
        """
        Get consumption trends
        GET /api/v1/analytics/consumption/?days=30&meter_id=GJ-ANAND-001
        """
        days = int(request.query_params.get('days', 30))
        meter_id = request.query_params.get('meter_id')
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        meters = self._get_user_meters()
        if meter_id:
            meters = meters.filter(meter_id=meter_id)
        
        # Group readings by date
        readings = MeterReading.objects.filter(
            meter__in=meters,
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        ).values('timestamp__date').annotate(
            total_energy=Sum('energy'),
            avg_power=Avg('power'),
            max_power=Max('power')
        ).order_by('timestamp__date')
        
        # Build trend data
        trends = []
        for reading in readings:
            date = reading['timestamp__date']
            energy = reading['total_energy'] or 0
            
            # Get efficiency score for date
            eff_score = EfficiencyScore.objects.filter(
                meter__in=meters,
                date=date
            ).aggregate(avg=Avg('score'))['avg'] or 0
            
            trends.append({
                'date': date,
                'energy': round(energy, 2),
                'avg_power': round(reading['avg_power'] or 0, 2),
                'peak_power': round(reading['max_power'] or 0, 2),
                'cost': Decimal(energy) * Decimal('6.00'),
                'efficiency_score': int(eff_score)
            })
        
        serializer = ConsumptionTrendSerializer(trends, many=True)
        return Response({
            'success': True,
            'period': {'start': start_date, 'end': end_date},
            'trends': serializer.data,
            'total_days': len(trends)
        })
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """
        Get detailed consumption trends with comparison
        GET /api/v1/analytics/trends/?meter_id=GJ-ANAND-001&period=week
        """
        meter_id = request.query_params.get('meter_id')
        period = request.query_params.get('period', 'week')  # day, week, month
        
        meters = self._get_user_meters()
        if meter_id:
            meters = meters.filter(meter_id=meter_id)
        
        if not meters.exists():
            return Response(
                {'error': 'No meters found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate date ranges
        end_date = timezone.now().date()
        if period == 'day':
            current_start = end_date
            previous_start = end_date - timedelta(days=1)
            previous_end = end_date - timedelta(days=1)
        elif period == 'week':
            current_start = end_date - timedelta(days=6)
            previous_start = end_date - timedelta(days=13)
            previous_end = end_date - timedelta(days=7)
        else:  # month
            current_start = end_date - timedelta(days=29)
            previous_start = end_date - timedelta(days=59)
            previous_end = end_date - timedelta(days=30)
        
        # Get current period data
        current_readings = MeterReading.objects.filter(
            meter__in=meters,
            timestamp__date__gte=current_start,
            timestamp__date__lte=end_date
        )
        
        current_energy = current_readings.aggregate(total=Sum('energy'))['total'] or 0
        current_avg_power = current_readings.aggregate(avg=Avg('power'))['avg'] or 0
        
        # Get previous period data
        previous_readings = MeterReading.objects.filter(
            meter__in=meters,
            timestamp__date__gte=previous_start,
            timestamp__date__lte=previous_end
        )
        
        previous_energy = previous_readings.aggregate(total=Sum('energy'))['total'] or 0
        previous_avg_power = previous_readings.aggregate(avg=Avg('power'))['avg'] or 0
        
        # Calculate changes
        energy_change = ((current_energy - previous_energy) / previous_energy * 100) if previous_energy > 0 else 0
        power_change = ((current_avg_power - previous_avg_power) / previous_avg_power * 100) if previous_avg_power > 0 else 0
        
        return Response({
            'success': True,
            'period': period,
            'current_period': {
                'start': current_start,
                'end': end_date,
                'energy': round(current_energy, 2),
                'avg_power': round(current_avg_power, 2),
                'cost': float(Decimal(current_energy) * Decimal('6.00'))
            },
            'previous_period': {
                'start': previous_start,
                'end': previous_end,
                'energy': round(previous_energy, 2),
                'avg_power': round(previous_avg_power, 2),
                'cost': float(Decimal(previous_energy) * Decimal('6.00'))
            },
            'comparison': {
                'energy_change_percent': round(energy_change, 2),
                'power_change_percent': round(power_change, 2),
                'trend': 'up' if energy_change > 0 else 'down' if energy_change < 0 else 'stable'
            }
        })
    
    @action(detail=False, methods=['get'])
    def efficiency(self, request):
        """
        Get efficiency analysis
        GET /api/v1/analytics/efficiency/?meter_id=GJ-ANAND-001&days=30
        """
        meter_id = request.query_params.get('meter_id')
        days = int(request.query_params.get('days', 30))
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        meters = self._get_user_meters()
        if meter_id:
            meters = meters.filter(meter_id=meter_id)
        
        # Get efficiency scores
        scores = EfficiencyScore.objects.filter(
            meter__in=meters,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        if not scores.exists():
            return Response({
                'success': True,
                'message': 'No efficiency data available',
                'scores': []
            })
        
        # Calculate aggregates
        avg_score = scores.aggregate(avg=Avg('score'))['avg'] or 0
        avg_power_factor = scores.aggregate(avg=Avg('power_factor_score'))['avg'] or 0
        total_wasted = scores.aggregate(total=Sum('wasted_energy'))['total'] or 0
        
        serializer = EfficiencyScoreSerializer(scores, many=True)
        
        return Response({
            'success': True,
            'period': {'start': start_date, 'end': end_date},
            'summary': {
                'avg_efficiency_score': round(avg_score, 2),
                'avg_power_factor_score': round(avg_power_factor, 2),
                'total_wasted_energy': round(total_wasted, 2),
                'potential_savings': float(Decimal(total_wasted) * Decimal('6.00')),
                'grade': self._get_grade(avg_score)
            },
            'scores': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def forecasts(self, request):
        """
        Get energy forecasts
        GET /api/v1/analytics/forecasts/?meter_id=GJ-ANAND-001&days=7
        """
        meter_id = request.query_params.get('meter_id')
        days = int(request.query_params.get('days', 7))
        
        meters = self._get_user_meters()
        if meter_id:
            meters = meters.filter(meter_id=meter_id)
        
        today = timezone.now().date()
        forecast_end = today + timedelta(days=days)
        
        # Get forecasts
        forecasts = EnergyForecast.objects.filter(
            meter__in=meters,
            forecast_date__gte=today,
            forecast_date__lte=forecast_end
        ).order_by('forecast_date', 'forecast_hour')
        
        serializer = EnergyForecastSerializer(forecasts, many=True)
        
        # Calculate summary
        total_predicted = forecasts.aggregate(total=Sum('predicted_energy'))['total'] or 0
        avg_confidence = forecasts.aggregate(avg=Avg('confidence_score'))['avg'] or 0
        
        return Response({
            'success': True,
            'period': {'start': today, 'end': forecast_end},
            'summary': {
                'total_predicted_energy': round(total_predicted, 2),
                'avg_confidence': round(avg_confidence, 2),
                'estimated_cost': float(Decimal(total_predicted) * Decimal('6.00'))
            },
            'forecasts': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def patterns(self, request):
        """
        Get consumption patterns
        GET /api/v1/analytics/patterns/?meter_id=GJ-ANAND-001&type=weekly
        """
        meter_id = request.query_params.get('meter_id')
        pattern_type = request.query_params.get('type', 'weekly')
        
        meters = self._get_user_meters()
        if meter_id:
            meters = meters.filter(meter_id=meter_id)
        
        # Get patterns
        patterns = ConsumptionPattern.objects.filter(
            meter__in=meters,
            pattern_type=pattern_type
        ).order_by('-period_end')[:10]  # Last 10 patterns
        
        serializer = ConsumptionPatternSerializer(patterns, many=True)
        
        return Response({
            'success': True,
            'pattern_type': pattern_type,
            'count': patterns.count(),
            'patterns': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def carbon_footprint(self, request):
        """
        Get carbon footprint data
        GET /api/v1/analytics/carbon_footprint/?days=30
        """
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        meters = self._get_user_meters()
        
        # Get carbon data
        carbon_data = CarbonImpact.objects.filter(
            meter__in=meters,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        serializer = CarbonFootprintSerializer(carbon_data, many=True)
        
        # Calculate totals
        total_emitted = carbon_data.aggregate(total=Sum('carbon_emitted'))['total'] or 0
        total_saved = carbon_data.aggregate(total=Sum('carbon_saved'))['total'] or 0
        net_carbon = total_emitted - total_saved
        
        return Response({
            'success': True,
            'period': {'start': start_date, 'end': end_date},
            'summary': {
                'total_carbon_emitted': round(total_emitted, 2),
                'total_carbon_saved': round(total_saved, 2),
                'net_carbon': round(net_carbon, 2),
                'trees_equivalent': round(total_emitted / 21, 2)
            },
            'daily_data': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def detect_anomaly(self, request):
        """
        Detect anomalies in real-time meter reading using trained ML model
        POST /api/v1/analytics/detect_anomaly/
        
        Request Body:
        {
            "meter_id": "GJ-ANAND-001",
            "voltage": 235.5,
            "current": 12.3,
            "power": 2.85,
            "energy": 156.7,
            "power_factor": 0.95,
            "frequency": 50.1
        }
        
        Response:
        {
            "is_anomaly": true,
            "severity": "warning",
            "message": "WARNING: Unusual Usage Pattern Detected by AI",
            "reading_data": {...},
            "timestamp": "2025-12-26T10:30:00Z",
            "alert_created": true
        }
        """
        ml_service = get_ml_service()
        
        # Extract reading data
        reading_data = {
            'voltage': float(request.data.get('voltage', 230)),
            'current': float(request.data.get('current', 0)),
            'power': float(request.data.get('power', 0)),
            'energy': float(request.data.get('energy', 0)),
            'power_factor': float(request.data.get('power_factor', 0.95)),
            'frequency': float(request.data.get('frequency', 50.0)),
            'timestamp': timezone.now()
        }
        
        meter_id = request.data.get('meter_id')
        
        # Perform anomaly detection
        is_anomaly, severity, message = ml_service.detect_anomaly(reading_data)
        
        # Create alert if anomaly detected
        alert_created = False
        if is_anomaly:
            try:
                meter = Meter.objects.get(meter_id=meter_id, user=request.user)
                
                # Determine alert type based on message
                alert_type = 'voltage_spike'
                if 'Voltage Drop' in message or 'Brownout' in message:
                    alert_type = 'voltage_drop'
                elif 'Overcurrent' in message:
                    alert_type = 'overcurrent'
                elif 'Phantom Load' in message:
                    alert_type = 'phantom_load'
                
                Alert.objects.create(
                    meter=meter,
                    alert_type=alert_type,
                    severity=severity,
                    message=message,
                    is_resolved=False
                )
                alert_created = True
                logger.info(f"Alert created for meter {meter_id}: {message}")
                
            except Meter.DoesNotExist:
                logger.warning(f"Meter {meter_id} not found for user {request.user}")
            except Exception as e:
                logger.error(f"Error creating alert: {e}")
        
        return Response({
            'success': True,
            'is_anomaly': is_anomaly,
            'severity': severity,
            'message': message,
            'reading_data': reading_data,
            'timestamp': timezone.now(),
            'alert_created': alert_created,
            'meter_id': meter_id
        })
    
    @action(detail=False, methods=['post'])
    def predict_consumption(self, request):
        """
        Predict monthly consumption using trained ML model
        POST /api/v1/analytics/predict_consumption/
        
        Request Body:
        {
            "meter_id": "GJ-ANAND-001",
            "current_day": 15,
            "consumed_so_far": 125.5,
            "avg_pump_usage": 0.35,
            "avg_voltage": 228.5
        }
        
        Response:
        {
            "projected_monthly_kwh": 256.8,
            "projected_cost": 1540.80,
            "current_consumption": 125.5,
            "days_remaining": 15,
            "efficiency_score": 72.5,
            "efficiency_grade": "C",
            "cost_breakdown": {...}
        }
        """
        ml_service = get_ml_service()
        
        # Extract parameters
        current_day = int(request.data.get('current_day', timezone.now().day))
        consumed_so_far = float(request.data.get('consumed_so_far', 0))
        avg_pump_usage = float(request.data.get('avg_pump_usage', 0))
        avg_voltage = float(request.data.get('avg_voltage', 230))
        
        # Predict monthly consumption
        projected_monthly = ml_service.project_monthly_usage(
            current_day, 
            consumed_so_far,
            avg_pump_usage,
            avg_voltage
        )
        
        # Calculate cost
        projected_cost = ml_service.get_slab_cost(projected_monthly)
        current_cost = ml_service.get_slab_cost(consumed_so_far)
        
        # Calculate efficiency score
        efficiency_score = ml_service.calculate_efficiency_score(projected_monthly)
        efficiency_grade = ml_service.get_efficiency_grade(efficiency_score)
        
        # Cost breakdown by slab
        cost_breakdown = {
            'slab_1': min(projected_monthly, 100) * 3.5,
            'slab_2': max(0, min(projected_monthly - 100, 150)) * 5.2,
            'slab_3': max(0, projected_monthly - 250) * 7.5,
            'total': projected_cost
        }
        
        return Response({
            'success': True,
            'projected_monthly_kwh': projected_monthly,
            'projected_cost': round(projected_cost, 2),
            'current_consumption': consumed_so_far,
            'current_cost': round(current_cost, 2),
            'days_remaining': 30 - current_day,
            'efficiency_score': round(efficiency_score, 2),
            'efficiency_grade': efficiency_grade,
            'cost_breakdown': cost_breakdown,
            'model_used': 'trained_monthly_regression_model'
        })
    
    @action(detail=False, methods=['post'])
    def forecast_hourly(self, request):
        """
        Forecast next hour consumption using trained time-series model
        POST /api/v1/analytics/forecast_hourly/
        
        Request Body:
        {
            "meter_id": "GJ-ANAND-001",
            "historical_readings": [
                {"timestamp": "2025-12-26T09:00:00Z", "power": 2.5, "energy": 2.5},
                {"timestamp": "2025-12-26T10:00:00Z", "power": 3.2, "energy": 3.2},
                ...
            ]
        }
        
        Response:
        {
            "predicted_power": 2.85,
            "predicted_energy": 2.85,
            "confidence_score": 0.85,
            "lower_bound": 2.42,
            "upper_bound": 3.28,
            "model_type": "trained_ml_model"
        }
        """
        ml_service = get_ml_service()
        
        historical_readings = request.data.get('historical_readings', [])
        
        if not historical_readings:
            return Response({
                'success': False,
                'error': 'historical_readings required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Make prediction
        prediction = ml_service.predict_next_hour(historical_readings)
        
        return Response({
            'success': True,
            **prediction,
            'timestamp': timezone.now()
        })
    
    @action(detail=False, methods=['get'])
    def ml_weekly_forecast(self, request):
        """
        Get 7-day energy consumption forecast
        GET /api/v1/analytics/ml_weekly_forecast/?meter_id=GJ-ANAND-001
        
        Response:
        {
            "forecast": [
                {"date": "2025-12-27", "predicted_energy": 12.5, "confidence": 0.75},
                ...
            ]
        }
        """
        ml_service = get_ml_service()
        meter_id = request.query_params.get('meter_id')
        
        if not meter_id:
            return Response({
                'success': False,
                'error': 'meter_id required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            meter = Meter.objects.get(meter_id=meter_id, user=request.user)
            
            # Get historical readings (last 30 days)
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            
            readings = MeterReading.objects.filter(
                meter=meter,
                timestamp__gte=start_date
            ).values('timestamp', 'energy', 'power')
            
            # Convert to list of dicts
            historical_data = [
                {
                    'timestamp': r['timestamp'],
                    'energy': r['energy'],
                    'power': r['power'] / 1000  # Convert W to kW
                }
                for r in readings
            ]
            
            # Generate forecast
            forecast = ml_service.predict_weekly_consumption(historical_data)
            
            return Response({
                'success': True,
                'meter_id': meter_id,
                'forecast': forecast,
                'historical_readings_count': len(historical_data)
            })
            
        except Meter.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Meter not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def ml_pattern_analysis(self, request):
        """
        Analyze consumption patterns and get AI-powered recommendations
        GET /api/v1/analytics/ml_pattern_analysis/?meter_id=GJ-ANAND-001&days=30
        
        Response:
        {
            "pattern": "analyzed",
            "peak_hours": [7, 19, 20],
            "off_peak_hours": [2, 3, 4],
            "recommendations": [...],
            "hourly_average": {...}
        }
        """
        ml_service = get_ml_service()
        meter_id = request.query_params.get('meter_id')
        days = int(request.query_params.get('days', 30))
        
        if not meter_id:
            return Response({
                'success': False,
                'error': 'meter_id required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            meter = Meter.objects.get(meter_id=meter_id, user=request.user)
            
            # Get readings
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            readings = MeterReading.objects.filter(
                meter=meter,
                timestamp__gte=start_date
            ).values('timestamp', 'power')
            
            # Convert to list
            reading_data = [
                {
                    'timestamp': r['timestamp'],
                    'power': r['power'] / 1000
                }
                for r in readings
            ]
            
            # Analyze patterns
            analysis = ml_service.analyze_consumption_pattern(reading_data)
            
            return Response({
                'success': True,
                'meter_id': meter_id,
                'analysis_period_days': days,
                **analysis
            })
            
        except Meter.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Meter not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def _get_grade(self, score):
        """Get letter grade from score"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
