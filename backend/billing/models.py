from django.db import models
from meters.models import User, Meter
from django.utils import timezone
from decimal import Decimal


class Subscription(models.Model):
    """Subscription plans for different user types"""
    
    PLAN_TYPES = (
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    )
    
    BILLING_CYCLES = (
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    )
    
    name = models.CharField(max_length=50)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')
    max_meters = models.IntegerField(default=1)
    features = models.JSONField(default=dict)  # Store features as JSON
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}/{self.billing_cycle}"


class UserSubscription(models.Model):
    """User's active subscription"""
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    subscription = models.ForeignKey(Subscription, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_subscriptions'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.subscription.name}"
    
    def is_valid(self):
        """Check if subscription is currently valid"""
        return self.status == 'active' and self.end_date > timezone.now()


class Invoice(models.Model):
    """Billing invoices for users"""
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    meter = models.ForeignKey(Meter, on_delete=models.SET_NULL, null=True, blank=True)
    user_subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Billing period
    billing_start_date = models.DateField()
    billing_end_date = models.DateField()
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Energy consumption details
    energy_consumed = models.FloatField(default=0)  # kWh
    rate_per_unit = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    paid_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.user.username}"
    
    def calculate_total(self):
        """Calculate the total amount"""
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        return self.total_amount
    
    def mark_as_paid(self, payment_method='', transaction_id=''):
        """Mark invoice as paid"""
        self.status = 'paid'
        self.paid_date = timezone.now()
        self.payment_method = payment_method
        self.transaction_id = transaction_id
        self.save()


class InvoiceItem(models.Model):
    """Line items in an invoice"""
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Energy-specific fields
    energy_consumed = models.FloatField(null=True, blank=True)  # kWh
    tariff_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'invoice_items'
    
    def __str__(self):
        return f"{self.description} - ₹{self.amount}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate amount
        self.amount = Decimal(str(self.quantity)) * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment transactions"""
    
    PAYMENT_METHODS = (
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Mobile Wallet'),
        ('cash', 'Cash'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    payment_id = models.CharField(max_length=100, unique=True, db_index=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # External payment gateway details
    gateway_name = models.CharField(max_length=50, blank=True)
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.payment_id} - ₹{self.amount}"


class Bill(models.Model):
    """Monthly electricity bills"""
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    bill_number = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name='bills')
    
    # Billing period
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    
    # Readings
    previous_reading = models.FloatField(default=0)  # kWh
    current_reading = models.FloatField(default=0)  # kWh
    units_consumed = models.FloatField(default=0)  # kWh
    
    # Charges
    base_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    energy_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subsidy = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Dates
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bills'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['meter', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Bill {self.bill_number} - {self.meter.meter_id}"
    
    def calculate_charges(self):
        """Calculate bill charges"""
        self.units_consumed = self.current_reading - self.previous_reading
        # Using average rate of ₹6 per unit
        self.energy_charge = Decimal(self.units_consumed) * Decimal('6.00')
        self.tax = self.energy_charge * Decimal('0.05')  # 5% tax
        self.total_amount = self.base_charge + self.energy_charge + self.tax - self.subsidy
        return self.total_amount


class TariffRate(models.Model):
    """Electricity tariff rates"""
    
    CATEGORIES = (
        ('domestic', 'Domestic'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('agricultural', 'Agricultural'),
    )
    
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    # Slab-based pricing (e.g., 0-100 units, 101-200 units)
    slab_min = models.IntegerField(default=0)
    slab_max = models.IntegerField(default=9999)
    rate_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    fixed_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Subsidy info
    subsidy_applicable = models.BooleanField(default=False)
    
    # Validity
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tariff_rates'
        ordering = ['category', 'slab_min']
        indexes = [
            models.Index(fields=['state', 'category']),
            models.Index(fields=['effective_from']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.slab_min}-{self.slab_max} units @ ₹{self.rate_per_unit}"

