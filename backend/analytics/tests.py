"""
Comprehensive tests for Analytics app
Tests for ML integration, forecasting, efficiency analysis, and analytics endpoints
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, timedelta
from decimal import Decimal
import json

from meters.models import Meter, MeterReading
from .models import EnergyForecast, ConsumptionPattern, EfficiencyScore, CarbonImpact
from .serializers import (
    EnergyForecastSerializer, ConsumptionPatternSerializer,
    EfficiencyScoreSerializer, CarbonFootprintSerializer
)
from .ml_service import MLModelService, get_ml_service

User = get_user_model()


class EnergyForecastModelTest(TestCase):
    """Test Energy Forecast model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123',
            role='farmer'
        )
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        self.forecast = EnergyForecast.objects.create(
            meter=self.meter,
            forecast_date=timezone.now().date() + timedelta(days=1),
            predicted_consumption=150.5,
            confidence_level=85.0,
            model_version='v1.0'
        )
    
    def test_forecast_creation(self):
        """Test forecast is created correctly"""
        self.assertEqual(self.forecast.meter, self.meter)
        self.assertEqual(self.forecast.predicted_consumption, 150.5)
        self.assertEqual(self.forecast.confidence_level, 85.0)
    
    def test_forecast_str_method(self):
        """Test forecast string representation"""
        self.assertIn(self.meter.meter_id, str(self.forecast))


class ConsumptionPatternModelTest(TestCase):
    """Test Consumption Pattern model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        self.pattern = ConsumptionPattern.objects.create(
            meter=self.meter,
            analysis_date=timezone.now().date(),
            peak_hour_start='18:00:00',
            peak_hour_end='22:00:00',
            off_peak_hour_start='00:00:00',
            off_peak_hour_end='06:00:00',
            average_daily_consumption=25.5,
            peak_consumption=35.0,
            off_peak_consumption=15.0
        )
    
    def test_pattern_creation(self):
        """Test pattern is created correctly"""
        self.assertEqual(self.pattern.meter, self.meter)
        self.assertEqual(self.pattern.average_daily_consumption, 25.5)
        self.assertTrue(self.pattern.peak_consumption > self.pattern.off_peak_consumption)
    
    def test_pattern_recommendations(self):
        """Test recommendations field"""
        recommendations = {
            'shift_load': 'Move heavy appliances to off-peak hours',
            'savings': 'Potential savings of ₹500/month'
        }
        self.pattern.recommendations = recommendations
        self.pattern.save()
        self.assertEqual(self.pattern.recommendations['shift_load'], recommendations['shift_load'])


class EfficiencyScoreModelTest(TestCase):
    """Test Efficiency Score model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        self.efficiency = EfficiencyScore.objects.create(
            meter=self.meter,
            score_date=timezone.now().date(),
            overall_score=85,
            power_factor_score=90,
            load_profile_score=80,
            peak_usage_score=85,
            consistency_score=90,
            grade='A'
        )
    
    def test_efficiency_creation(self):
        """Test efficiency score is created correctly"""
        self.assertEqual(self.efficiency.meter, self.meter)
        self.assertEqual(self.efficiency.overall_score, 85)
        self.assertEqual(self.efficiency.grade, 'A')
    
    def test_efficiency_scores(self):
        """Test individual efficiency scores"""
        self.assertTrue(0 <= self.efficiency.power_factor_score <= 100)
        self.assertTrue(0 <= self.efficiency.load_profile_score <= 100)
        self.assertTrue(0 <= self.efficiency.peak_usage_score <= 100)


