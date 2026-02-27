"""
URL Configuration for Distribution API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet, basename='company')
router.register(r'districts', views.DistrictViewSet, basename='district')
router.register(r'villages', views.VillageViewSet, basename='village')
router.register(r'transformers', views.TransformerViewSet, basename='transformer')
router.register(r'houses', views.HouseViewSet, basename='house')
router.register(r'readings', views.ElectricityReadingViewSet, basename='reading')
router.register(r'alerts', views.LossAlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DistributionDashboardView.as_view(), name='distribution-dashboard'),
    path('simulator/run/', views.SimulatorAPIView.as_view(), name='run-simulator'),
]
