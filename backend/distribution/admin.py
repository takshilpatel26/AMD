from django.contrib import admin
from .models import (
    Company, District, Village, Transformer, House,
    ElectricityReading, LossAlert, CompanyAdmin
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'company', 'state', 'is_active']
    list_filter = ['company', 'state', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'district', 'population', 'total_households']
    list_filter = ['district__company', 'district', 'is_active']
    search_fields = ['name', 'code', 'pincode']


@admin.register(Transformer)
class TransformerAdmin(admin.ModelAdmin):
    list_display = ['transformer_id', 'name', 'village', 'capacity_kva', 'status']
    list_filter = ['village__district', 'transformer_type', 'status']
    search_fields = ['transformer_id', 'name']


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ['consumer_id', 'consumer_name', 'transformer', 'connection_type', 'connection_status']
    list_filter = ['transformer__village', 'connection_type', 'connection_status']
    search_fields = ['consumer_id', 'consumer_name', 'meter_number']


@admin.register(ElectricityReading)
class ElectricityReadingAdmin(admin.ModelAdmin):
    list_display = ['house', 'voltage_sent', 'voltage_received', 'voltage_loss_percentage', 'status', 'reading_timestamp']
    list_filter = ['status', 'is_anomaly', 'transformer']
    search_fields = ['house__consumer_id']
    date_hierarchy = 'reading_timestamp'


@admin.register(LossAlert)
class LossAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'house', 'alert_type', 'severity', 'status', 'created_at']
    list_filter = ['alert_type', 'severity', 'status', 'district']
    search_fields = ['title', 'house__consumer_id']
    date_hierarchy = 'created_at'
