from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import Meter, MeterReading, Alert, Notification
from .serializers import (
    UserSerializer, UserRegistrationSerializer, MeterSerializer,
    MeterReadingSerializer, MeterReadingBulkSerializer, AlertSerializer,
    AlertAcknowledgeSerializer, NotificationSerializer, DashboardStatsSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User operations"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'village']
    ordering_fields = ['date_joined', 'username']
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MeterViewSet(viewsets.ModelViewSet):
    """ViewSet for Meter operations"""
    
    serializer_class = MeterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['meter_id', 'location', 'manufacturer']
    ordering_fields = ['installation_date', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'farmer':
            return Meter.objects.filter(user=user)
        elif user.role == 'sarpanch':
            return Meter.objects.filter(user__village=user.village)
        elif user.role in ['utility', 'government']:
            return Meter.objects.all()
        return Meter.objects.none()
    
    @action(detail=True, methods=['get'])
    def readings(self, request, pk=None):
        """Get meter readings with optional date range"""
        meter = self.get_object()
        
        # Parse query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        limit = int(request.query_params.get('limit', 100))
        
        queryset = meter.readings.all()
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        queryset = queryset[:limit]
        serializer = MeterReadingSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def live_status(self, request, pk=None):
        """Get live meter status"""
        meter = self.get_object()
        latest_reading = meter.readings.first()
        
        if not latest_reading:
            return Response({'error': 'No readings available'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if meter is online (reading within last 5 minutes)
        is_online = (timezone.now() - latest_reading.timestamp) < timedelta(minutes=5)
        
        return Response({
            'meter_id': meter.meter_id,
            'status': meter.status,
            'is_online': is_online,
            'last_reading': MeterReadingSerializer(latest_reading).data,
            'active_alerts': meter.alerts.filter(status='active').count()
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get overall meter statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_meters': queryset.count(),
            'active_meters': queryset.filter(status='active').count(),
            'inactive_meters': queryset.filter(status='inactive').count(),
            'faulty_meters': queryset.filter(status='faulty').count(),
            'by_type': queryset.values('meter_type').annotate(count=Count('id'))
        }
        
        return Response(stats)


class MeterReadingViewSet(viewsets.ModelViewSet):
    """ViewSet for MeterReading operations"""
    
    serializer_class = MeterReadingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'farmer':
            return MeterReading.objects.filter(meter__user=user)
        elif user.role == 'sarpanch':
            return MeterReading.objects.filter(meter__user__village=user.village)
        elif user.role in ['utility', 'government']:
            return MeterReading.objects.all()
        
        return MeterReading.objects.none()
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create meter readings"""
        serializer = MeterReadingBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        readings = serializer.save()
        
        return Response({
            'message': f'{len(readings)} readings created successfully',
            'count': len(readings)
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def anomalies(self, request):
        """Get anomaly readings"""
        queryset = self.get_queryset().filter(is_anomaly=True)
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet for Alert operations"""
    
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'farmer':
            return Alert.objects.filter(meter__user=user)
        elif user.role == 'sarpanch':
            return Alert.objects.filter(meter__user__village=user.village)
        elif user.role in ['utility', 'government']:
            return Alert.objects.all()
        
        return Alert.objects.none()
    
    def list(self, request, *args, **kwargs):
        """List alerts with optional filters"""
        queryset = self.get_queryset()
        
        # Filter by status
        alert_status = request.query_params.get('status')
        if alert_status:
            queryset = queryset.filter(status=alert_status)
        
        # Filter by severity
        severity = request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by alert type
        alert_type = request.query_params.get('alert_type')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        # Filter by meter
        meter_id = request.query_params.get('meter_id')
        if meter_id:
            queryset = queryset.filter(meter__meter_id=meter_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        alert.status = 'acknowledged'
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_acknowledge(self, request):
        """Bulk acknowledge alerts"""
        serializer = AlertAcknowledgeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        alert_ids = serializer.validated_data['alert_ids']
        updated = Alert.objects.filter(id__in=alert_ids).update(
            status='acknowledged',
            acknowledged_at=timezone.now()
        )
        
        return Response({
            'message': f'{updated} alerts acknowledged',
            'count': updated
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get alert statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'active': queryset.filter(status='active').count(),
            'acknowledged': queryset.filter(status='acknowledged').count(),
            'resolved': queryset.filter(status='resolved').count(),
            'by_severity': queryset.values('severity').annotate(count=Count('id')),
            'by_type': queryset.values('alert_type').annotate(count=Count('id')),
            'critical_count': queryset.filter(severity='critical', status='active').count()
        }
        
        return Response(stats)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Notification operations (read-only)"""
    
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.read_at = timezone.now()
        notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        updated = self.get_queryset().filter(read_at__isnull=True).update(
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'{updated} notifications marked as read',
            'count': updated
        })


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet for dashboard data"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get dashboard statistics"""
        user = request.user
        
        # Get user's meters
        if user.role == 'farmer':
            meters = Meter.objects.filter(user=user)
        elif user.role == 'sarpanch':
            meters = Meter.objects.filter(user__village=user.village)
        else:
            meters = Meter.objects.all()
        
        # Calculate statistics
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Get today's readings
        today_readings = MeterReading.objects.filter(
            meter__in=meters,
            timestamp__date=today
        )
        
        # Get month's readings
        month_readings = MeterReading.objects.filter(
            meter__in=meters,
            timestamp__date__gte=start_of_month
        )
        
        # Calculate aggregates
        total_energy = month_readings.aggregate(Sum('energy'))['energy__sum'] or 0
        avg_power = today_readings.aggregate(Avg('power'))['power__avg'] or 0
        avg_voltage = today_readings.aggregate(Avg('voltage'))['voltage__avg'] or 0
        avg_current = today_readings.aggregate(Avg('current'))['current__avg'] or 0
        avg_pf = today_readings.aggregate(Avg('power_factor'))['power_factor__avg'] or 0.95
        
        # Get active alerts
        active_alerts = Alert.objects.filter(
            meter__in=meters,
            status='active'
        ).count()
        
        # Mock calculations (replace with actual logic)
        efficiency_score = min(100, int((avg_pf * 100) * 0.7 + 30))
        monthly_cost = total_energy * 7.5  # ₹7.5 per unit
        cost_savings = monthly_cost * 0.15  # 15% savings
        carbon_saved = total_energy * 0.82 * 0.15  # 15% reduction
        
        stats = {
            'total_energy': round(total_energy, 2),
            'current_power': round(avg_power, 2),
            'efficiency_score': efficiency_score,
            'active_alerts': active_alerts,
            'monthly_cost': round(monthly_cost, 2),
            'cost_savings': round(cost_savings, 2),
            'carbon_saved': round(carbon_saved, 2),
            'voltage': round(avg_voltage, 2),
            'current': round(avg_current, 2),
            'power_factor': round(avg_pf, 2)
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)
