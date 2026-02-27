"""
Billing Serializers - DRF Serializers for Billing Models
"""

from rest_framework import serializers
from .models import Subscription, UserSubscription, Invoice, Bill, Payment, TariffRate
from meters.models import Meter


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'name', 'plan_type', 'description', 'price',
            'billing_cycle', 'max_meters', 'features',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions"""
    
    subscription_name = serializers.CharField(source='subscription.name', read_only=True)
    subscription_price = serializers.DecimalField(
        source='subscription.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    days_remaining = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'subscription', 'subscription_name',
            'subscription_price', 'status', 'start_date', 'end_date',
            'auto_renew', 'days_remaining', 'is_valid',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_days_remaining(self, obj):
        """Calculate days remaining"""
        from django.utils import timezone
        if obj.end_date > timezone.now():
            return (obj.end_date - timezone.now()).days
        return 0
    
    def get_is_valid(self, obj):
        """Check if subscription is valid"""
        return obj.is_valid()


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    meter_id = serializers.CharField(source='meter.meter_id', read_only=True, allow_null=True)
    payment_status = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'user', 'user_name', 'meter',
            'meter_id', 'user_subscription', 'billing_start_date',
            'billing_end_date', 'subtotal', 'tax_amount',
            'discount_amount', 'total_amount', 'energy_consumed',
            'rate_per_unit', 'status', 'payment_status', 'is_overdue',
            'due_date', 'issued_date', 'paid_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'created_at', 'updated_at']
    
    def get_payment_status(self, obj):
        """Get payment status with details"""
        if obj.status == 'paid':
            return 'Paid'
        elif obj.status == 'overdue':
            return 'Overdue'
        elif obj.status == 'pending':
            return 'Pending Payment'
        return obj.get_status_display()
    
    def get_is_overdue(self, obj):
        """Check if invoice is overdue"""
        from django.utils import timezone
        return obj.status == 'pending' and obj.due_date < timezone.now().date()


class BillSerializer(serializers.ModelSerializer):
    """Serializer for electricity bills"""
    
    meter_id = serializers.CharField(source='meter.meter_id', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    payment_made = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = [
            'id', 'bill_number', 'user', 'user_name', 'meter',
            'meter_id', 'billing_period_start', 'billing_period_end',
            'previous_reading', 'current_reading', 'units_consumed',
            'base_charge', 'energy_charge', 'tax', 'subsidy',
            'total_amount', 'due_date', 'status', 'payment_made',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'bill_number', 'created_at', 'updated_at']
    
    def get_payment_made(self, obj):
        """Get payment info if bill is paid"""
        if obj.status == 'paid':
            payment = Payment.objects.filter(bill=obj).first()
            if payment:
                return {
                    'payment_id': payment.id,
                    'amount': float(payment.amount),
                    'method': payment.payment_method,
                    'date': payment.payment_date
                }
        return None


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True, allow_null=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'user', 'user_name', 'invoice',
            'invoice_number', 'amount', 'payment_method', 'status',
            'gateway_name', 'gateway_transaction_id', 'gateway_response',
            'payment_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'payment_id', 'created_at', 'updated_at']


class TariffRateSerializer(serializers.ModelSerializer):
    """Serializer for tariff rates"""
    
    class Meta:
        model = TariffRate
        fields = [
            'id', 'name', 'state', 'category', 'slab_min',
            'slab_max', 'rate_per_unit', 'fixed_charge',
            'subsidy_applicable', 'effective_from', 'effective_to',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BillingSummarySerializer(serializers.Serializer):
    """Serializer for billing summary"""
    
    total_bills = serializers.IntegerField()
    paid_bills = serializers.IntegerField()
    pending_bills = serializers.IntegerField()
    overdue_bills = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    next_due_date = serializers.DateField(allow_null=True)
    subscription_status = serializers.CharField()
