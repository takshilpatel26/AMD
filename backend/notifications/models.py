from django.db import models
from django.conf import settings
import uuid

class Notification(models.Model):
    """
    Notification model for storing alert notifications sent to users
    """
    NOTIFICATION_TYPES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    ]
    
    ALERT_TYPES = [
        ('voltage_spike', 'Voltage Spike'),
        ('voltage_drop', 'Voltage Drop'),
        ('overcurrent', 'Overcurrent'),
        ('phantom_load', 'Phantom Load'),
        ('power_outage', 'Power Outage'),
        ('high_consumption', 'High Consumption'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES, null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Twilio specific fields
    twilio_sid = models.CharField(max_length=100, null=True, blank=True)
    recipient = models.CharField(max_length=100)  # Phone number or email
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} to {self.user.username} - {self.status}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        self.status = 'read'
        self.read_at = timezone.now()
        self.save(update_fields=['status', 'read_at'])
