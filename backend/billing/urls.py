"""
Billing URL Configuration
"""

from django.urls import path
from .views import BillingViewSet, SubscriptionViewSet

urlpatterns = [
    # Billing summary and management
    path('summary/', BillingViewSet.as_view({'get': 'summary'}), name='billing-summary'),
    path('bills/', BillingViewSet.as_view({'get': 'bills'}), name='billing-bills'),
    path('bills/<int:pk>/', BillingViewSet.as_view({'get': 'bill_detail'}), name='bill-detail'),
    path('invoices/', BillingViewSet.as_view({'get': 'invoices'}), name='billing-invoices'),
    path('invoices/<int:pk>/', BillingViewSet.as_view({'get': 'invoice_detail'}), name='invoice-detail'),
    
    # Bill operations
    path('generate_bill/', BillingViewSet.as_view({'post': 'generate_bill'}), name='generate-bill'),
    path('pay_bill/', BillingViewSet.as_view({'post': 'pay_bill'}), name='pay-bill'),
    path('calculate_estimate/', BillingViewSet.as_view({'get': 'calculate_estimate'}), name='calculate-estimate'),
    
    # Payments and tariffs
    path('payments/', BillingViewSet.as_view({'get': 'payments'}), name='billing-payments'),
    path('tariffs/', BillingViewSet.as_view({'get': 'tariffs'}), name='billing-tariffs'),
    
    # Subscriptions
    path('subscriptions/', SubscriptionViewSet.as_view({'get': 'list'}), name='subscriptions-list'),
    path('subscriptions/my_subscription/', SubscriptionViewSet.as_view({'get': 'my_subscription'}), name='my-subscription'),
    path('subscriptions/<int:pk>/subscribe/', SubscriptionViewSet.as_view({'post': 'subscribe'}), name='subscribe'),
]
