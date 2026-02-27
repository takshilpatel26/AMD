"""
WebSocket URL Configuration for Meters App
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket endpoint for live meter readings
    re_path(r'ws/meters/(?P<meter_id>[\w-]+)/$', consumers.MeterReadingConsumer.as_asgi()),
    
    # WebSocket endpoint for dashboard updates
    re_path(r'ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
    
    # WebSocket endpoint for alerts
    re_path(r'ws/alerts/$', consumers.AlertConsumer.as_asgi()),
]
