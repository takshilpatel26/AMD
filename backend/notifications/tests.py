"""
Comprehensive tests for Notifications app
Tests for notification models, services, WhatsApp, SMS, and alert notifications
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from meters.models import Meter, Alert
from .models import Notification
from .services import TwilioService, AlertNotificationService, twilio_service, alert_notification_service

User = get_user_model()


class NotificationModelTest(TestCase):
    """Test Notification model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123',
            phone_number='+919876543210'
        )
        
        self.notification = Notification.objects.create(
            user=self.user,
            notification_type='whatsapp',
            alert_type='voltage_spike',
            title='High Voltage Alert',
            message='Voltage spike detected at your meter',
            recipient='+919876543210',
            status='pending'
        )
    
    def test_notification_creation(self):
        """Test notification is created correctly"""
        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.notification_type, 'whatsapp')
        self.assertEqual(self.notification.status, 'pending')
    
    def test_notification_str_method(self):
        """Test notification string representation"""
        expected = f"{self.notification.notification_type} to {self.user.username} - {self.notification.status}"
        self.assertEqual(str(self.notification), expected)
    
    def test_mark_as_read(self):
        """Test mark_as_read method"""
        self.notification.mark_as_read()
        self.assertEqual(self.notification.status, 'read')
        self.assertIsNotNone(self.notification.read_at)
    
    def test_notification_types(self):
        """Test different notification types"""
        types = ['whatsapp', 'sms', 'email', 'push']
        for notif_type in types:
            notification = Notification.objects.create(
                user=self.user,
                notification_type=notif_type,
                title='Test Notification',
                message='Test message',
                recipient='+919876543210'
            )
            self.assertEqual(notification.notification_type, notif_type)
    
    def test_alert_types(self):
        """Test different alert types"""
        alert_types = ['voltage_spike', 'voltage_drop', 'overcurrent', 
                      'phantom_load', 'power_outage', 'high_consumption']
        for alert_type in alert_types:
            notification = Notification.objects.create(
                user=self.user,
                notification_type='whatsapp',
                alert_type=alert_type,
                title=f'{alert_type} Alert',
                message=f'{alert_type} detected',
                recipient='+919876543210'
            )
            self.assertEqual(notification.alert_type, alert_type)


class TwilioServiceTest(TestCase):
    """Test Twilio Service"""
    
    def setUp(self):
        self.service = TwilioService()
        self.test_phone = '+919876543210'
        self.test_message = 'Test message from Gram Meter'
    
    @patch('notifications.services.twilio_client.messages.create')
    def test_send_whatsapp_success(self, mock_create):
        """Test successful WhatsApp message sending"""
        mock_message = MagicMock()
        mock_message.sid = 'SM123456789'
        mock_message.status = 'queued'
        mock_create.return_value = mock_message
        
        result = self.service.send_whatsapp(self.test_phone, self.test_message)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['message_sid'], 'SM123456789')
        self.assertEqual(result['status'], 'queued')
    
    @patch('notifications.services.twilio_client.messages.create')
    def test_send_whatsapp_failure(self, mock_create):
        """Test WhatsApp sending failure"""
        mock_create.side_effect = Exception('Twilio API Error')
        
        result = self.service.send_whatsapp(self.test_phone, self.test_message)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('notifications.services.twilio_client.messages.create')
    def test_send_sms_success(self, mock_create):
        """Test successful SMS sending"""
        mock_message = MagicMock()
        mock_message.sid = 'SM987654321'
        mock_message.status = 'sent'
        mock_create.return_value = mock_message
        
        result = self.service.send_sms(self.test_phone, self.test_message)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['message_sid'], 'SM987654321')
    
    @patch('notifications.services.twilio_client.messages.create')
    def test_send_sms_failure(self, mock_create):
        """Test SMS sending failure"""
        mock_create.side_effect = Exception('SMS sending failed')
        
        result = self.service.send_sms(self.test_phone, self.test_message)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_format_phone_number(self):
        """Test phone number formatting"""
        # Test Indian number without country code
        result = self.service.format_phone_number('9876543210')
        self.assertEqual(result, '+919876543210')
        
        # Test number already with country code
        result = self.service.format_phone_number('+919876543210')
        self.assertEqual(result, '+919876543210')


