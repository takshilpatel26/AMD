"""
Distribution Network Models

Hierarchy:
- Company (e.g., Torrent Power)
  └── District
      └── Village
          └── Transformer (4-6 per village, each powers ~10 houses)
              └── House
                  └── ElectricityReading (sent vs received voltage)
                      └── LossAlert (when loss detected)
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class Company(models.Model):
    """Electricity distribution company (e.g., Torrent Power)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)  # e.g., "TORRENT"
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    logo_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    """District under a company's service area"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)  # e.g., "ANAND"
    state = models.CharField(max_length=100, default="Gujarat")
    total_capacity_kva = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['company', 'code']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company.code})"

    @property
    def village_count(self):
        return self.villages.count()

    @property
    def transformer_count(self):
        return sum(v.transformers.count() for v in self.villages.all())


class Village(models.Model):
    """Village within a district"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='villages')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)  # e.g., "VLG001"
    pincode = models.CharField(max_length=10, blank=True)
    population = models.PositiveIntegerField(default=0)
    total_households = models.PositiveIntegerField(default=0)
    gps_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['district', 'code']
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.district.name}"

    @property
    def transformer_count(self):
        return self.transformers.count()

    @property
    def house_count(self):
        return sum(t.houses.count() for t in self.transformers.all())


class Transformer(models.Model):
    """Distribution transformer - powers ~10 houses"""
    
    class TransformerType(models.TextChoices):
        DISTRIBUTION = 'distribution', 'Distribution Transformer'
        POLE_MOUNTED = 'pole_mounted', 'Pole Mounted'
        PAD_MOUNTED = 'pad_mounted', 'Pad Mounted'
        SUBSTATION = 'substation', 'Substation Transformer'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        MAINTENANCE = 'maintenance', 'Under Maintenance'
        FAULTY = 'faulty', 'Faulty'
        OFFLINE = 'offline', 'Offline'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name='transformers')
    transformer_id = models.CharField(max_length=50, unique=True)  # e.g., "TRF-ANAND-VLG001-01"
    name = models.CharField(max_length=200)
    transformer_type = models.CharField(
        max_length=20, 
        choices=TransformerType.choices, 
        default=TransformerType.DISTRIBUTION
    )
    capacity_kva = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 25, 63, 100 KVA
    input_voltage = models.DecimalField(max_digits=10, decimal_places=2, default=11000)  # 11KV input
    output_voltage = models.DecimalField(max_digits=10, decimal_places=2, default=230)  # 230V output
    efficiency_rating = models.DecimalField(max_digits=5, decimal_places=2, default=98.5)  # percentage
    max_houses = models.PositiveIntegerField(default=10)
    installation_date = models.DateField(null=True, blank=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    gps_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['transformer_id']

    def __str__(self):
        return f"{self.transformer_id} - {self.name}"

    @property
    def house_count(self):
        return self.houses.count()

    @property
    def current_load_percentage(self):
        """Calculate current load as percentage of capacity"""
        total_load = sum(h.connected_load_kw for h in self.houses.filter(is_active=True))
        if self.capacity_kva > 0:
            return (total_load / float(self.capacity_kva)) * 100
        return 0


class House(models.Model):
    """Individual house connected to a transformer"""
    
    class ConnectionType(models.TextChoices):
        RESIDENTIAL = 'residential', 'Residential'
        AGRICULTURAL = 'agricultural', 'Agricultural'
        COMMERCIAL = 'commercial', 'Commercial'
        INDUSTRIAL = 'industrial', 'Industrial'

    class ConnectionStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        DISCONNECTED = 'disconnected', 'Disconnected'
        SUSPENDED = 'suspended', 'Suspended'
        PENDING = 'pending', 'Pending Connection'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transformer = models.ForeignKey(Transformer, on_delete=models.CASCADE, related_name='houses')
    consumer_id = models.CharField(max_length=50, unique=True)  # e.g., "CON-ANAND-VLG001-TRF01-001"
    consumer_name = models.CharField(max_length=200)
    address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True)
    connection_type = models.CharField(
        max_length=20, 
        choices=ConnectionType.choices, 
        default=ConnectionType.RESIDENTIAL
    )
    connected_load_kw = models.DecimalField(max_digits=10, decimal_places=2, default=2.0)  # sanctioned load
    meter_number = models.CharField(max_length=50, blank=True)
    connection_date = models.DateField(null=True, blank=True)
    connection_status = models.CharField(
        max_length=20, 
        choices=ConnectionStatus.choices, 
        default=ConnectionStatus.ACTIVE
    )
    gps_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    gps_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Houses"
        ordering = ['consumer_id']

    def __str__(self):
        return f"{self.consumer_id} - {self.consumer_name}"


