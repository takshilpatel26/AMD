from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Meter, MeterReading, Alert, Notification

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    full_name = serializers.SerializerMethodField()
    meter_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'whatsapp_number', 'village', 'district',
            'state', 'preferred_language', 'profile_picture', 'meter_count',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    
    def get_meter_count(self, obj):
        return obj.meters.count()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm', 'first_name',
            'last_name', 'role', 'phone_number', 'whatsapp_number', 'village',
            'district', 'state', 'preferred_language'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class MeterSerializer(serializers.ModelSerializer):
    """Serializer for Meter model"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    latest_reading = serializers.SerializerMethodField()
    alert_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Meter
        fields = [
            'id', 'meter_id', 'user', 'user_name', 'meter_type', 'manufacturer',
            'model_number', 'installation_date', 'status', 'location', 'latitude',
            'longitude', 'rated_voltage', 'rated_current', 'latest_reading',
            'alert_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_latest_reading(self, obj):
        latest = obj.readings.first()
        if latest:
            return {
                'voltage': latest.voltage,
                'current': latest.current,
                'power': latest.power,
                'energy': latest.energy,
                'timestamp': latest.timestamp
            }
        return None
    
    def get_alert_count(self, obj):
        return obj.alerts.filter(status='active').count()


class MeterReadingSerializer(serializers.ModelSerializer):
    """Serializer for MeterReading model"""
    
    meter_id = serializers.CharField(source='meter.meter_id', read_only=True)
    
    class Meta:
        model = MeterReading
        fields = [
            'id', 'meter', 'meter_id', 'timestamp', 'voltage', 'current', 'power',
            'energy', 'power_factor', 'frequency', 'temperature', 'apparent_power',
            'reactive_power', 'is_anomaly', 'anomaly_type'
        ]
        read_only_fields = ['id', 'apparent_power', 'reactive_power']
    
    def validate(self, data):
        # Validate voltage range
        if data.get('voltage') and (data['voltage'] < 0 or data['voltage'] > 500):
            raise serializers.ValidationError("Voltage must be between 0 and 500V")
        
        # Validate current
        if data.get('current') and data['current'] < 0:
            raise serializers.ValidationError("Current cannot be negative")
        
        # Validate power factor
        if data.get('power_factor') and (data['power_factor'] < 0 or data['power_factor'] > 1):
            raise serializers.ValidationError("Power factor must be between 0 and 1")
        
        return data


class MeterReadingBulkSerializer(serializers.Serializer):
    """Serializer for bulk meter reading creation"""
    
    readings = MeterReadingSerializer(many=True)
    
    def create(self, validated_data):
        readings_data = validated_data.get('readings', [])
        readings = [MeterReading(**reading) for reading in readings_data]
        return MeterReading.objects.bulk_create(readings)


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model"""
    
    meter_id = serializers.CharField(source='meter.meter_id', read_only=True)
    user = serializers.SerializerMethodField()
    localized_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'meter', 'meter_id', 'user', 'reading', 'alert_type', 'severity',
            'status', 'title', 'message', 'localized_message', 'message_hindi',
            'message_gujarati', 'recommended_action', 'estimated_cost_impact',
            'created_at', 'acknowledged_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_user(self, obj):
        return {
            'id': obj.meter.user.id,
            'name': obj.meter.user.get_full_name(),
            'preferred_language': obj.meter.user.preferred_language
        }
    
    def get_localized_message(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'preferred_language'):
            lang = request.user.preferred_language
            if lang == 'hi' and obj.message_hindi:
                return obj.message_hindi
            elif lang == 'gu' and obj.message_gujarati:
                return obj.message_gujarati
        return obj.message


class AlertAcknowledgeSerializer(serializers.Serializer):
    """Serializer for acknowledging alerts"""
    
    alert_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    
    def validate_alert_ids(self, value):
        if not Alert.objects.filter(id__in=value).exists():
            raise serializers.ValidationError("Invalid alert IDs")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    alert_title = serializers.CharField(source='alert.title', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_name', 'alert', 'alert_title', 'channel',
            'status', 'recipient', 'message', 'external_id', 'error_message',
            'sent_at', 'delivered_at', 'read_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'external_id', 'sent_at', 'delivered_at', 'created_at'
        ]


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    
    total_energy = serializers.FloatField()
    current_power = serializers.FloatField()
    efficiency_score = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    monthly_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    cost_savings = serializers.DecimalField(max_digits=10, decimal_places=2)
    carbon_saved = serializers.FloatField()
    voltage = serializers.FloatField()
    current = serializers.FloatField()
    power_factor = serializers.FloatField()