class CarbonImpactModelTest(TestCase):
    """Test Carbon Impact model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        self.carbon = CarbonImpact.objects.create(
            meter=self.meter,
            calculation_date=timezone.now().date(),
            energy_consumed=100.0,
            carbon_emitted=70.0,
            trees_equivalent=2.5,
            carbon_saved=10.0
        )
    
    def test_carbon_creation(self):
        """Test carbon impact is created correctly"""
        self.assertEqual(self.carbon.meter, self.meter)
        self.assertEqual(self.carbon.energy_consumed, 100.0)
        self.assertEqual(self.carbon.carbon_emitted, 70.0)
    
    def test_carbon_calculations(self):
        """Test carbon emissions calculation"""
        # Typical grid carbon factor is 0.7 kg CO2/kWh
        expected_carbon = self.carbon.energy_consumed * 0.7
        self.assertEqual(self.carbon.carbon_emitted, expected_carbon)


class MLServiceTest(TestCase):
    """Test ML Model Service"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        # Create sample readings
        self.readings = []
        for i in range(100):
            reading = MeterReading.objects.create(
                meter=self.meter,
                timestamp=timezone.now() - timedelta(hours=i),
                voltage=230.0 + (i % 10),
                current=10.0 + (i % 5),
                power=2200.0 + (i * 10),
                energy=5.5 + i
            )
            self.readings.append(reading)
    
    def test_ml_service_singleton(self):
        """Test ML service singleton pattern"""
        service1 = get_ml_service()
        service2 = get_ml_service()
        self.assertEqual(id(service1), id(service2))
    
    def test_anomaly_detection(self):
        """Test anomaly detection"""
        service = get_ml_service()
        
        # Test with normal reading
        result = service.detect_anomaly(230.0, 10.0, 2200.0, 50.0)
        self.assertIsInstance(result, dict)
        self.assertIn('is_anomaly', result)
    
    def test_monthly_projection(self):
        """Test monthly consumption projection"""
        service = get_ml_service()
        
        recent_consumption = [25.5, 26.0, 24.5, 27.0, 25.0]
        result = service.project_monthly_usage(recent_consumption)
        
        self.assertIsInstance(result, dict)
        self.assertIn('projected_units', result)
        self.assertIn('estimated_cost', result)
    
    def test_efficiency_calculation(self):
        """Test efficiency score calculation"""
        service = get_ml_service()
        
        power_factors = [0.95, 0.92, 0.94, 0.93, 0.96]
        result = service.calculate_efficiency_score(power_factors, [], [])
        
        self.assertIsInstance(result, dict)
        self.assertIn('overall_score', result)
        self.assertTrue(0 <= result['overall_score'] <= 100)
    
    def test_hourly_prediction(self):
        """Test hourly consumption prediction"""
        service = get_ml_service()
        
        recent_readings = self.readings[:24]
        result = service.predict_next_hour(recent_readings)
        
        self.assertIsInstance(result, dict)
        self.assertIn('predicted_consumption', result)
    
    def test_weekly_forecast(self):
        """Test weekly consumption forecast"""
        service = get_ml_service()
        
        result = service.predict_weekly_consumption(self.readings)
        
        self.assertIsInstance(result, dict)
        self.assertIn('forecast', result)
        self.assertEqual(len(result['forecast']), 7)


