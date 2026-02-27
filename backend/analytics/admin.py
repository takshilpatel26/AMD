"""
Django Admin configuration for Analytics app
Provides comprehensive admin interface for managing forecasts, consumption patterns, efficiency scores, and carbon impact
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Sum, Count
from .models import (
    EnergyForecast, ConsumptionPattern, EfficiencyScore, CarbonImpact
)


@admin.register(EnergyForecast)
class EnergyForecastAdmin(admin.ModelAdmin):
    """Admin interface for Energy Forecast model"""
    
    list_display = ['meter', 'forecast_date', 'predicted_consumption_display', 
                    'confidence_level_display', 'model_version', 'created_at']
    list_filter = ['forecast_date', 'model_version', 'created_at']
    search_fields = ['meter__meter_id', 'meter__user__username']
    ordering = ['-forecast_date', '-created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'forecast_date'
    
    fieldsets = (
        ('Forecast Details', {
            'fields': ('meter', 'forecast_date')
        }),
        ('Prediction', {
            'fields': ('predicted_consumption', 'confidence_level', 'prediction_range_min', 'prediction_range_max')
        }),
        ('Model Information', {
            'fields': ('model_version', 'algorithm_used')
        }),
        ('Metadata', {
            'fields': ('metadata', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def predicted_consumption_display(self, obj):
        """Display formatted predicted consumption"""
        return f"{obj.predicted_consumption:.2f} kWh"
    predicted_consumption_display.short_description = 'Predicted Consumption'
    
    def confidence_level_display(self, obj):
        """Display colored confidence level"""
        if obj.confidence_level >= 90:
            color = 'green'
        elif obj.confidence_level >= 70:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color,
            obj.confidence_level
        )
    confidence_level_display.short_description = 'Confidence'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('meter', 'meter__user')


@admin.register(ConsumptionPattern)
class ConsumptionPatternAdmin(admin.ModelAdmin):
    """Admin interface for Consumption Pattern model"""
    
    list_display = ['meter', 'period_start', 'period_end', 'total_energy_display', 
                    'pattern_type', 'efficiency_score', 'created_at']
    list_filter = ['period_start', 'pattern_type', 'created_at']
    search_fields = ['meter__meter_id', 'meter__user__username']
    ordering = ['-period_end', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'period_start'
    
    fieldsets = (
        ('Pattern Details', {
            'fields': ('meter', 'pattern_type', 'period_start', 'period_end')
        }),
        ('Consumption Metrics', {
            'fields': ('total_energy', 'avg_power', 'peak_power', 'peak_time', 'off_peak_energy')
        }),
        ('Efficiency', {
            'fields': ('efficiency_score', 'power_factor_avg')
        }),
        ('Cost Analysis', {
            'fields': ('estimated_cost', 'potential_savings')
        }),
        ('Insights', {
            'fields': ('insights', 'recommendations'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_energy_display(self, obj):
        """Display formatted total energy"""
        return f"{obj.total_energy:.2f} kWh"
    total_energy_display.short_description = 'Total Energy'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('meter', 'meter__user')


@admin.register(EfficiencyScore)
class EfficiencyScoreAdmin(admin.ModelAdmin):
    """Admin interface for Efficiency Score model"""
    
    list_display = ['meter', 'date', 'score_display',
                    'power_factor_score', 'load_profile_score', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['meter__meter_id', 'meter__user__username']
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Score Details', {
            'fields': ('meter', 'date', 'score')
        }),
        ('Individual Scores', {
            'fields': ('power_factor_score', 'load_profile_score', 
                      'peak_usage_score', 'consistency_score')
        }),
        ('Energy Breakdown', {
            'fields': ('total_energy', 'optimal_energy', 'wasted_energy')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['recalculate_scores']
    
    def score_display(self, obj):
        """Display colored score"""
        if obj.score >= 90:
            color = 'green'
        elif obj.score >= 75:
            color = 'blue'
        elif obj.score >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{}/100</span>',
            color,
            obj.score
        )
    score_display.short_description = 'Score'
    
    def recalculate_scores(self, request, queryset):
        """Admin action to recalculate scores"""
        updated = 0
        for score in queryset:
            score.calculate_score()
            score.save(update_fields=['score'])
            updated += 1
        
        self.message_user(request, f'{updated} scores recalculated.')
    recalculate_scores.short_description = 'Recalculate scores'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('meter', 'meter__user')


@admin.register(CarbonImpact)
class CarbonImpactAdmin(admin.ModelAdmin):
    """Admin interface for Carbon Impact model"""
    
    list_display = ['meter', 'date', 'energy_consumed_display', 
                    'carbon_emitted_display', 'trees_equivalent_display', 'carbon_saved_display']
    list_filter = ['date', 'created_at']
    search_fields = ['meter__meter_id', 'meter__user__username']
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Impact Details', {
            'fields': ('meter', 'date')
        }),
        ('Energy Consumption', {
            'fields': ('energy_consumed',)
        }),
        ('Carbon Footprint', {
            'fields': ('carbon_emitted', 'carbon_saved')
        }),
        ('Tree Equivalent', {
            'fields': ('trees_equivalent',)
        }),
        ('Renewable Energy', {
            'fields': ('renewable_energy_used', 'renewable_percentage')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def energy_consumed_display(self, obj):
        """Display formatted energy consumed"""
        return f"{obj.energy_consumed:.2f} kWh"
    energy_consumed_display.short_description = 'Energy Consumed'
    
    def carbon_emitted_display(self, obj):
        """Display formatted carbon emitted"""
        return format_html(
            '<span style="color: red;">{:.2f} kg CO₂</span>',
            obj.carbon_emitted
        )
    carbon_emitted_display.short_description = 'Carbon Emitted'
    
    def carbon_saved_display(self, obj):
        """Display formatted carbon saved"""
        return format_html(
            '<span style="color: green;">{:.2f} kg CO₂</span>',
            obj.carbon_saved
        )
    carbon_saved_display.short_description = 'Carbon Saved'
    
    def trees_equivalent_display(self, obj):
        """Display trees equivalent with icon"""
        return format_html(
            '<span style="color: green;">🌳 {:.1f} trees</span>',
            obj.trees_equivalent
        )
    trees_equivalent_display.short_description = 'Trees Equivalent'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('meter', 'meter__user')


# Custom admin site configuration
class AnalyticsAdminSite(admin.AdminSite):
    """Custom admin site for Analytics"""
    site_header = 'Gram Meter Analytics Administration'
    site_title = 'Gram Meter Analytics Admin'
    index_title = 'Analytics Management'
    
    def index(self, request, extra_context=None):
        """Customize admin index with analytics summary"""
        extra_context = extra_context or {}
        
        # Add analytics statistics
        extra_context['total_forecasts'] = EnergyForecast.objects.count()
        extra_context['total_patterns'] = ConsumptionPattern.objects.count()
        extra_context['total_scores'] = EfficiencyScore.objects.count()
        extra_context['total_carbon_reports'] = CarbonImpact.objects.count()
        
        # Average efficiency score
        avg_score = EfficiencyScore.objects.aggregate(Avg('overall_score'))
        extra_context['avg_efficiency_score'] = avg_score['overall_score__avg'] or 0
        
        # Total carbon saved
        total_saved = CarbonImpact.objects.aggregate(Sum('carbon_saved'))
        extra_context['total_carbon_saved'] = total_saved['carbon_saved__sum'] or 0
        
        return super().index(request, extra_context)


# Register models with custom admin site if needed
# analytics_admin_site = AnalyticsAdminSite(name='analytics_admin')
# analytics_admin_site.register(EnergyForecast, EnergyForecastAdmin)
# analytics_admin_site.register(ConsumptionPattern, ConsumptionPatternAdmin)
# analytics_admin_site.register(EfficiencyScore, EfficiencyScoreAdmin)
# analytics_admin_site.register(CarbonImpact, CarbonImpactAdmin)

