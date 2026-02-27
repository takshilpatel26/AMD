"""
Notification Views - API endpoints for notifications
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .services import alert_notification_service
from meters.models import Alert
import logging

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter notifications by user"""
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def send_test_whatsapp(self, request):
        """
        Send test WhatsApp message
        POST /api/v1/notifications/send_test_whatsapp/
        """
        phone = request.data.get('phone')
        message = request.data.get('message', 'Test message from Gram Meter! 🌾')
        
        if not phone:
            return Response(
                {'error': 'Phone number required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .services import twilio_service
        result = twilio_service.send_whatsapp(phone, message)
        
        if result.get('success'):
            return Response({
                'status': 'success',
                'message': 'WhatsApp sent successfully',
                'message_sid': result.get('message_sid')
            })
        else:
            return Response(
                {'error': result.get('error')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def send_test_sms(self, request):
        """
        Send test SMS
        POST /api/v1/notifications/send_test_sms/
        """
        phone = request.data.get('phone')
        message = request.data.get('message', 'Test SMS from Gram Meter!')
        
        if not phone:
            return Response(
                {'error': 'Phone number required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from .services import twilio_service
        result = twilio_service.send_sms(phone, message)
        
        if result.get('success'):
            return Response({
                'status': 'success',
                'message': 'SMS sent successfully',
                'message_sid': result.get('message_sid')
            })
        else:
            return Response(
                {'error': result.get('error')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def send_alert_notification(self, request):
        """
        Send alert notification to user
        POST /api/v1/notifications/send_alert_notification/
        Body: {"alert_id": 1, "channel": "whatsapp"}
        """
        alert_id = request.data.get('alert_id')
        channel = request.data.get('channel', 'whatsapp')
        
        if not alert_id:
            return Response(
                {'error': 'alert_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            alert = Alert.objects.get(id=alert_id)
        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        result = alert_notification_service.send_alert(
            alert=alert,
            user=request.user,
            channel=channel
        )
        
        if result.get('success'):
            return Response({
                'status': 'success',
                'message': f'{channel.title()} notification sent',
                'message_sid': result.get('message_sid')
            })
        else:
            return Response(
                {'error': result.get('error')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get count of unread notifications
        GET /api/v1/notifications/unread_count/
        """
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark notification as read
        POST /api/v1/notifications/{id}/mark_read/
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all notifications as read
        POST /api/v1/notifications/mark_all_read/
        """
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all notifications marked as read'})