class AlertNotificationServiceTest(TestCase):
    """Test Alert Notification Service"""
    
    def setUp(self):
        self.service = AlertNotificationService()
        
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123',
            phone_number='+919876543210',
            whatsapp_number='+919876543210',
            preferred_language='en'
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
            message_hindi='उच्च वोल्टेज का पता चला',
            message_gujarati='ઉચ્ચ વોલ્ટેજ મળ્યું'
        )
    
    @patch('notifications.services.twilio_service.send_whatsapp')
    def test_send_alert_whatsapp(self, mock_send_whatsapp):
        """Test sending alert via WhatsApp"""
        mock_send_whatsapp.return_value = {
            'success': True,
            'message_sid': 'SM123456'
        }
        
        result = self.service.send_alert_notification(self.alert, channel='whatsapp')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 'whatsapp')
        
        # Verify notification was created
        notification = Notification.objects.filter(
            user=self.user,
            alert_type='voltage_spike'
        ).first()
        self.assertIsNotNone(notification)
    
    @patch('notifications.services.twilio_service.send_sms')
    def test_send_alert_sms(self, mock_send_sms):
        """Test sending alert via SMS"""
        mock_send_sms.return_value = {
            'success': True,
            'message_sid': 'SM789012'
        }
        
        result = self.service.send_alert_notification(self.alert, channel='sms')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['channel'], 'sms')
    
    def test_localized_message(self):
        """Test localized message based on user language"""
        # Test Hindi
        self.user.preferred_language = 'hi'
        self.user.save()
        
        message = self.service.get_localized_message(self.alert, self.user)
        self.assertEqual(message, self.alert.message_hindi)
        
        # Test Gujarati
        self.user.preferred_language = 'gu'
        self.user.save()
        
        message = self.service.get_localized_message(self.alert, self.user)
        self.assertEqual(message, self.alert.message_gujarati)
        
        # Test English (default)
        self.user.preferred_language = 'en'
        self.user.save()
        
        message = self.service.get_localized_message(self.alert, self.user)
        self.assertEqual(message, self.alert.message)
    
    @patch('notifications.services.twilio_service.send_whatsapp')
    def test_bulk_alert_notification(self, mock_send_whatsapp):
        """Test sending alert to multiple users"""
        mock_send_whatsapp.return_value = {'success': True}
        
        # Create additional users
        user2 = User.objects.create_user(
            username='testfarmer2',
            email='farmer2@test.com',
            password='test123',
            phone_number='+919876543211',
            whatsapp_number='+919876543211'
        )
        
        users = [self.user, user2]
        results = []
        
        for user in users:
            result = self.service.send_alert_notification(self.alert, channel='whatsapp')
            results.append(result)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r['success'] for r in results))


