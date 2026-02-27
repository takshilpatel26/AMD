"""
Analytics Serializers - DRF Serializers for Analytics Models
"""

from rest_framework import serializers
from .models import EnergyForecast, ConsumptionPattern, EfficiencyScore, CarbonImpact
from meters.models import Meter


class EnergyForecastSerializer(serializers.ModelSerializer):
    """Serializer for energy forecasts"""
    
    meter_id = serializers.CharField(source='meter.meter_id', read_only=True)
    meter_location = serializers.CharField(source='meter.location', read_only=True)
    
    class Meta:
        model = EnergyForecast
        fields = [
            'id', 'meter', 'meter_id', 'meter_location',
            'forecast_date', 'forecast_hour', 'predicted_energy',
            'predicted_power', 'confidence_score', 'model_version',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConsumptionPatternSerializer(serializers.ModelSerializer):
    """Serializer for consumption patterns"""
    
    meter_id = serializers.CharField(source='meter.meter_id', read_only=True)
    duration_days = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsumptionPattern
        fields = [
            'id', 'meter', 'meter_id', 'pattern_type',
            'period_start', 'period_end', 'duration_days',
            'total_energy', 'avg_power', 'peak_power', 'peak_time',
            'off_peak_energy', 'efficiency_score', 'power_factor_avg',
            'estimated_cost', 'potential_savings', 'insights',
            'recommendations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_duration_days(self, obj):
        """Calculate duration in days"""
        return (obj.period_end - obj.period_start).days + 1


class EfficiencyScoreSerializer(serializers.ModelSerializer):
    """Serializer for efficiency scores"""
    
    meter_id = serializers.CharField(source='meter.meter_id', read_only=True)
    efficiency_grade = serializers.SerializerMethodField()
    savings_potential = serializers.SerializerMethodField()
    
    class Meta:
        model = EfficiencyScore
        fields = [
            'id', 'meter', 'meter_id', 'date', 'score',
            'efficiency_grade', 'power_factor_score',
            'load_profile_score', 'peak_usage_score',
            'consistency_score', 'total_energy', 'optimal_energy',
            'wasted_energy', 'savings_potential', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_efficiency_grade(self, obj):
        """Get letter grade based on score"""
        if obj.score >= 90:
            return 'A+'
        elif obj.score >= 80:
            return 'A'
        elif obj.score >= 70:
            return 'B'
        elif obj.score >= 60:
            return 'C'
        elif obj.score >= 50:
            return 'D'
        else:
            return 'F'
    
    def get_savings_potential(self, obj):
        """Calculate potential savings percentage"""
        if obj.optimal_energy > 0:
            savings_percent = (obj.wasted_energy / obj.optimal_energy) * 100
            return round(savings_percent, 2)
        return 0


class CarbonFootprintSerializer(serializers.ModelSerializer):
    """Serializer for carbon footprint"""
    
    meter_id = serializers.CharField(source='meter.meter_id', read_only=True)
    net_carbon = serializers.SerializerMethodField()
    
    class Meta:
        model = CarbonImpact
        fields = [
            'id', 'meter', 'meter_id', 'date', 'energy_consumed',
            'carbon_emitted', 'carbon_saved', 'net_carbon',
            'trees_equivalent', 'renewable_energy_used',
            'renewable_percentage', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_net_carbon(self, obj):
        """Calculate net carbon (emitted - saved)"""
        return round(obj.carbon_emitted - obj.carbon_saved, 2)


class ConsumptionTrendSerializer(serializers.Serializer):
    """Serializer for consumption trend data"""
    
    date = serializers.DateField()
    energy = serializers.FloatField()
    avg_power = serializers.FloatField()
    peak_power = serializers.FloatField()
    cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    efficiency_score = serializers.IntegerField()


class AnalyticsSummarySerializer(serializers.Serializer):
    """Serializer for analytics summary dashboard"""
    
    total_energy = serializers.FloatField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_efficiency = serializers.FloatField()
    total_carbon = serializers.FloatField()
    potential_savings = serializers.DecimalField(max_digits=10, decimal_places=2)
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    comparison_data = serializers.DictField(required=False)
