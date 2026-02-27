"""
WebSocket Consumers for Real-Time Updates
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers import serialize
from .models import Meter, MeterReading, Alert
import logging

logger = logging.getLogger(__name__)


class MeterReadingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for streaming live meter readings
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.meter_id = self.scope['url_route']['kwargs']['meter_id']
        self.room_group_name = f'meter_{self.meter_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected for meter: {self.meter_id}")
        
        # Send initial data
        initial_data = await self.get_initial_data()
        await self.send(text_data=json.dumps(initial_data))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected for meter: {self.meter_id}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            command = data.get('command')
            
            if command == 'get_latest':
                latest_data = await self.get_latest_reading()
                await self.send(text_data=json.dumps(latest_data))
            
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Invalid message format'
            }))
    
    async def meter_reading(self, event):
        """Handle meter reading updates from group"""
        await self.send(text_data=json.dumps({
            'type': 'meter_reading',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_initial_data(self):
        """Get initial meter data and latest readings"""
        try:
            meter = Meter.objects.get(meter_id=self.meter_id)
            latest_readings = MeterReading.objects.filter(
                meter=meter
            ).order_by('-timestamp')[:10]
            
            return {
                'type': 'initial_data',
                'meter': {
                    'meter_id': meter.meter_id,
                    'meter_type': meter.meter_type,
                    'status': meter.status,
                    'location': meter.location,
                    'manufacturer': meter.manufacturer,
                },
                'readings': [
                    {
                        'id': reading.id,
                        'timestamp': reading.timestamp.isoformat(),
                        'voltage': float(reading.voltage),
                        'current': float(reading.current),
                        'power': float(reading.power),
                        'energy': float(reading.energy),
                        'power_factor': float(reading.power_factor),
                        'frequency': float(reading.frequency),
                        'is_anomaly': reading.is_anomaly,
                    }
                    for reading in latest_readings
                ]
            }
        except Meter.DoesNotExist:
            return {
                'type': 'error',
                'error': f'Meter {self.meter_id} not found'
            }
    
    @database_sync_to_async
    def get_latest_reading(self):
        """Get latest meter reading"""
        try:
            meter = Meter.objects.get(meter_id=self.meter_id)
            reading = MeterReading.objects.filter(meter=meter).latest('timestamp')
            
            return {
                'type': 'latest_reading',
                'data': {
                    'id': reading.id,
                    'timestamp': reading.timestamp.isoformat(),
                    'voltage': float(reading.voltage),
                    'current': float(reading.current),
                    'power': float(reading.power),
                    'energy': float(reading.energy),
                    'power_factor': float(reading.power_factor),
                    'frequency': float(reading.frequency),
                    'is_anomaly': reading.is_anomaly,
                }
            }
        except (Meter.DoesNotExist, MeterReading.DoesNotExist):
            return {
                'type': 'error',
                'error': 'No data available'
            }


class DashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for dashboard updates
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.room_group_name = 'dashboard_updates'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info("Dashboard WebSocket connected")
        
        # Send initial dashboard stats
        stats = await self.get_dashboard_stats()
        await self.send(text_data=json.dumps(stats))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info("Dashboard WebSocket disconnected")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            command = data.get('command')
            
            if command == 'refresh':
                stats = await self.get_dashboard_stats()
                await self.send(text_data=json.dumps(stats))
            
        except Exception as e:
            logger.error(f"Error processing dashboard message: {str(e)}")
    
    async def dashboard_update(self, event):
        """Handle dashboard updates from group"""
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        from django.db.models import Count, Avg, Sum
        from datetime import timedelta
        from django.utils import timezone
        
        now = timezone.now()
        
        return {
            'type': 'dashboard_stats',
            'data': {
                'total_meters': Meter.objects.filter(status='active').count(),
                'total_users': Meter.objects.values('user').distinct().count(),
                'active_alerts': Alert.objects.filter(
                    status__in=['pending', 'acknowledged']
                ).count(),
                'total_energy_today': float(
                    MeterReading.objects.filter(
                        timestamp__gte=now.replace(hour=0, minute=0, second=0)
                    ).aggregate(
                        total=Sum('energy')
                    )['total'] or 0
                ),
                'avg_power_factor': float(
                    MeterReading.objects.filter(
                        timestamp__gte=now - timedelta(hours=24)
                    ).aggregate(
                        avg=Avg('power_factor')
                    )['avg'] or 0
                ),
                'timestamp': now.isoformat()
            }
        }


class AlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time alerts
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.room_group_name = 'alerts'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info("Alert WebSocket connected")
        
        # Send recent alerts
        recent_alerts = await self.get_recent_alerts()
        await self.send(text_data=json.dumps(recent_alerts))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info("Alert WebSocket disconnected")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            command = data.get('command')
            
            if command == 'get_recent':
                alerts = await self.get_recent_alerts()
                await self.send(text_data=json.dumps(alerts))
            
        except Exception as e:
            logger.error(f"Error processing alert message: {str(e)}")
    
    async def new_alert(self, event):
        """Handle new alert from group"""
        await self.send(text_data=json.dumps({
            'type': 'new_alert',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_recent_alerts(self):
        """Get recent alerts"""
        alerts = Alert.objects.select_related('meter', 'meter__user').filter(
            status__in=['pending', 'acknowledged']
        ).order_by('-timestamp')[:20]
        
        return {
            'type': 'recent_alerts',
            'data': [
                {
                    'id': alert.id,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'message': alert.message,
                    'status': alert.status,
                    'timestamp': alert.timestamp.isoformat(),
                    'meter_id': alert.meter.meter_id,
                    'user': alert.meter.user.get_full_name(),
                }
                for alert in alerts
            ]
        }
