"""
DRF Views for Distribution Network API
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Company, District, Village, Transformer, House,
    ElectricityReading, LossAlert, CompanyAdmin
)
from .serializers import (
    CompanySerializer, DistrictSerializer, DistrictListSerializer,
    VillageSerializer, VillageListSerializer,
    TransformerSerializer, TransformerListSerializer,
    HouseSerializer, HouseListSerializer,
    ElectricityReadingSerializer, LossAlertSerializer, LossAlertListSerializer,
    CompanyAdminSerializer, DistributionDashboardStatsSerializer,
    TransformerStatsSerializer
)
from .simulator import simulator


class CompanyViewSet(viewsets.ModelViewSet):
    """API endpoint for companies"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]  # Allow public access for demo

    @action(detail=True, methods=['get'])
    def dashboard_stats(self, request, pk=None):
        """Get dashboard statistics for a company"""
        company = self.get_object()
        stats = self._calculate_company_stats(company)
        serializer = DistributionDashboardStatsSerializer(stats)
        return Response(serializer.data)

    def _calculate_company_stats(self, company):
        """Calculate comprehensive statistics for a company"""
        districts = company.districts.all()
        
        total_villages = 0
        total_transformers = 0
        total_houses = 0
        
        for district in districts:
            villages = district.villages.all()
            total_villages += villages.count()
            for village in villages:
                transformers = village.transformers.all()
                total_transformers += transformers.count()
                for transformer in transformers:
                    total_houses += transformer.houses.count()
        
        # Get alerts
        active_alerts = LossAlert.objects.filter(
            district__company=company,
            status='active'
        ).count()
        
        critical_alerts = LossAlert.objects.filter(
            district__company=company,
            status='active',
            severity='critical'
        ).count()
        
        # Get recent readings aggregates
        recent_readings = ElectricityReading.objects.filter(
            transformer__village__district__company=company,
            reading_timestamp__gte=timezone.now() - timedelta(hours=24)
        )
        
        aggregates = recent_readings.aggregate(
            total_power_loss=Sum('power_loss_kw'),
            avg_loss_pct=Avg('power_loss_percentage'),
            anomaly_count=Count('id', filter=Q(is_anomaly=True))
        )
        
        # Count transformers with issues
        transformers_with_issues = Transformer.objects.filter(
            village__district__company=company,
            status__in=['faulty', 'maintenance']
        ).count()
        
        # Estimate financial loss
        total_loss = aggregates['total_power_loss'] or Decimal('0')
        rate_per_kwh = Decimal('7.50')
        estimated_financial_loss = total_loss * 24 * rate_per_kwh  # Daily projection
        
        return {
            'total_districts': districts.count(),
            'total_villages': total_villages,
            'total_transformers': total_transformers,
            'total_houses': total_houses,
            'active_alerts': active_alerts,
            'critical_alerts': critical_alerts,
            'total_power_loss_kw': total_loss,
            'average_loss_percentage': aggregates['avg_loss_pct'] or Decimal('0'),
            'estimated_financial_loss': estimated_financial_loss,
            'transformers_with_issues': transformers_with_issues,
            'houses_with_anomalies': aggregates['anomaly_count'] or 0,
        }


