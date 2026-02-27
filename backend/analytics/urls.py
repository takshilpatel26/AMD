"""
Analytics URL Configuration - Including ML-powered endpoints
"""

from django.urls import path
from .views import AnalyticsViewSet

urlpatterns = [
    # Analytics endpoints
    path('summary/', AnalyticsViewSet.as_view({'get': 'summary'}), name='analytics-summary'),
    path('consumption/', AnalyticsViewSet.as_view({'get': 'consumption'}), name='analytics-consumption'),
    path('trends/', AnalyticsViewSet.as_view({'get': 'trends'}), name='analytics-trends'),
    path('efficiency/', AnalyticsViewSet.as_view({'get': 'efficiency'}), name='analytics-efficiency'),
    path('forecasts/', AnalyticsViewSet.as_view({'get': 'forecasts'}), name='analytics-forecasts'),
    path('patterns/', AnalyticsViewSet.as_view({'get': 'patterns'}), name='analytics-patterns'),
    path('carbon_footprint/', AnalyticsViewSet.as_view({'get': 'carbon_footprint'}), name='analytics-carbon'),
    
    # ML-powered endpoints (using trained models)
    path('ml/detect_anomaly/', AnalyticsViewSet.as_view({'post': 'detect_anomaly'}), name='analytics-ml-anomaly'),
    path('ml/predict_consumption/', AnalyticsViewSet.as_view({'post': 'predict_consumption'}), name='analytics-ml-predict'),
    path('ml/forecast_hourly/', AnalyticsViewSet.as_view({'post': 'forecast_hourly'}), name='analytics-ml-forecast-hourly'),
    path('ml/weekly_forecast/', AnalyticsViewSet.as_view({'get': 'ml_weekly_forecast'}), name='analytics-ml-weekly'),
    path('ml/pattern_analysis/', AnalyticsViewSet.as_view({'get': 'ml_pattern_analysis'}), name='analytics-ml-patterns'),
]

