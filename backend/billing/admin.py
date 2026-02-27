"""
Django Admin configuration for Billing app
Provides comprehensive admin interface for managing subscriptions, invoices, bills, payments, and tariffs
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from decimal import Decimal
from .models import (
    Subscription, UserSubscription, Invoice, InvoiceItem,
    Payment, Bill, TariffRate
)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscription model"""
    
    list_display = ['name', 'plan_type', 'price_display', 'billing_cycle', 
                    'max_meters', 'is_active', 'created_at']
    list_filter = ['plan_type', 'billing_cycle', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'billing_cycle')
        }),
        ('Limits', {
            'fields': ('max_meters', 'features')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        """Display formatted price"""
        return f"₹{obj.price}"
    price_display.short_description = 'Price'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for UserSubscription model"""
    
    list_display = ['user', 'subscription', 'status_display', 'start_date', 
                    'end_date', 'auto_renew', 'is_valid_display']
    list_filter = ['status', 'auto_renew', 'start_date', 'subscription__plan_type']
    search_fields = ['user__username', 'user__email', 'subscription__name']
    ordering = ['-start_date']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'subscription', 'status')
        }),
        ('Duration', {
            'fields': ('start_date', 'end_date', 'auto_renew')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_display(self, obj):
        """Display colored status"""
        colors = {
            'active': 'green',
            'expired': 'red',
            'cancelled': 'gray',
            'suspended': 'orange'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def is_valid_display(self, obj):
        """Display subscription validity"""
        if obj.is_valid():
            return format_html('<span style="color: green;">✓ Valid</span>')
        return format_html('<span style="color: red;">✗ Invalid</span>')
    is_valid_display.short_description = 'Valid'


class InvoiceItemInline(admin.TabularInline):
    """Inline admin for Invoice Items"""
    model = InvoiceItem
    extra = 1
    readonly_fields = ['amount']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin interface for Invoice model"""
    
    list_display = ['invoice_number', 'user', 'meter', 'total_amount_display', 
                    'status_display', 'due_date', 'created_at']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'user__username', 'meter__meter_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'total_amount']
    date_hierarchy = 'created_at'
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'user', 'meter', 'user_subscription')
        }),
        ('Billing Period', {
            'fields': ('billing_start_date', 'billing_end_date')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Energy Details', {
            'fields': ('energy_consumed', 'rate_per_unit')
        }),
        ('Payment Details', {
            'fields': ('status', 'due_date', 'paid_date', 'payment_method', 'transaction_id')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_paid', 'mark_as_overdue']
    
    def total_amount_display(self, obj):
        """Display formatted total amount"""
        return f"₹{obj.total_amount}"
    total_amount_display.short_description = 'Total Amount'
    
    def status_display(self, obj):
        """Display colored status"""
        colors = {
            'draft': 'gray',
            'pending': 'orange',
            'paid': 'green',
            'overdue': 'red',
            'cancelled': 'darkgray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def mark_as_paid(self, request, queryset):
        """Admin action to mark invoices as paid"""
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} invoices marked as paid.')
    mark_as_paid.short_description = 'Mark selected invoices as paid'
    
    def mark_as_overdue(self, request, queryset):
        """Admin action to mark invoices as overdue"""
        updated = queryset.update(status='overdue')
        self.message_user(request, f'{updated} invoices marked as overdue.')
    mark_as_overdue.short_description = 'Mark selected invoices as overdue'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model"""
    
    list_display = ['payment_id', 'user', 'invoice', 'amount_display', 
                    'payment_method', 'status_display', 'payment_date']
    list_filter = ['status', 'payment_method', 'payment_date', 'created_at']
    search_fields = ['payment_id', 'user__username', 'invoice__invoice_number', 
                     'gateway_transaction_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'invoice', 'user', 'amount')
        }),
        ('Payment Method', {
            'fields': ('payment_method', 'status', 'payment_date')
        }),
        ('Gateway Details', {
            'fields': ('gateway_name', 'gateway_transaction_id', 'gateway_response'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def amount_display(self, obj):
        """Display formatted amount"""
        return f"₹{obj.amount}"
    amount_display.short_description = 'Amount'
    
    def status_display(self, obj):
        """Display colored status"""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'success': 'green',
            'failed': 'red',
            'refunded': 'purple'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    """Admin interface for Bill model"""
    
    list_display = ['bill_number', 'user', 'meter', 'units_consumed', 
                    'total_amount_display', 'status_display', 'due_date']
    list_filter = ['status', 'due_date', 'billing_period_start']
    search_fields = ['bill_number', 'user__username', 'meter__meter_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'units_consumed']
    date_hierarchy = 'billing_period_start'
    
    fieldsets = (
        ('Bill Information', {
            'fields': ('bill_number', 'user', 'meter')
        }),
        ('Billing Period', {
            'fields': ('billing_period_start', 'billing_period_end')
        }),
        ('Readings', {
            'fields': ('previous_reading', 'current_reading', 'units_consumed')
        }),
        ('Charges', {
            'fields': ('base_charge', 'energy_charge', 'tax', 'subsidy', 'total_amount')
        }),
        ('Payment', {
            'fields': ('status', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['calculate_charges', 'mark_as_paid']
    
    def total_amount_display(self, obj):
        """Display formatted total amount"""
        return f"₹{obj.total_amount}"
    total_amount_display.short_description = 'Total Amount'
    
    def status_display(self, obj):
        """Display colored status"""
        colors = {
            'draft': 'gray',
            'pending': 'orange',
            'paid': 'green',
            'overdue': 'red',
            'cancelled': 'darkgray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def calculate_charges(self, request, queryset):
        """Admin action to recalculate charges"""
        for bill in queryset:
            bill.calculate_charges()
            bill.save()
        self.message_user(request, f'{queryset.count()} bills recalculated.')
    calculate_charges.short_description = 'Recalculate charges for selected bills'
    
    def mark_as_paid(self, request, queryset):
        """Admin action to mark bills as paid"""
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} bills marked as paid.')
    mark_as_paid.short_description = 'Mark selected bills as paid'


@admin.register(TariffRate)
class TariffRateAdmin(admin.ModelAdmin):
    """Admin interface for Tariff Rate model"""
    
    list_display = ['name', 'state', 'category', 'slab_display', 
                    'rate_display', 'fixed_charge_display', 'is_active']
    list_filter = ['state', 'category', 'is_active', 'subsidy_applicable']
    search_fields = ['name', 'state']
    ordering = ['state', 'category', 'slab_min']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Tariff Information', {
            'fields': ('name', 'state', 'category')
        }),
        ('Slab Definition', {
            'fields': ('slab_min', 'slab_max')
        }),
        ('Rates', {
            'fields': ('rate_per_unit', 'fixed_charge')
        }),
        ('Subsidy', {
            'fields': ('subsidy_applicable',)
        }),
        ('Validity', {
            'fields': ('effective_from', 'effective_to', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def slab_display(self, obj):
        """Display slab range"""
        return f"{obj.slab_min}-{obj.slab_max} units"
    slab_display.short_description = 'Slab Range'
    
    def rate_display(self, obj):
        """Display formatted rate"""
        return f"₹{obj.rate_per_unit}/unit"
    rate_display.short_description = 'Rate'
    
    def fixed_charge_display(self, obj):
        """Display formatted fixed charge"""
        return f"₹{obj.fixed_charge}"
    fixed_charge_display.short_description = 'Fixed Charge'


# Admin site customization
admin.site.site_header = 'Gram Meter Billing Administration'
admin.site.site_title = 'Gram Meter Billing Admin'
admin.site.index_title = 'Billing Management'

