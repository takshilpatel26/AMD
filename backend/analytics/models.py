from django.db import models
from meters.models import User, Meter
from django.utils import timezone


class EnergyForecast(models.Model):
    """ML-generated energy consumption forecasts"""
    
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name='forecasts')
    forecast_date = models.DateField(db_index=True)
    forecast_hour = models.IntegerField(default=0)  # 0-23
    predicted_energy = models.FloatField()  # kWh
    predicted_power = models.FloatField()  # Watts
    confidence_score = models.FloatField(default=0.0)  # 0-1
    model_version = models.CharField(max_length=20, default='v1.0')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'energy_forecasts'
        ordering = ['forecast_date', 'forecast_hour']
        indexes = [
            models.Index(fields=['meter', 'forecast_date']),
        ]
        unique_together = ['meter', 'forecast_date', 'forecast_hour']
    
    def __str__(self):
        return f"Forecast {self.meter.meter_id} - {self.forecast_date} {self.forecast_hour}:00"


class ConsumptionPattern(models.Model):
    """User consumption pattern analysis"""
    
    PATTERN_TYPES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name='patterns')
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Consumption metrics
    total_energy = models.FloatField(default=0)  # kWh
    avg_power = models.FloatField(default=0)  # Watts
    peak_power = models.FloatField(default=0)  # Watts
    peak_time = models.TimeField(null=True, blank=True)
    off_peak_energy = models.FloatField(default=0)  # kWh
    
    # Efficiency metrics
    efficiency_score = models.FloatField(default=0)  # 0-100
    power_factor_avg = models.FloatField(default=0.95)
    
    # Cost analysis
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    potential_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Pattern insights (JSON)
    insights = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consumption_patterns'
        ordering = ['-period_end']
        indexes = [
            models.Index(fields=['meter', '-period_end']),
        ]
    
    def __str__(self):
        return f"{self.meter.meter_id} - {self.pattern_type} ({self.period_start})"


class EfficiencyScore(models.Model):
    """Daily efficiency scores for meters"""
    
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name='efficiency_scores')
    date = models.DateField(db_index=True)
    score = models.IntegerField(default=0)  # 0-100
    
    # Contributing factors
    power_factor_score = models.IntegerField(default=0)
    load_profile_score = models.IntegerField(default=0)
    peak_usage_score = models.IntegerField(default=0)
    consistency_score = models.IntegerField(default=0)
    
    # Breakdown
    total_energy = models.FloatField(default=0)
    optimal_energy = models.FloatField(default=0)
    wasted_energy = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'efficiency_scores'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['meter', '-date']),
        ]
        unique_together = ['meter', 'date']
    
    def __str__(self):
        return f"{self.meter.meter_id} - {self.date} ({self.score}%)"
    
    def calculate_score(self):
        """Calculate overall efficiency score"""
        self.score = int(
            (self.power_factor_score * 0.3) +
            (self.load_profile_score * 0.3) +
            (self.peak_usage_score * 0.2) +
            (self.consistency_score * 0.2)
        )
        return self.score


class CarbonImpact(models.Model):
    """Carbon footprint tracking"""
    
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name='carbon_impacts')
    date = models.DateField(db_index=True)
    
    # Energy consumption
    energy_consumed = models.FloatField(default=0)  # kWh
    
    # Carbon metrics
    carbon_emitted = models.FloatField(default=0)  # kg CO2
    carbon_saved = models.FloatField(default=0)  # kg CO2 compared to baseline
    trees_equivalent = models.FloatField(default=0)  # Number of trees planted equivalent
    
    # Renewable energy contribution
    renewable_energy_used = models.FloatField(default=0)  # kWh
    renewable_percentage = models.FloatField(default=0)  # %
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'carbon_impacts'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['meter', '-date']),
        ]
        unique_together = ['meter', 'date']
    
    def __str__(self):
        return f"{self.meter.meter_id} - {self.date} ({self.carbon_emitted} kg CO2)"
    
    def calculate_carbon(self, emission_factor=0.82):
        """Calculate carbon emissions (default: 0.82 kg CO2 per kWh for India)"""
        self.carbon_emitted = self.energy_consumed * emission_factor
        self.trees_equivalent = self.carbon_emitted / 21.77  # Average tree absorbs 21.77 kg CO2/year
        return self.carbon_emitted