class ElectricityReading(models.Model):
    """Reading capturing voltage sent from transformer vs received at house"""
    
    class ReadingStatus(models.TextChoices):
        NORMAL = 'normal', 'Normal'
        LOW_VOLTAGE = 'low_voltage', 'Low Voltage'
        HIGH_VOLTAGE = 'high_voltage', 'High Voltage'
        LOSS_DETECTED = 'loss_detected', 'Loss Detected'
        THEFT_SUSPECTED = 'theft_suspected', 'Theft Suspected'
        EQUIPMENT_FAULT = 'equipment_fault', 'Equipment Fault'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='readings')
    transformer = models.ForeignKey(Transformer, on_delete=models.CASCADE, related_name='readings')
    
    # Voltage readings
    voltage_sent = models.DecimalField(max_digits=10, decimal_places=2)  # From transformer
    voltage_received = models.DecimalField(max_digits=10, decimal_places=2)  # At house meter
    voltage_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Calculated loss
    voltage_loss_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Current readings
    current_sent = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Amps from transformer
    current_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Amps at house
    
    # Power readings
    power_sent_kw = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # kW from transformer
    power_received_kw = models.DecimalField(max_digits=10, decimal_places=3, default=0)  # kW at house
    power_loss_kw = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    power_loss_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Energy readings
    energy_sent_kwh = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    energy_received_kwh = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    energy_loss_kwh = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    
    # Additional metrics
    power_factor = models.DecimalField(max_digits=4, decimal_places=2, default=0.95)
    frequency = models.DecimalField(max_digits=5, decimal_places=2, default=50.0)
    line_distance_meters = models.DecimalField(max_digits=10, decimal_places=2, default=100)  # Distance from transformer
    
    # Status
    status = models.CharField(max_length=20, choices=ReadingStatus.choices, default=ReadingStatus.NORMAL)
    is_anomaly = models.BooleanField(default=False)
    
    # Timestamps
    reading_timestamp = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reading_timestamp']
        indexes = [
            models.Index(fields=['house', 'reading_timestamp']),
            models.Index(fields=['transformer', 'reading_timestamp']),
            models.Index(fields=['status']),
            models.Index(fields=['is_anomaly']),
        ]

    def __str__(self):
        return f"{self.house.consumer_id} - {self.reading_timestamp}"

    def save(self, *args, **kwargs):
        # Calculate losses
        self.voltage_loss = self.voltage_sent - self.voltage_received
        if self.voltage_sent > 0:
            self.voltage_loss_percentage = (self.voltage_loss / self.voltage_sent) * 100
        
        self.power_loss_kw = self.power_sent_kw - self.power_received_kw
        if self.power_sent_kw > 0:
            self.power_loss_percentage = (self.power_loss_kw / self.power_sent_kw) * 100
        
        self.energy_loss_kwh = self.energy_sent_kwh - self.energy_received_kwh
        
        # Determine status based on loss
        self._update_status()
        
        super().save(*args, **kwargs)

    def _update_status(self):
        """Update status based on readings"""
        # Normal acceptable loss is 2-5% for distribution
        NORMAL_LOSS_THRESHOLD = 5.0
        THEFT_THRESHOLD = 15.0
        LOW_VOLTAGE_THRESHOLD = 207  # 10% below 230V
        HIGH_VOLTAGE_THRESHOLD = 253  # 10% above 230V
        
        if self.voltage_received < LOW_VOLTAGE_THRESHOLD:
            self.status = self.ReadingStatus.LOW_VOLTAGE
            self.is_anomaly = True
        elif self.voltage_received > HIGH_VOLTAGE_THRESHOLD:
            self.status = self.ReadingStatus.HIGH_VOLTAGE
            self.is_anomaly = True
        elif self.power_loss_percentage > THEFT_THRESHOLD:
            self.status = self.ReadingStatus.THEFT_SUSPECTED
            self.is_anomaly = True
        elif self.power_loss_percentage > NORMAL_LOSS_THRESHOLD:
            self.status = self.ReadingStatus.LOSS_DETECTED
            self.is_anomaly = True
        else:
            self.status = self.ReadingStatus.NORMAL
            self.is_anomaly = False


class LossAlert(models.Model):
    """Alert generated when electricity loss is detected"""
    
    class AlertSeverity(models.TextChoices):
        INFO = 'info', 'Information'
        WARNING = 'warning', 'Warning'
        CRITICAL = 'critical', 'Critical'
        EMERGENCY = 'emergency', 'Emergency'

    class AlertType(models.TextChoices):
        VOLTAGE_DROP = 'voltage_drop', 'Voltage Drop'
        POWER_LOSS = 'power_loss', 'Power Loss'
        THEFT_SUSPECTED = 'theft_suspected', 'Theft Suspected'
        EQUIPMENT_FAULT = 'equipment_fault', 'Equipment Fault'
        OVERLOAD = 'overload', 'Overload'
        LINE_FAULT = 'line_fault', 'Line Fault'

    class AlertStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
        INVESTIGATING = 'investigating', 'Under Investigation'
        RESOLVED = 'resolved', 'Resolved'
        FALSE_ALARM = 'false_alarm', 'False Alarm'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reading = models.ForeignKey(ElectricityReading, on_delete=models.CASCADE, related_name='alerts')
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='loss_alerts')
    transformer = models.ForeignKey(Transformer, on_delete=models.CASCADE, related_name='loss_alerts')
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name='loss_alerts')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='loss_alerts')
    
    alert_type = models.CharField(max_length=20, choices=AlertType.choices)
    severity = models.CharField(max_length=20, choices=AlertSeverity.choices)
    status = models.CharField(max_length=20, choices=AlertStatus.choices, default=AlertStatus.ACTIVE)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Loss details
    voltage_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    voltage_loss_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    power_loss_kw = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    power_loss_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    estimated_financial_loss = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # In INR
    
    # Resolution
    acknowledged_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['transformer', 'created_at']),
            models.Index(fields=['village', 'created_at']),
            models.Index(fields=['district', 'created_at']),
        ]

    def __str__(self):
        return f"{self.alert_type} - {self.house.consumer_id} - {self.severity}"

    def acknowledge(self, user):
        """Acknowledge the alert"""
        self.status = self.AlertStatus.ACKNOWLEDGED
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save()

    def resolve(self, user, notes=""):
        """Resolve the alert"""
        self.status = self.AlertStatus.RESOLVED
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()


class CompanyAdmin(models.Model):
    """Admin users for the company"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_admin_profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='admins')
    employee_id = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    can_manage_districts = models.BooleanField(default=False)
    can_manage_alerts = models.BooleanField(default=True)
    can_view_reports = models.BooleanField(default=True)
    is_super_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Admin"
        verbose_name_plural = "Company Admins"

    def __str__(self):
        return f"{self.user.username} - {self.company.name}"
