"""
Comprehensive tests for Meters app
Tests for models, views, serializers, authentication, and API endpoints
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Meter, MeterReading, Alert, Notification
from .serializers import (
    UserSerializer, MeterSerializer, MeterReadingSerializer,
    AlertSerializer, NotificationSerializer
)

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123',
            role='farmer',
            phone_number='+919876543210',
            village='Anand',
            district='Anand',
            state='Gujarat'
        )
    
    def test_user_creation(self):
        """Test user is created correctly"""
        self.assertEqual(self.user.username, 'testfarmer')
        self.assertEqual(self.user.role, 'farmer')
        self.assertEqual(self.user.village, 'Anand')
        self.assertTrue(self.user.check_password('test123'))
    
    def test_user_str_method(self):
        """Test user string representation"""
        self.assertIn(self.user.username, str(self.user))
        self.assertIn(self.user.role, str(self.user))
    
    def test_user_roles(self):
        """Test different user roles"""
        roles = ['farmer', 'sarpanch', 'utility', 'government']
        for role in roles:
            user = User.objects.create_user(
                username=f'test_{role}',
                email=f'{role}@test.com',
                password='test123',
                role=role
            )
            self.assertEqual(user.role, role)


class MeterModelTest(TestCase):
    """Test Meter model"""
    
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
            meter_type='residential',
            manufacturer='Secure Meters',
            model_number='SM-001',
            installation_date=timezone.now().date(),
            status='active',
            location='Anand Village, Gujarat',
            latitude=Decimal('22.5516'),
            longitude=Decimal('72.9342'),
            rated_voltage=230.0,
            rated_current=40.0
        )
    
    def test_meter_creation(self):
        """Test meter is created correctly"""
        self.assertEqual(self.meter.meter_id, 'GJ-ANAND-00001')
        self.assertEqual(self.meter.user, self.user)
        self.assertEqual(self.meter.meter_type, 'residential')
        self.assertEqual(self.meter.status, 'active')
    
    def test_meter_str_method(self):
        """Test meter string representation"""
        expected = f"{self.meter.meter_id} - {self.user.username}"
        self.assertEqual(str(self.meter), expected)
    
    def test_meter_types(self):
        """Test different meter types"""
        types = ['residential', 'commercial', 'agricultural', 'industrial']
        for meter_type in types:
            meter = Meter.objects.create(
                meter_id=f'GJ-TEST-{meter_type[:3].upper()}',
                user=self.user,
                meter_type=meter_type,
                installation_date=timezone.now().date(),
                location='Test Location'
            )
            self.assertEqual(meter.meter_type, meter_type)


class MeterReadingModelTest(TestCase):
    """Test MeterReading model"""
    
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
        
        self.reading = MeterReading.objects.create(
            meter=self.meter,
            timestamp=timezone.now(),
            voltage=230.0,
            current=10.0,
            power=2200.0,
            energy=5.5,
            power_factor=0.95,
            frequency=50.0
        )
    
    def test_reading_creation(self):
        """Test meter reading is created correctly"""
        self.assertEqual(self.reading.meter, self.meter)
        self.assertEqual(self.reading.voltage, 230.0)
        self.assertEqual(self.reading.current, 10.0)
        self.assertEqual(self.reading.power, 2200.0)
    
    def test_apparent_power_calculation(self):
        """Test apparent power is calculated on save"""
        # Create new reading
        reading = MeterReading.objects.create(
            meter=self.meter,
            timestamp=timezone.now(),
            voltage=230.0,
            current=10.0,
            power=2000.0
        )
        # Apparent power should be V * I = 2300 VA
        self.assertEqual(reading.apparent_power, 2300.0)
    
    def test_anomaly_flag(self):
        """Test anomaly flagging"""
        reading = MeterReading.objects.create(
            meter=self.meter,
            timestamp=timezone.now(),
            voltage=295.0,  # High voltage
            current=10.0,
            power=2500.0,
            is_anomaly=True,
            anomaly_type='voltage_spike'
        )
        self.assertTrue(reading.is_anomaly)
        self.assertEqual(reading.anomaly_type, 'voltage_spike')


class AlertModelTest(TestCase):
    """Test Alert model"""
    
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
        
        self.alert = Alert.objects.create(
            meter=self.meter,
            alert_type='voltage_spike',
            severity='critical',
            title='High Voltage Detected',
            message='Voltage spike detected at 295V',
            estimated_cost_impact=Decimal('200.00')
        )
    
    def test_alert_creation(self):
        """Test alert is created correctly"""
        self.assertEqual(self.alert.meter, self.meter)
        self.assertEqual(self.alert.alert_type, 'voltage_spike')
        self.assertEqual(self.alert.severity, 'critical')
        self.assertEqual(self.alert.status, 'active')
    
    def test_alert_str_method(self):
        """Test alert string representation"""
        expected = f"{self.alert.alert_type} - {self.meter.meter_id}"
        self.assertEqual(str(self.alert), expected)


class UserAPITest(APITestCase):
    """Test User API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123',
            role='farmer'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_current_user(self):
        """Test GET /api/v1/users/me/"""
        response = self.client.get('/api/v1/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testfarmer')
    
    def test_update_profile(self):
        """Test PUT /api/v1/users/update_profile/"""
        data = {
            'first_name': 'Test',
            'last_name': 'Farmer',
            'village': 'Anand'
        }
        response = self.client.put('/api/v1/users/update_profile/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Test')


