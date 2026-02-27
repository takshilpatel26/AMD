"""
DRF Serializers for Distribution Network
"""

from rest_framework import serializers
from .models import (
    Company, District, Village, Transformer, House,
    ElectricityReading, LossAlert, CompanyAdmin
)


class CompanySerializer(serializers.ModelSerializer):
    district_count = serializers.SerializerMethodField()
    total_transformers = serializers.SerializerMethodField()
    total_houses = serializers.SerializerMethodField()
    active_alerts = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'code', 'address', 'contact_email', 'contact_phone',
            'logo_url', 'is_active', 'district_count', 'total_transformers',
            'total_houses', 'active_alerts', 'created_at', 'updated_at'
        ]

    def get_district_count(self, obj):
        return obj.districts.count()

    def get_total_transformers(self, obj):
        count = 0
        for district in obj.districts.all():
            for village in district.villages.all():
                count += village.transformers.count()
        return count

    def get_total_houses(self, obj):
        count = 0
        for district in obj.districts.all():
            for village in district.villages.all():
                for transformer in village.transformers.all():
                    count += transformer.houses.count()
        return count

    def get_active_alerts(self, obj):
        count = 0
        for district in obj.districts.all():
            count += district.loss_alerts.filter(status='active').count()
        return count


class DistrictSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    village_count = serializers.SerializerMethodField()
    transformer_count = serializers.SerializerMethodField()
    house_count = serializers.SerializerMethodField()
    active_alerts = serializers.SerializerMethodField()

    class Meta:
        model = District
        fields = [
            'id', 'company', 'company_name', 'name', 'code', 'state',
            'total_capacity_kva', 'is_active', 'village_count', 
            'transformer_count', 'house_count', 'active_alerts',
            'created_at', 'updated_at'
        ]

    def get_village_count(self, obj):
        return obj.villages.count()

    def get_transformer_count(self, obj):
        return sum(v.transformers.count() for v in obj.villages.all())

    def get_house_count(self, obj):
        count = 0
        for village in obj.villages.all():
            for transformer in village.transformers.all():
                count += transformer.houses.count()
        return count

    def get_active_alerts(self, obj):
        return obj.loss_alerts.filter(status='active').count()


class DistrictListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing districts"""
    village_count = serializers.SerializerMethodField()
    active_alerts = serializers.SerializerMethodField()

    class Meta:
        model = District
        fields = ['id', 'name', 'code', 'state', 'village_count', 'active_alerts']

    def get_village_count(self, obj):
        return obj.villages.count()

    def get_active_alerts(self, obj):
        return obj.loss_alerts.filter(status='active').count()


class VillageSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)
    transformer_count = serializers.SerializerMethodField()
    house_count = serializers.SerializerMethodField()
    active_alerts = serializers.SerializerMethodField()

    class Meta:
        model = Village
        fields = [
            'id', 'district', 'district_name', 'name', 'code', 'pincode',
            'population', 'total_households', 'gps_latitude', 'gps_longitude',
            'is_active', 'transformer_count', 'house_count', 'active_alerts',
            'created_at', 'updated_at'
        ]

    def get_transformer_count(self, obj):
        return obj.transformers.count()

    def get_house_count(self, obj):
        return sum(t.houses.count() for t in obj.transformers.all())

    def get_active_alerts(self, obj):
        return obj.loss_alerts.filter(status='active').count()


class VillageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing villages"""
    transformer_count = serializers.SerializerMethodField()
    active_alerts = serializers.SerializerMethodField()

    class Meta:
        model = Village
        fields = ['id', 'name', 'code', 'transformer_count', 'active_alerts']

    def get_transformer_count(self, obj):
        return obj.transformers.count()

    def get_active_alerts(self, obj):
        return obj.loss_alerts.filter(status='active').count()


class TransformerSerializer(serializers.ModelSerializer):
    village_name = serializers.CharField(source='village.name', read_only=True)
    district_name = serializers.CharField(source='village.district.name', read_only=True)
    house_count = serializers.SerializerMethodField()
    current_load_percentage = serializers.SerializerMethodField()
    active_alerts = serializers.SerializerMethodField()

    class Meta:
        model = Transformer
        fields = [
            'id', 'village', 'village_name', 'district_name', 'transformer_id',
            'name', 'transformer_type', 'capacity_kva', 'input_voltage',
            'output_voltage', 'efficiency_rating', 'max_houses',
            'installation_date', 'last_maintenance_date', 'gps_latitude',
            'gps_longitude', 'status', 'is_active', 'house_count',
            'current_load_percentage', 'active_alerts', 'created_at', 'updated_at'
        ]

    def get_house_count(self, obj):
        return obj.houses.count()

    def get_current_load_percentage(self, obj):
        return round(obj.current_load_percentage, 2)

    def get_active_alerts(self, obj):
        return obj.loss_alerts.filter(status='active').count()


class TransformerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing transformers"""
    house_count = serializers.SerializerMethodField()
    active_alerts = serializers.SerializerMethodField()

    class Meta:
        model = Transformer
        fields = [
            'id', 'transformer_id', 'name', 'capacity_kva', 'status',
            'house_count', 'active_alerts'
        ]

    def get_house_count(self, obj):
        return obj.houses.count()

    def get_active_alerts(self, obj):
        return obj.loss_alerts.filter(status='active').count()


class HouseSerializer(serializers.ModelSerializer):
    transformer_id_display = serializers.CharField(source='transformer.transformer_id', read_only=True)
    village_name = serializers.CharField(source='transformer.village.name', read_only=True)
    latest_reading = serializers.SerializerMethodField()
    has_active_alert = serializers.SerializerMethodField()

    class Meta:
        model = House
        fields = [
            'id', 'transformer', 'transformer_id_display', 'village_name',
            'consumer_id', 'consumer_name', 'address', 'phone_number',
            'connection_type', 'connected_load_kw', 'meter_number',
            'connection_date', 'connection_status', 'gps_latitude',
            'gps_longitude', 'is_active', 'latest_reading', 'has_active_alert',
            'created_at', 'updated_at'
        ]

    def get_latest_reading(self, obj):
        reading = obj.readings.first()
        if reading:
            return {
                'voltage_sent': float(reading.voltage_sent),
                'voltage_received': float(reading.voltage_received),
                'voltage_loss_percentage': float(reading.voltage_loss_percentage),
                'power_loss_percentage': float(reading.power_loss_percentage),
                'status': reading.status,
                'timestamp': reading.reading_timestamp
            }
        return None

    def get_has_active_alert(self, obj):
        return obj.loss_alerts.filter(status='active').exists()


class HouseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing houses"""
    status = serializers.SerializerMethodField()
    has_alert = serializers.SerializerMethodField()

    class Meta:
        model = House
        fields = ['id', 'consumer_id', 'consumer_name', 'connection_type', 'status', 'has_alert']

    def get_status(self, obj):
        reading = obj.readings.first()
        return reading.status if reading else 'no_data'

    def get_has_alert(self, obj):
        return obj.loss_alerts.filter(status='active').exists()


class ElectricityReadingSerializer(serializers.ModelSerializer):
    house_consumer_id = serializers.CharField(source='house.consumer_id', read_only=True)
    house_consumer_name = serializers.CharField(source='house.consumer_name', read_only=True)
    transformer_id_display = serializers.CharField(source='transformer.transformer_id', read_only=True)

    class Meta:
        model = ElectricityReading
        fields = [
            'id', 'house', 'house_consumer_id', 'house_consumer_name',
            'transformer', 'transformer_id_display', 'voltage_sent',
            'voltage_received', 'voltage_loss', 'voltage_loss_percentage',
            'current_sent', 'current_received', 'power_sent_kw',
            'power_received_kw', 'power_loss_kw', 'power_loss_percentage',
            'energy_sent_kwh', 'energy_received_kwh', 'energy_loss_kwh',
            'power_factor', 'frequency', 'line_distance_meters',
            'status', 'is_anomaly', 'reading_timestamp', 'created_at'
        ]
        read_only_fields = [
            'voltage_loss', 'voltage_loss_percentage', 'power_loss_kw',
            'power_loss_percentage', 'energy_loss_kwh', 'status', 'is_anomaly'
        ]


class LossAlertSerializer(serializers.ModelSerializer):
    house_consumer_id = serializers.CharField(source='house.consumer_id', read_only=True)
    house_consumer_name = serializers.CharField(source='house.consumer_name', read_only=True)
    transformer_id_display = serializers.CharField(source='transformer.transformer_id', read_only=True)
    village_name = serializers.CharField(source='village.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.username', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)

    class Meta:
        model = LossAlert
        fields = [
            'id', 'reading', 'house', 'house_consumer_id', 'house_consumer_name',
            'transformer', 'transformer_id_display', 'village', 'village_name',
            'district', 'district_name', 'alert_type', 'severity', 'status',
            'title', 'description', 'voltage_loss', 'voltage_loss_percentage',
            'power_loss_kw', 'power_loss_percentage', 'estimated_financial_loss',
            'acknowledged_by', 'acknowledged_by_name', 'acknowledged_at',
            'resolved_by', 'resolved_by_name', 'resolved_at', 'resolution_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'acknowledged_by', 'acknowledged_at', 'resolved_by', 'resolved_at'
        ]


class LossAlertListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing alerts"""
    house_consumer_id = serializers.CharField(source='house.consumer_id', read_only=True)
    transformer_id_display = serializers.CharField(source='transformer.transformer_id', read_only=True)
    village_name = serializers.CharField(source='village.name', read_only=True)

    class Meta:
        model = LossAlert
        fields = [
            'id', 'house_consumer_id', 'transformer_id_display', 'village_name',
            'alert_type', 'severity', 'status', 'title', 'power_loss_percentage',
            'created_at'
        ]


class CompanyAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = CompanyAdmin
        fields = [
            'id', 'user', 'username', 'email', 'company', 'company_name',
            'employee_id', 'department', 'designation', 'can_manage_districts',
            'can_manage_alerts', 'can_view_reports', 'is_super_admin',
            'created_at', 'updated_at'
        ]


# Dashboard Statistics Serializers
class DistributionDashboardStatsSerializer(serializers.Serializer):
    """Statistics for company admin dashboard"""
    total_districts = serializers.IntegerField()
    total_villages = serializers.IntegerField()
    total_transformers = serializers.IntegerField()
    total_houses = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()
    total_power_loss_kw = serializers.DecimalField(max_digits=12, decimal_places=3)
    average_loss_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    estimated_financial_loss = serializers.DecimalField(max_digits=15, decimal_places=2)
    transformers_with_issues = serializers.IntegerField()
    houses_with_anomalies = serializers.IntegerField()


class TransformerStatsSerializer(serializers.Serializer):
    """Statistics for a single transformer"""
    transformer_id = serializers.CharField()
    name = serializers.CharField()
    total_houses = serializers.IntegerField()
    houses_with_loss = serializers.IntegerField()
    average_voltage_loss = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_power_loss = serializers.DecimalField(max_digits=10, decimal_places=3)
    total_power_loss_kw = serializers.DecimalField(max_digits=10, decimal_places=3)
    active_alerts = serializers.IntegerField()
    status = serializers.CharField()