class DistrictViewSet(viewsets.ModelViewSet):
    """API endpoint for districts"""
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [AllowAny]  # Allow public access for demo

    def get_serializer_class(self):
        if self.action == 'list':
            return DistrictListSerializer
        return DistrictSerializer

    def get_queryset(self):
        queryset = District.objects.all()
        company_id = self.request.query_params.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        return queryset

    @action(detail=True, methods=['get'])
    def villages(self, request, pk=None):
        """Get all villages in this district"""
        district = self.get_object()
        villages = district.villages.all()
        serializer = VillageListSerializer(villages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """Get all active alerts in this district"""
        district = self.get_object()
        alerts = district.loss_alerts.filter(status='active')
        serializer = LossAlertListSerializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for this district"""
        district = self.get_object()
        
        villages = district.villages.all()
        total_transformers = sum(v.transformers.count() for v in villages)
        total_houses = sum(
            sum(t.houses.count() for t in v.transformers.all())
            for v in villages
        )
        
        active_alerts = district.loss_alerts.filter(status='active').count()
        
        recent_readings = ElectricityReading.objects.filter(
            transformer__village__district=district,
            reading_timestamp__gte=timezone.now() - timedelta(hours=24)
        )
        
        aggregates = recent_readings.aggregate(
            total_power_loss=Sum('power_loss_kw'),
            avg_loss_pct=Avg('power_loss_percentage'),
        )
        
        return Response({
            'district_id': str(district.id),
            'district_name': district.name,
            'total_villages': villages.count(),
            'total_transformers': total_transformers,
            'total_houses': total_houses,
            'active_alerts': active_alerts,
            'total_power_loss_kw': aggregates['total_power_loss'] or 0,
            'average_loss_percentage': aggregates['avg_loss_pct'] or 0,
        })


class VillageViewSet(viewsets.ModelViewSet):
    """API endpoint for villages"""
    queryset = Village.objects.all()
    serializer_class = VillageSerializer
    permission_classes = [AllowAny]  # Allow public access for demo

    def get_serializer_class(self):
        if self.action == 'list':
            return VillageListSerializer
        return VillageSerializer

    def get_queryset(self):
        queryset = Village.objects.all()
        district_id = self.request.query_params.get('district')
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        return queryset

    @action(detail=True, methods=['get'])
    def transformers(self, request, pk=None):
        """Get all transformers in this village"""
        village = self.get_object()
        transformers = village.transformers.all()
        serializer = TransformerListSerializer(transformers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """Get all active alerts in this village"""
        village = self.get_object()
        alerts = village.loss_alerts.filter(status='active')
        serializer = LossAlertListSerializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for this village"""
        village = self.get_object()
        
        transformers = village.transformers.all()
        total_houses = sum(t.houses.count() for t in transformers)
        active_alerts = village.loss_alerts.filter(status='active').count()
        
        recent_readings = ElectricityReading.objects.filter(
            transformer__village=village,
            reading_timestamp__gte=timezone.now() - timedelta(hours=24)
        )
        
        aggregates = recent_readings.aggregate(
            total_power_loss=Sum('power_loss_kw'),
            avg_loss_pct=Avg('power_loss_percentage'),
        )
        
        return Response({
            'village_id': str(village.id),
            'village_name': village.name,
            'total_transformers': transformers.count(),
            'total_houses': total_houses,
            'active_alerts': active_alerts,
            'total_power_loss_kw': aggregates['total_power_loss'] or 0,
            'average_loss_percentage': aggregates['avg_loss_pct'] or 0,
        })


class TransformerViewSet(viewsets.ModelViewSet):
    """API endpoint for transformers"""
    queryset = Transformer.objects.all()
    serializer_class = TransformerSerializer
    permission_classes = [AllowAny]  # Allow public access for demo

    def get_serializer_class(self):
        if self.action == 'list':
            return TransformerListSerializer
        return TransformerSerializer

    def get_queryset(self):
        queryset = Transformer.objects.all()
        village_id = self.request.query_params.get('village')
        if village_id:
            queryset = queryset.filter(village_id=village_id)
        return queryset

    @action(detail=True, methods=['get'])
    def houses(self, request, pk=None):
        """Get all houses powered by this transformer"""
        transformer = self.get_object()
        houses = transformer.houses.all()
        serializer = HouseListSerializer(houses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def readings(self, request, pk=None):
        """Get recent readings for this transformer"""
        transformer = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        
        readings = ElectricityReading.objects.filter(
            transformer=transformer,
            reading_timestamp__gte=timezone.now() - timedelta(hours=hours)
        )[:100]
        
        serializer = ElectricityReadingSerializer(readings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """Get all active alerts for this transformer"""
        transformer = self.get_object()
        alerts = transformer.loss_alerts.filter(status='active')
        serializer = LossAlertListSerializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get detailed statistics for this transformer"""
        transformer = self.get_object()
        houses = transformer.houses.all()
        
        recent_readings = ElectricityReading.objects.filter(
            transformer=transformer,
            reading_timestamp__gte=timezone.now() - timedelta(hours=24)
        )
        
        aggregates = recent_readings.aggregate(
            total_power_loss=Sum('power_loss_kw'),
            avg_voltage_loss=Avg('voltage_loss'),
            avg_power_loss=Avg('power_loss_kw'),
            houses_with_loss=Count('house', filter=Q(is_anomaly=True), distinct=True)
        )
        
        active_alerts = transformer.loss_alerts.filter(status='active').count()
        
        return Response({
            'transformer_id': transformer.transformer_id,
            'name': transformer.name,
            'total_houses': houses.count(),
            'houses_with_loss': aggregates['houses_with_loss'] or 0,
            'average_voltage_loss': round(float(aggregates['avg_voltage_loss'] or 0), 2),
            'average_power_loss': round(float(aggregates['avg_power_loss'] or 0), 3),
            'total_power_loss_kw': round(float(aggregates['total_power_loss'] or 0), 3),
            'active_alerts': active_alerts,
            'status': transformer.status,
        })


class HouseViewSet(viewsets.ModelViewSet):
    """API endpoint for houses"""
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [AllowAny]  # Allow public access for demo

    def get_serializer_class(self):
        if self.action == 'list':
            return HouseListSerializer
        return HouseSerializer

    def get_queryset(self):
        queryset = House.objects.all()
        transformer_id = self.request.query_params.get('transformer')
        if transformer_id:
            queryset = queryset.filter(transformer_id=transformer_id)
        return queryset

    @action(detail=True, methods=['get'])
    def readings(self, request, pk=None):
        """Get readings for this house"""
        house = self.get_object()
        hours = int(request.query_params.get('hours', 24))
        
        readings = house.readings.filter(
            reading_timestamp__gte=timezone.now() - timedelta(hours=hours)
        )[:50]
        
        serializer = ElectricityReadingSerializer(readings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """Get alerts for this house"""
        house = self.get_object()
        alerts = house.loss_alerts.all()[:20]
        serializer = LossAlertListSerializer(alerts, many=True)
        return Response(serializer.data)


class ElectricityReadingViewSet(viewsets.ModelViewSet):
    """API endpoint for electricity readings"""
    queryset = ElectricityReading.objects.all()
    serializer_class = ElectricityReadingSerializer
    permission_classes = [AllowAny]  # Allow public access for demo

    def get_queryset(self):
        queryset = ElectricityReading.objects.all()
        
        # Filter by various parameters
        house_id = self.request.query_params.get('house')
        transformer_id = self.request.query_params.get('transformer')
        status = self.request.query_params.get('status')
        anomalies_only = self.request.query_params.get('anomalies_only')
        
        if house_id:
            queryset = queryset.filter(house_id=house_id)
        if transformer_id:
            queryset = queryset.filter(transformer_id=transformer_id)
        if status:
            queryset = queryset.filter(status=status)
        if anomalies_only == 'true':
            queryset = queryset.filter(is_anomaly=True)
        
        return queryset[:100]  # Limit results


class LossAlertViewSet(viewsets.ModelViewSet):
    """API endpoint for loss alerts"""
    queryset = LossAlert.objects.all()
    serializer_class = LossAlertSerializer
    permission_classes = [AllowAny]  # Allow public access for demo

    def get_serializer_class(self):
        if self.action == 'list':
            return LossAlertListSerializer
        return LossAlertSerializer

    def get_queryset(self):
        queryset = LossAlert.objects.all()
        
        # Filter by various parameters
        status = self.request.query_params.get('status')
        severity = self.request.query_params.get('severity')
        alert_type = self.request.query_params.get('type')
        district_id = self.request.query_params.get('district')
        village_id = self.request.query_params.get('village')
        transformer_id = self.request.query_params.get('transformer')
        
        if status:
            queryset = queryset.filter(status=status)
        if severity:
            queryset = queryset.filter(severity=severity)
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        if village_id:
            queryset = queryset.filter(village_id=village_id)
        if transformer_id:
            queryset = queryset.filter(transformer_id=transformer_id)
        
        return queryset

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        alert.acknowledge(request.user)
        return Response({'status': 'acknowledged'})

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        notes = request.data.get('notes', '')
        alert.resolve(request.user, notes)
        return Response({'status': 'resolved'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get alert statistics"""
        district_id = request.query_params.get('district')
        
        queryset = LossAlert.objects.all()
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        
        stats = {
            'total': queryset.count(),
            'active': queryset.filter(status='active').count(),
            'acknowledged': queryset.filter(status='acknowledged').count(),
            'resolved': queryset.filter(status='resolved').count(),
            'by_severity': {
                'critical': queryset.filter(severity='critical', status='active').count(),
                'warning': queryset.filter(severity='warning', status='active').count(),
                'info': queryset.filter(severity='info', status='active').count(),
            },
            'by_type': {
                'theft_suspected': queryset.filter(alert_type='theft_suspected', status='active').count(),
                'power_loss': queryset.filter(alert_type='power_loss', status='active').count(),
                'voltage_drop': queryset.filter(alert_type='voltage_drop', status='active').count(),
                'equipment_fault': queryset.filter(alert_type='equipment_fault', status='active').count(),
            }
        }
        
        return Response(stats)


class SimulatorAPIView(APIView):
    """API endpoint to trigger simulator"""
    permission_classes = [AllowAny]  # Allow public access for demo

    def post(self, request):
        """Generate new readings for all or specific houses"""
        company_id = request.data.get('company_id')
        district_id = request.data.get('district_id')
        village_id = request.data.get('village_id')
        transformer_id = request.data.get('transformer_id')
        
        try:
            company = Company.objects.get(id=company_id) if company_id else None
            district = District.objects.get(id=district_id) if district_id else None
            village = Village.objects.get(id=village_id) if village_id else None
            transformer = Transformer.objects.get(id=transformer_id) if transformer_id else None
            
            readings = simulator.simulate_all_houses(
                company=company,
                district=district,
                village=village,
                transformer=transformer
            )
            
            # Count anomalies
            anomalies = sum(1 for r in readings if r.is_anomaly)
            
            return Response({
                'status': 'success',
                'readings_generated': len(readings),
                'anomalies_detected': anomalies,
                'alerts_created': anomalies,
            })
        
        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class DistributionDashboardView(APIView):
    """Main dashboard API for company admins"""
    permission_classes = [AllowAny]  # Allow public access for demo

    def get(self, request):
        """Get comprehensive dashboard data with full hierarchy"""
        company_id = request.query_params.get('company')
        
        # Get company or first available
        if company_id:
            company = Company.objects.filter(id=company_id).first()
        else:
            company = Company.objects.first()
        
        if not company:
            return Response({'error': 'No company found'}, status=404)
        
        # Calculate stats
        districts = list(company.districts.all())
        
        total_villages = 0
        total_transformers = 0
        total_houses = 0
        
        district_data = []
        for district in districts:
            villages = list(district.villages.all())
            v_count = len(villages)
            t_count = 0
            h_count = 0
            
            village_data = []
            for village in villages:
                transformers = list(village.transformers.all())
                t_count += len(transformers)
                v_h_count = 0
                
                transformer_data = []
                for transformer in transformers:
                    houses = list(transformer.houses.all())
                    t_h_count = len(houses)
                    h_count += t_h_count
                    v_h_count += t_h_count
                    
                    # Get transformer alerts
                    t_alerts = transformer.loss_alerts.filter(status='active').count()
                    
                    # Get house data for this transformer
                    house_data = []
                    for house in houses[:20]:  # Limit to 20 houses per transformer for performance
                        # Get latest reading
                        latest_reading = ElectricityReading.objects.filter(
                            transformer=transformer,
                            house=house
                        ).order_by('-reading_timestamp').first()
                        
                        house_data.append({
                            'id': str(house.id),
                            'consumer_id': house.consumer_id,
                            'consumer_name': house.consumer_name,
                            'connection_type': house.connection_type,
                            'connected_load_kw': float(house.connected_load_kw),
                            'latest_voltage': float(latest_reading.voltage_received) if latest_reading else None,
                            'latest_power': float(latest_reading.power_received_kw) if latest_reading else None,
                            'power_loss': float(latest_reading.power_loss_kw) if latest_reading else None,
                            'is_anomaly': latest_reading.is_anomaly if latest_reading else False,
                        })
                    
                    transformer_data.append({
                        'id': str(transformer.id),
                        'transformer_id': transformer.transformer_id,
                        'name': transformer.name or f"Transformer {transformer.transformer_id}",
                        'capacity_kva': float(transformer.capacity_kva),
                        'status': transformer.status,
                        'house_count': t_h_count,
                        'active_alerts': t_alerts,
                        'houses': house_data,
                    })
                
                # Get village alerts
                v_alerts = LossAlert.objects.filter(
                    transformer__village=village,
                    status='active'
                ).count()
                
                village_data.append({
                    'id': str(village.id),
                    'name': village.name,
                    'code': village.code,
                    'transformer_count': len(transformers),
                    'house_count': v_h_count,
                    'active_alerts': v_alerts,
                    'transformers': transformer_data,
                })
            
            total_villages += v_count
            total_transformers += t_count
            total_houses += h_count
            
            active_alerts = district.loss_alerts.filter(status='active').count()
            
            district_data.append({
                'id': str(district.id),
                'name': district.name,
                'code': district.code,
                'village_count': v_count,
                'transformer_count': t_count,
                'house_count': h_count,
                'active_alerts': active_alerts,
                'villages': village_data,
            })
        
        # Get recent readings aggregates
        recent_readings = ElectricityReading.objects.filter(
            transformer__village__district__company=company,
            reading_timestamp__gte=timezone.now() - timedelta(hours=24)
        )
        
        aggregates = recent_readings.aggregate(
            total_power_loss=Sum('power_loss_kw'),
            avg_loss_pct=Avg('power_loss_percentage'),
            anomaly_count=Count('id', filter=Q(is_anomaly=True))
        )
        
        # Get active alerts
        all_active_alerts = LossAlert.objects.filter(
            district__company=company,
            status='active'
        )
        
        total_active_alerts = all_active_alerts.count()
        critical_count = all_active_alerts.filter(severity='critical').count()
        
        # Get recent alerts for display (limited to 10)
        active_alerts = all_active_alerts.order_by('-created_at')[:10]
        
        alert_data = LossAlertListSerializer(active_alerts, many=True).data
        
        # Calculate financial loss
        total_loss = float(aggregates['total_power_loss'] or 0)
        rate_per_kwh = 7.50
        estimated_daily_loss = total_loss * 24 * rate_per_kwh
        
        return Response({
            'company': {
                'id': str(company.id),
                'name': company.name,
                'code': company.code,
            },
            'summary': {
                'total_districts': len(districts),
                'total_villages': total_villages,
                'total_transformers': total_transformers,
                'total_houses': total_houses,
                'active_alerts': total_active_alerts,
                'critical_alerts': critical_count,
                'total_power_loss_kw': round(total_loss, 3),
                'average_loss_percentage': round(float(aggregates['avg_loss_pct'] or 0), 2),
                'estimated_daily_loss_inr': round(estimated_daily_loss, 2),
                'houses_with_anomalies': aggregates['anomaly_count'] or 0,
            },
            'districts': district_data,
            'recent_alerts': alert_data,
        })