class AnalyticsAPITest(APITestCase):
    """Test Analytics API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123',
            role='farmer'
        )
        self.client.force_authenticate(user=self.user)
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        # Create readings for testing
        for i in range(50):
            MeterReading.objects.create(
                meter=self.meter,
                timestamp=timezone.now() - timedelta(hours=i),
                voltage=230.0,
                current=10.0,
                power=2200.0,
                energy=5.5 + i
            )
    
    def test_consumption_trends(self):
        """Test GET /api/v1/analytics/consumption_trends/"""
        response = self.client.get(f'/api/v1/analytics/consumption_trends/?meter_id={self.meter.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
    
    def test_efficiency_analysis(self):
        """Test GET /api/v1/analytics/efficiency/"""
        response = self.client.get(f'/api/v1/analytics/efficiency/?meter_id={self.meter.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('efficiency_score', response.data)
    
    def test_cost_projection(self):
        """Test GET /api/v1/analytics/cost_projection/"""
        response = self.client.get(f'/api/v1/analytics/cost_projection/?meter_id={self.meter.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('projected_cost', response.data)
    
    def test_carbon_footprint(self):
        """Test GET /api/v1/analytics/carbon_footprint/"""
        response = self.client.get(f'/api/v1/analytics/carbon_footprint/?meter_id={self.meter.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('carbon_emitted', response.data)


class MLEndpointsTest(APITestCase):
    """Test ML-powered API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123',
            role='farmer'
        )
        self.client.force_authenticate(user=self.user)
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        # Create substantial reading history
        for i in range(100):
            MeterReading.objects.create(
                meter=self.meter,
                timestamp=timezone.now() - timedelta(hours=i),
                voltage=230.0 + (i % 10),
                current=10.0 + (i % 5),
                power=2200.0 + (i * 10),
                energy=5.5 + i
            )
    
    def test_ml_detect_anomaly(self):
        """Test POST /api/v1/analytics/ml/detect_anomaly/"""
        data = {
            'meter_id': self.meter.id,
            'voltage': 295.0,  # High voltage
            'current': 10.0,
            'power': 2500.0,
            'frequency': 50.0
        }
        response = self.client.post('/api/v1/analytics/ml/detect_anomaly/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_anomaly', response.data)
    
    def test_ml_predict_consumption(self):
        """Test POST /api/v1/analytics/ml/predict_consumption/"""
        data = {
            'meter_id': self.meter.id
        }
        response = self.client.post('/api/v1/analytics/ml/predict_consumption/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('projected_units', response.data)
        self.assertIn('estimated_cost', response.data)
    
    def test_ml_forecast_hourly(self):
        """Test POST /api/v1/analytics/ml/forecast_hourly/"""
        data = {
            'meter_id': self.meter.id
        }
        response = self.client.post('/api/v1/analytics/ml/forecast_hourly/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('predicted_consumption', response.data)
    
    def test_ml_weekly_forecast(self):
        """Test GET /api/v1/analytics/ml/weekly_forecast/"""
        response = self.client.get(f'/api/v1/analytics/ml/weekly_forecast/?meter_id={self.meter.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('forecast', response.data)
    
    def test_ml_pattern_analysis(self):
        """Test GET /api/v1/analytics/ml/pattern_analysis/"""
        response = self.client.get(f'/api/v1/analytics/ml/pattern_analysis/?meter_id={self.meter.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('peak_hours', response.data)
        self.assertIn('recommendations', response.data)


class ForecastingTest(TestCase):
    """Test forecasting functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        # Create historical readings
        for i in range(168):  # 1 week of hourly data
            MeterReading.objects.create(
                meter=self.meter,
                timestamp=timezone.now() - timedelta(hours=i),
                voltage=230.0,
                current=10.0,
                power=2200.0 + (i % 24) * 100,  # Daily pattern
                energy=2.2 + (i % 24) * 0.1
            )
    
    def test_forecast_generation(self):
        """Test generating consumption forecast"""
        service = get_ml_service()
        readings = MeterReading.objects.filter(meter=self.meter)[:100]
        
        forecast = service.predict_weekly_consumption(readings)
        
        self.assertIsInstance(forecast, dict)
        self.assertIn('forecast', forecast)
        self.assertEqual(len(forecast['forecast']), 7)


class SerializerTest(TestCase):
    """Test Analytics serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        self.forecast = EnergyForecast.objects.create(
            meter=self.meter,
            forecast_date=timezone.now().date() + timedelta(days=1),
            predicted_consumption=150.5,
            confidence_level=85.0
        )
        
        self.efficiency = EfficiencyScore.objects.create(
            meter=self.meter,
            score_date=timezone.now().date(),
            overall_score=85,
            grade='A'
        )
    
    def test_forecast_serializer(self):
        """Test EnergyForecastSerializer"""
        serializer = EnergyForecastSerializer(self.forecast)
        self.assertEqual(serializer.data['predicted_consumption'], 150.5)
        self.assertIn('meter_id', serializer.data)
    
    def test_efficiency_serializer(self):
        """Test EfficiencyScoreSerializer"""
        serializer = EfficiencyScoreSerializer(self.efficiency)
        self.assertEqual(serializer.data['overall_score'], 85)
        self.assertEqual(serializer.data['grade'], 'A')


class DataAggregationTest(TestCase):
    """Test data aggregation and analytics"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        # Create readings with varying patterns
        for day in range(7):
            for hour in range(24):
                power = 2000 + (hour * 100)  # Simulates daily pattern
                MeterReading.objects.create(
                    meter=self.meter,
                    timestamp=timezone.now() - timedelta(days=day, hours=hour),
                    voltage=230.0,
                    current=power / 230.0,
                    power=power,
                    energy=power / 1000.0
                )
    
    def test_daily_aggregation(self):
        """Test daily consumption aggregation"""
        from django.db.models import Sum, Avg
        
        daily_data = MeterReading.objects.filter(
            meter=self.meter,
            timestamp__date=timezone.now().date()
        ).aggregate(
            total_energy=Sum('energy'),
            avg_power=Avg('power')
        )
        
        self.assertIsNotNone(daily_data['total_energy'])
        self.assertIsNotNone(daily_data['avg_power'])
    
    def test_peak_identification(self):
        """Test peak hour identification"""
        from django.db.models import Max
        
        max_power = MeterReading.objects.filter(meter=self.meter).aggregate(
            max_power=Max('power')
        )
        
        self.assertIsNotNone(max_power['max_power'])
        self.assertTrue(max_power['max_power'] > 0)


# Run tests with: python manage.py test analytics
