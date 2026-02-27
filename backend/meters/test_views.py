"""
Test endpoints for SMS and Alert functionality
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .sms_service import send_sms
from .alert_service import AlertService
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def test_sms(request):
    """
    Test SMS sending functionality
    
    POST /api/v1/test/sms/
    Body: {
        "phone_number": "+919876543210",
        "message": "Test message"
    }
    """
    phone_number = request.data.get('phone_number')
    message = request.data.get('message', 'Test SMS from Gram Meter!')
    
    if not phone_number:
        return Response({
            'success': False,
            'error': 'phone_number is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        result = send_sms(phone_number, message)
        
        return Response({
            'success': result['success'],
            'message': result['message'],
            'provider': result.get('provider'),
            'phone_number': phone_number
        }, status=status.HTTP_200_OK if result['success'] else status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Test SMS error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def test_alert(request):
    """
    Test alert sending functionality
    
    POST /api/v1/test/alert/
    Body: {
        "phone_number": "+919876543210",
        "alert_type": "high_usage",
        "meter_reading": 150.5
    }
    """
    phone_number = request.data.get('phone_number')
    alert_type = request.data.get('alert_type', 'high_usage')
    meter_reading = float(request.data.get('meter_reading', 100.0))
    
    if not phone_number:
        return Response({
            'success': False,
            'error': 'phone_number is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        success = AlertService.send_meter_alert(
            user_phone=phone_number,
            meter_reading=meter_reading,
            alert_type=alert_type,
            threshold=200.0,
            daily_limit=150.0
        )
        
        return Response({
            'success': success,
            'message': f'Alert {"sent" if success else "failed"}',
            'alert_type': alert_type,
            'phone_number': phone_number
        }, status=status.HTTP_200_OK if success else status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Test alert error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def sms_config_status(request):
    """
    Check SMS configuration status
    
    GET /api/v1/test/sms-status/
    """
    from django.conf import settings
    
    provider = getattr(settings, 'SMS_PROVIDER', 'Not configured')
    
    config_status = {
        'provider': provider,
        'configured': False,
        'details': {}
    }
    
    if provider == 'FAST2SMS':
        has_key = bool(getattr(settings, 'FAST2SMS_API_KEY', ''))
        sender_id = getattr(settings, 'FAST2SMS_SENDER_ID', 'TXTIND')
        config_status['configured'] = has_key
        config_status['details'] = {
            'api_key': 'Configured' if has_key else 'Missing',
            'sender_id': sender_id,
            'recommendation': 'Add FAST2SMS_API_KEY to .env file' if not has_key else 'Ready to send SMS'
        }
    elif provider == 'AWS_SNS':
        has_access_key = bool(getattr(settings, 'AWS_ACCESS_KEY_ID', ''))
        has_secret_key = bool(getattr(settings, 'AWS_SECRET_ACCESS_KEY', ''))
        config_status['configured'] = all([has_access_key, has_secret_key])
        config_status['details'] = {
            'aws_access_key_id': 'Configured' if has_access_key else 'Missing',
            'aws_secret_access_key': 'Configured' if has_secret_key else 'Missing',
            'region': getattr(settings, 'AWS_REGION', 'ap-south-1')
        }
    else:
        config_status['details'] = {
            'message': f'Unsupported provider: {provider}',
            'supported_providers': ['FAST2SMS', 'AWS_SNS']
        }
    
    return Response(config_status, status=status.HTTP_200_OK)
