from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Meter, MeterReading, Alert, Notification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'village', 'state', 'is_active']
    list_filter = ['role', 'state', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'village']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Gram Meter Profile', {
            'fields': ('role', 'phone_number', 'whatsapp_number', 'village', 
                      'district', 'state', 'preferred_language', 'profile_picture')
        }),
    )


@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    list_display = ['meter_id', 'user', 'meter_type', 'status', 'location', 'installation_date']
    list_filter = ['meter_type', 'status', 'installation_date']
    search_fields = ['meter_id', 'user__username', 'location', 'manufacturer']
    date_hierarchy = 'installation_date'


@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ['meter', 'timestamp', 'voltage', 'current', 'power', 'energy', 'is_anomaly']
    list_filter = ['is_anomaly', 'timestamp']
    search_fields = ['meter__meter_id']
    date_hierarchy = 'timestamp'
    readonly_fields = ['apparent_power', 'reactive_power']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['meter', 'alert_type', 'severity', 'status', 'created_at']
    list_filter = ['alert_type', 'severity', 'status', 'created_at']
    search_fields = ['meter__meter_id', 'title', 'message']
    date_hierarchy = 'created_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'channel', 'status', 'recipient', 'sent_at', 'created_at']
    list_filter = ['channel', 'status', 'created_at']
    search_fields = ['user__username', 'recipient', 'message']
    date_hierarchy = 'created_at'

