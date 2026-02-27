from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class User(AbstractUser):
    """Extended User model for Gram Meter platform"""
    
    USER_ROLES = (
        ('farmer', 'Farmer/End User'),
        ('sarpanch', 'Sarpanch/Village Admin'),
        ('utility', 'Utility Company'),
        ('government', 'Government Official'),
    )
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='farmer')
    phone_number = models.CharField(max_length=15, blank=True)
    whatsapp_number = models.CharField(max_length=15, blank=True)
    village = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, default='Gujarat')
    preferred_language = models.CharField(
        max_length=10,
        choices=(('en', 'English'), ('hi', 'Hindi'), ('gu', 'Gujarati')),
        default='en'
    )
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['role', 'state']),
            models.Index(fields=['village']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class Meter(models.Model):
    """Smart Meter model representing physical energy meters"""
    
    METER_TYPES = (
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('agricultural', 'Agricultural'),
        ('industrial', 'Industrial'),
    )
    
    METER_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('faulty', 'Faulty'),
    )
    
    meter_id = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meters')
    meter_type = models.CharField(max_length=20, choices=METER_TYPES, default='residential')
    manufacturer = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    installation_date = models.DateField()
    status = models.CharField(max_length=20, choices=METER_STATUS, default='active')
    location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    rated_voltage = models.FloatField(default=230.0)  # In volts
    rated_current = models.FloatField(default=40.0)  # In amperes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meters'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['meter_type']),
            models.Index(fields=['installation_date']),
        ]
    
    def __str__(self):
        return f"{self.meter_id} - {self.user.username}"


class MeterReading(models.Model):
    """Real-time and historical meter readings"""
    
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    voltage = models.FloatField(validators=[MinValueValidator(0)])  # Volts
    current = models.FloatField(validators=[MinValueValidator(0)])  # Amperes
    power = models.FloatField(validators=[MinValueValidator(0)])  # Watts
    energy = models.FloatField(validators=[MinValueValidator(0)])  # kWh
    power_factor = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        default=0.95
    )
    frequency = models.FloatField(default=50.0)  # Hz
    temperature = models.FloatField(null=True, blank=True)  # Celsius
    
    # Calculated fields
    apparent_power = models.FloatField(null=True, blank=True)  # VA
    reactive_power = models.FloatField(null=True, blank=True)  # VAR
    
    # Data quality
    is_anomaly = models.BooleanField(default=False)
    anomaly_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'meter_readings'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['meter', '-timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_anomaly']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-calculate apparent and reactive power
        if self.voltage and self.current:
            self.apparent_power = self.voltage * self.current
            if self.power and self.apparent_power:
                self.reactive_power = (self.apparent_power ** 2 - self.power ** 2) ** 0.5
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.meter.meter_id} - {self.timestamp}"


class Alert(models.Model):
    """System-generated alerts for anomalies and critical events"""
    
    ALERT_TYPES = (
        ('voltage_spike', 'Voltage Spike'),
        ('voltage_drop', 'Voltage Drop'),
        ('overcurrent', 'Overcurrent'),
        ('phantom_load', 'Phantom Load'),
        ('power_outage', 'Power Outage'),
        ('meter_offline', 'Meter Offline'),
        ('high_consumption', 'High Consumption'),
        ('billing_alert', 'Billing Alert'),
    )
    
    SEVERITY_LEVELS = (
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('emergency', 'Emergency'),
    )
    
    ALERT_STATUS = (
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
    )
    
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name='alerts')
    reading = models.ForeignKey(MeterReading, on_delete=models.SET_NULL, null=True, blank=True)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    severity = models.CharField(max_length=15, choices=SEVERITY_LEVELS, default='warning')
    status = models.CharField(max_length=20, choices=ALERT_STATUS, default='active')
    title = models.CharField(max_length=200)
    message = models.TextField()
    message_hindi = models.TextField(blank=True)
    message_gujarati = models.TextField(blank=True)
    recommended_action = models.TextField(blank=True)
    estimated_cost_impact = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['meter', '-created_at']),
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['alert_type']),
        ]
    
    def __str__(self):
        return f"{self.alert_type} - {self.meter.meter_id}"


class Notification(models.Model):
    """User notifications via WhatsApp, SMS, Email, or Push"""
    
    NOTIFICATION_CHANNELS = (
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
    )
    
    NOTIFICATION_STATUS = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    channel = models.CharField(max_length=15, choices=NOTIFICATION_CHANNELS)
    status = models.CharField(max_length=15, choices=NOTIFICATION_STATUS, default='pending')
    recipient = models.CharField(max_length=100)  # Phone number or email
    message = models.TextField()
    external_id = models.CharField(max_length=100, blank=True)  # Twilio SID, etc.
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['channel']),
        ]
    
    def __str__(self):
        return f"{self.channel} to {self.user.username} - {self.status}"