class NotificationAPITest(APITestCase):
    """Test Notification API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123',
            phone_number='+919876543210'
        )
        self.client.force_authenticate(user=self.user)
        
        self.notification = Notification.objects.create(
            user=self.user,
            notification_type='whatsapp',
            title='Test Notification',
            message='Test message',
            recipient='+919876543210',
            status='sent'
        )
    
    def test_list_notifications(self):
        """Test GET /api/v1/notifications/"""
        response = self.client.get('/api/v1/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @patch('notifications.services.twilio_service.send_whatsapp')
    def test_send_test_whatsapp(self, mock_send_whatsapp):
        """Test POST /api/v1/notifications/send_test_whatsapp/"""
        mock_send_whatsapp.return_value = {
            'success': True,
            'message_sid': 'SM123456'
        }
        
        data = {
            'phone': '+919876543210',
            'message': 'Test WhatsApp message'
        }
        response = self.client.post('/api/v1/notifications/send_test_whatsapp/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
    
    @patch('notifications.services.twilio_service.send_sms')
    def test_send_test_sms(self, mock_send_sms):
        """Test POST /api/v1/notifications/send_test_sms/"""
        mock_send_sms.return_value = {
            'success': True,
            'message_sid': 'SM789012'
        }
        
        data = {
            'phone': '+919876543210',
            'message': 'Test SMS message'
        }
        response = self.client.post('/api/v1/notifications/send_test_sms/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')


class NotificationStatusTest(TestCase):
    """Test notification status transitions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.notification = Notification.objects.create(
            user=self.user,
            notification_type='whatsapp',
            title='Test',
            message='Test message',
            recipient='+919876543210',
            status='pending'
        )
    
    def test_status_transitions(self):
        """Test notification status flow"""
        # Pending -> Sent
        self.notification.status = 'sent'
        self.notification.sent_at = timezone.now()
        self.notification.save()
        self.assertEqual(self.notification.status, 'sent')
        
        # Sent -> Delivered
        self.notification.status = 'delivered'
        self.notification.delivered_at = timezone.now()
        self.notification.save()
        self.assertEqual(self.notification.status, 'delivered')
        
        # Delivered -> Read
        self.notification.mark_as_read()
        self.assertEqual(self.notification.status, 'read')
        self.assertIsNotNone(self.notification.read_at)
    
    def test_failed_notification(self):
        """Test failed notification handling"""
        self.notification.status = 'failed'
        self.notification.error_message = 'Twilio API Error'
        self.notification.save()
        
        self.assertEqual(self.notification.status, 'failed')
        self.assertIsNotNone(self.notification.error_message)


class NotificationFilteringTest(TestCase):
    """Test notification filtering and querying"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        # Create notifications with different types and statuses
        for i in range(5):
            Notification.objects.create(
                user=self.user,
                notification_type='whatsapp',
                title=f'Notification {i}',
                message=f'Message {i}',
                recipient='+919876543210',
                status='sent' if i % 2 == 0 else 'delivered'
            )
    
    def test_filter_by_type(self):
        """Test filtering notifications by type"""
        whatsapp_notifications = Notification.objects.filter(
            user=self.user,
            notification_type='whatsapp'
        )
        self.assertEqual(whatsapp_notifications.count(), 5)
    
    def test_filter_by_status(self):
        """Test filtering notifications by status"""
        sent_notifications = Notification.objects.filter(
            user=self.user,
            status='sent'
        )
        self.assertEqual(sent_notifications.count(), 3)
        
        delivered_notifications = Notification.objects.filter(
            user=self.user,
            status='delivered'
        )
        self.assertEqual(delivered_notifications.count(), 2)
    
    def test_recent_notifications(self):
        """Test getting recent notifications"""
        recent = Notification.objects.filter(
            user=self.user,
            created_at__gte=timezone.now() - timedelta(days=1)
        ).order_by('-created_at')
        
        self.assertEqual(recent.count(), 5)


class NotificationMetadataTest(TestCase):
    """Test notification metadata handling"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
    
    def test_metadata_storage(self):
        """Test storing metadata in notification"""
        metadata = {
            'alert_id': 123,
            'meter_id': 'GJ-ANAND-00001',
            'severity': 'critical',
            'voltage': 295.0
        }
        
        notification = Notification.objects.create(
            user=self.user,
            notification_type='whatsapp',
            title='High Voltage',
            message='Alert message',
            recipient='+919876543210',
            metadata=metadata
        )
        
        self.assertEqual(notification.metadata['alert_id'], 123)
        self.assertEqual(notification.metadata['severity'], 'critical')
    
    def test_twilio_sid_storage(self):
        """Test storing Twilio SID"""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='whatsapp',
            title='Test',
            message='Test message',
            recipient='+919876543210',
            twilio_sid='SM123456789abcdef'
        )
        
        self.assertEqual(notification.twilio_sid, 'SM123456789abcdef')


# Run tests with: python manage.py test notifications
