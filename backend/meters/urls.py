from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, MeterViewSet, MeterReadingViewSet,
    AlertViewSet, NotificationViewSet, DashboardViewSet
)
from .mobile_auth_views import (
    SignupRequestView, SignupVerifyView,
    MobileLoginRequestView, MobileLoginVerifyView,
    LogoutView, SessionListView, resend_otp
)
from .drf_auth_views import verify_token, auth_status, TokenRefreshAPIView
from .admin_views import AdminLoginView, VillageDataView, VillageDataStreamView
from .test_views import test_sms, test_alert, sms_config_status

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'meters', MeterViewSet, basename='meter')
router.register(r'readings', MeterReadingViewSet, basename='reading')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    # Mobile-Only Authentication with Session Management
    path('auth/signup/request/', SignupRequestView.as_view(), name='signup_request'),
    path('auth/signup/verify/', SignupVerifyView.as_view(), name='signup_verify'),
    path('auth/login/request/', MobileLoginRequestView.as_view(), name='mobile_login_request'),
    path('auth/login/verify/', MobileLoginVerifyView.as_view(), name='mobile_login_verify'),
    path('auth/otp/resend/', resend_otp, name='resend_otp'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/sessions/', SessionListView.as_view(), name='session_list'),
    
    # Token & Status Endpoints
    path('auth/token/refresh/', TokenRefreshAPIView.as_view(), name='token_refresh'),
    path('auth/verify/', verify_token, name='verify_token'),
    path('auth/status/', auth_status, name='auth_status'),
    
    # Admin Panel Endpoints (Village Grid Monitoring)
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin/villagedata/', VillageDataView.as_view(), name='admin_village_data'),
    path('admin/villagedata/stream/', VillageDataStreamView.as_view(), name='admin_village_stream'),
    
    # Test Endpoints (SMS & Alerts)
    path('test/sms/', test_sms, name='test_sms'),
    path('test/alert/', test_alert, name='test_alert'),
    path('test/sms-status/', sms_config_status, name='sms_config_status'),
    
    # API Routes
    path('', include(router.urls)),
]