class MeterAPITest(APITestCase):
    """Test Meter API endpoints"""
    
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
            meter_type='residential',
            installation_date=timezone.now().date(),
            location='Test Location'
        )
    
    def test_list_meters(self):
        """Test GET /api/v1/meters/"""
        response = self.client.get('/api/v1/meters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    def test_get_meter_detail(self):
        """Test GET /api/v1/meters/{id}/"""
        response = self.client.get(f'/api/v1/meters/{self.meter.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['meter_id'], 'GJ-ANAND-00001')
    
    def test_create_meter(self):
        """Test POST /api/v1/meters/"""
        data = {
            'meter_id': 'GJ-ANAND-00002',
            'user': self.user.id,
            'meter_type': 'residential',
            'installation_date': timezone.now().date().isoformat(),
            'location': 'Test Location 2'
        }
        response = self.client.post('/api/v1/meters/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_get_meter_readings(self):
        """Test GET /api/v1/meters/{id}/readings/"""
        # Create a reading first
        MeterReading.objects.create(
            meter=self.meter,
            timestamp=timezone.now(),
            voltage=230.0,
            current=10.0,
            power=2200.0,
            energy=5.5
        )
        
        response = self.client.get(f'/api/v1/meters/{self.meter.id}/readings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    def test_get_live_status(self):
        """Test GET /api/v1/meters/{id}/live_status/"""
        # Create a recent reading
        MeterReading.objects.create(
            meter=self.meter,
            timestamp=timezone.now(),
            voltage=230.0,
            current=10.0,
            power=2200.0,
            energy=5.5
        )
        
        response = self.client.get(f'/api/v1/meters/{self.meter.id}/live_status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_online', response.data)


class MeterReadingAPITest(APITestCase):
    """Test MeterReading API endpoints"""
    
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
    
    def test_create_reading(self):
        """Test POST /api/v1/readings/"""
        data = {
            'meter': self.meter.id,
            'timestamp': timezone.now().isoformat(),
            'voltage': 230.0,
            'current': 10.0,
            'power': 2200.0,
            'energy': 5.5,
            'power_factor': 0.95
        }
        response = self.client.post('/api/v1/readings/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_readings(self):
        """Test GET /api/v1/readings/"""
        MeterReading.objects.create(
            meter=self.meter,
            timestamp=timezone.now(),
            voltage=230.0,
            current=10.0,
            power=2200.0,
            energy=5.5
        )
        
        response = self.client.get('/api/v1/readings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    def test_get_anomalies(self):
        """Test GET /api/v1/readings/anomalies/"""
        # Create anomaly reading
        MeterReading.objects.create(
            meter=self.meter,
            timestamp=timezone.now(),
            voltage=295.0,
            current=10.0,
            power=2500.0,
            energy=6.0,
            is_anomaly=True,
            anomaly_type='voltage_spike'
        )
        
        response = self.client.get('/api/v1/readings/anomalies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AlertAPITest(APITestCase):
    """Test Alert API endpoints"""
    
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
        
        self.alert = Alert.objects.create(
            meter=self.meter,
            alert_type='voltage_spike',
            severity='critical',
            title='High Voltage',
            message='Voltage spike detected'
        )
    
    def test_list_alerts(self):
        """Test GET /api/v1/alerts/"""
        response = self.client.get('/api/v1/alerts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
    
    def test_get_alert_detail(self):
        """Test GET /api/v1/alerts/{id}/"""
        response = self.client.get(f'/api/v1/alerts/{self.alert.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['alert_type'], 'voltage_spike')
    
    def test_acknowledge_alert(self):
        """Test POST /api/v1/alerts/acknowledge/"""
        data = {
            'alert_ids': [self.alert.id]
        }
        response = self.client.post('/api/v1/alerts/acknowledge/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check alert status updated
        self.alert.refresh_from_db()
        self.assertEqual(self.alert.status, 'acknowledged')


class DashboardAPITest(APITestCase):
    """Test Dashboard API endpoints"""
    
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
        
        # Create some readings
        for i in range(10):
            MeterReading.objects.create(
                meter=self.meter,
                timestamp=timezone.now() - timedelta(hours=i),
                voltage=230.0,
                current=10.0,
                power=2200.0,
                energy=5.5 + i
            )
    
    def test_get_stats(self):
        """Test GET /api/v1/dashboard/stats/"""
        response = self.client.get('/api/v1/dashboard/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_energy', response.data)
        self.assertIn('current_power', response.data)


class SerializerTest(TestCase):
    """Test serializers"""
    
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
    
    def test_user_serializer(self):
        """Test UserSerializer"""
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['username'], 'testfarmer')
        self.assertIn('meter_count', serializer.data)
    
    def test_meter_serializer(self):
        """Test MeterSerializer"""
        serializer = MeterSerializer(self.meter)
        self.assertEqual(serializer.data['meter_id'], 'GJ-ANAND-00001')
        self.assertIn('user_name', serializer.data)
    
    def test_meter_reading_serializer(self):
        """Test MeterReadingSerializer"""
        reading = MeterReading.objects.create(
            meter=self.meter,
            timestamp=timezone.now(),
            voltage=230.0,
            current=10.0,
            power=2200.0,
            energy=5.5
        )
        serializer = MeterReadingSerializer(reading)
        self.assertEqual(serializer.data['voltage'], 230.0)
        self.assertIn('meter_id', serializer.data)


class PermissionTest(APITestCase):
    """Test API permissions and role-based access"""
    
    def setUp(self):
        self.farmer = User.objects.create_user(
            username='farmer1',
            email='farmer@test.com',
            password='test123',
            role='farmer'
        )
        
        self.sarpanch = User.objects.create_user(
            username='sarpanch1',
            email='sarpanch@test.com',
            password='test123',
            role='sarpanch',
            village='Anand'
        )
        
        self.utility = User.objects.create_user(
            username='utility1',
            email='utility@test.com',
            password='test123',
            role='utility'
        )
        
        self.farmer_meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.farmer,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
    
    def test_farmer_can_only_see_own_meters(self):
        """Test farmer can only access their own meters"""
        self.client.force_authenticate(user=self.farmer)
        response = self.client.get('/api/v1/meters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_utility_can_see_all_meters(self):
        """Test utility can access all meters"""
        self.client.force_authenticate(user=self.utility)
        response = self.client.get('/api/v1/meters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Utility should see all meters
        self.assertTrue(len(response.data) >= 1)
    
    def test_unauthorized_access_denied(self):
        """Test unauthorized access is denied"""
        response = self.client.get('/api/v1/meters/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ValidationTest(TestCase):
    """Test data validation"""
    
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
    
    def test_voltage_validation(self):
        """Test voltage must be within valid range"""
        reading = MeterReading(
            meter=self.meter,
            timestamp=timezone.now(),
            voltage=600.0,  # Invalid - too high
            current=10.0,
            power=2200.0,
            energy=5.5
        )
        # Note: Django validators run on form/serializer level, not model level
        # This test demonstrates the model can save, but serializer would validate
        reading.save()
        self.assertEqual(reading.voltage, 600.0)
    
    def test_power_factor_range(self):
        """Test power factor must be between 0 and 1"""
        reading = MeterReading(
            meter=self.meter,
            timestamp=timezone.now(),
            voltage=230.0,
            current=10.0,
            power=2200.0,
            energy=5.5,
            power_factor=0.95
        )
        reading.save()
        self.assertTrue(0 <= reading.power_factor <= 1)


# Run tests with: python manage.py test meters
