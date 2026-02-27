"""
Billing Views - API endpoints for billing, invoices, and payments
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid

from .models import Subscription, UserSubscription, Invoice, Bill, Payment, TariffRate
from .serializers import (
    SubscriptionSerializer, UserSubscriptionSerializer,
    InvoiceSerializer, BillSerializer, PaymentSerializer,
    TariffRateSerializer, BillingSummarySerializer
)
from meters.models import Meter
import logging

logger = logging.getLogger(__name__)


class BillingViewSet(viewsets.ViewSet):
    """
    ViewSet for billing and invoice management
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get billing summary
        GET /api/v1/billing/summary/
        """
        user = request.user
        
        # Get all bills for user
        all_bills = Bill.objects.filter(user=user)
        paid_bills = all_bills.filter(status='paid')
        pending_bills = all_bills.filter(status='pending')
        overdue_bills = all_bills.filter(status='overdue')
        
        # Calculate amounts
        total_amount = all_bills.aggregate(total=Sum('total_amount'))['total'] or 0
        paid_amount = paid_bills.aggregate(total=Sum('total_amount'))['total'] or 0
        pending_amount = pending_bills.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Next due date
        next_bill = pending_bills.order_by('due_date').first()
        next_due_date = next_bill.due_date if next_bill else None
        
        # Subscription status
        subscription = UserSubscription.objects.filter(user=user, status='active').first()
        subscription_status = 'active' if subscription and subscription.is_valid() else 'inactive'
        
        data = {
            'total_bills': all_bills.count(),
            'paid_bills': paid_bills.count(),
            'pending_bills': pending_bills.count(),
            'overdue_bills': overdue_bills.count(),
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'pending_amount': pending_amount,
            'next_due_date': next_due_date,
            'subscription_status': subscription_status
        }
        
        serializer = BillingSummarySerializer(data)
        return Response({
            'success': True,
            'summary': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def bills(self, request):
        """
        Get all bills for user
        GET /api/v1/billing/bills/?status=pending&meter_id=GJ-ANAND-001
        """
        user = request.user
        bill_status = request.query_params.get('status')
        meter_id = request.query_params.get('meter_id')
        
        bills = Bill.objects.filter(user=user)
        
        if bill_status:
            bills = bills.filter(status=bill_status)
        
        if meter_id:
            bills = bills.filter(meter__meter_id=meter_id)
        
        bills = bills.order_by('-created_at')
        
        serializer = BillSerializer(bills, many=True)
        return Response({
            'success': True,
            'count': bills.count(),
            'bills': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def bill_detail(self, request, pk=None):
        """
        Get bill details
        GET /api/v1/billing/bills/{id}/
        """
        try:
            bill = Bill.objects.get(pk=pk, user=request.user)
            serializer = BillSerializer(bill)
            return Response({
                'success': True,
                'bill': serializer.data
            })
        except Bill.DoesNotExist:
            return Response(
                {'error': 'Bill not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def invoices(self, request):
        """
        Get all invoices for user
        GET /api/v1/billing/invoices/?status=pending
        """
        user = request.user
        invoice_status = request.query_params.get('status')
        
        invoices = Invoice.objects.filter(user=user)
        
        if invoice_status:
            invoices = invoices.filter(status=invoice_status)
        
        invoices = invoices.order_by('-created_at')
        
        serializer = InvoiceSerializer(invoices, many=True)
        return Response({
            'success': True,
            'count': invoices.count(),
            'invoices': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def invoice_detail(self, request, pk=None):
        """
        Get invoice details
        GET /api/v1/billing/invoices/{id}/
        """
        try:
            invoice = Invoice.objects.get(pk=pk, user=request.user)
            serializer = InvoiceSerializer(invoice)
            return Response({
                'success': True,
                'invoice': serializer.data
            })
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def generate_bill(self, request):
        """
        Generate monthly bill for meter
        POST /api/v1/billing/generate_bill/
        Body: {"meter_id": "GJ-ANAND-001"}
        """
        meter_id = request.data.get('meter_id')
        
        if not meter_id:
            return Response(
                {'error': 'meter_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            meter = Meter.objects.get(meter_id=meter_id, user=request.user)
        except Meter.DoesNotExist:
            return Response(
                {'error': 'Meter not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get current month readings
        today = timezone.now().date()
        period_start = today.replace(day=1)
        
        # Get readings
        from meters.models import MeterReading
        readings = MeterReading.objects.filter(
            meter=meter,
            timestamp__date__gte=period_start,
            timestamp__date__lte=today
        )
        
        if not readings.exists():
            return Response(
                {'error': 'No readings found for current period'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate consumption
        first_reading = readings.order_by('timestamp').first()
        last_reading = readings.order_by('timestamp').last()
        
        previous_reading = first_reading.energy_kwh
        current_reading = last_reading.energy_kwh
        units_consumed = current_reading - previous_reading
        
        # Generate bill number
        bill_number = f"BILL-{meter.meter_id}-{today.strftime('%Y%m')}"
        
        # Check if bill already exists
        if Bill.objects.filter(bill_number=bill_number).exists():
            return Response(
                {'error': 'Bill for this period already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create bill
        bill = Bill.objects.create(
            bill_number=bill_number,
            user=request.user,
            meter=meter,
            billing_period_start=period_start,
            billing_period_end=today,
            previous_reading=previous_reading,
            current_reading=current_reading,
            base_charge=Decimal('50.00'),  # Fixed charge
            due_date=today + timedelta(days=15)
        )
        
        # Calculate charges
        bill.calculate_charges()
        bill.save()
        
        serializer = BillSerializer(bill)
        return Response({
            'success': True,
            'message': 'Bill generated successfully',
            'bill': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def pay_bill(self, request):
        """
        Process bill payment
        POST /api/v1/billing/pay_bill/
        Body: {"bill_id": 1, "payment_method": "upi", "transaction_id": "..."}
        """
        bill_id = request.data.get('bill_id')
        payment_method = request.data.get('payment_method', 'upi')
        gateway_transaction_id = request.data.get('transaction_id', '')
        
        if not bill_id:
            return Response(
                {'error': 'bill_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            bill = Bill.objects.get(pk=bill_id, user=request.user)
        except Bill.DoesNotExist:
            return Response(
                {'error': 'Bill not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if bill.status == 'paid':
            return Response(
                {'error': 'Bill already paid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark bill as paid
        bill.status = 'paid'
        bill.save()
        
        return Response({
            'success': True,
            'message': 'Payment successful',
            'bill_number': bill.bill_number,
            'amount_paid': float(bill.total_amount)
        })
    
    @action(detail=False, methods=['get'])
    def payments(self, request):
        """
        Get payment history
        GET /api/v1/billing/payments/
        """
        payments = Payment.objects.filter(user=request.user).order_by('-created_at')
        serializer = PaymentSerializer(payments, many=True)
        
        return Response({
            'success': True,
            'count': payments.count(),
            'payments': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def tariffs(self, request):
        """
        Get tariff rates
        GET /api/v1/billing/tariffs/?category=domestic&state=Gujarat
        """
        category = request.query_params.get('category', 'domestic')
        state = request.query_params.get('state', 'Gujarat')
        
        tariffs = TariffRate.objects.filter(
            category=category,
            state=state,
            is_active=True
        ).order_by('slab_min')
        
        serializer = TariffRateSerializer(tariffs, many=True)
        
        return Response({
            'success': True,
            'category': category,
            'state': state,
            'tariffs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def calculate_estimate(self, request):
        """
        Calculate bill estimate
        GET /api/v1/billing/calculate_estimate/?units=150
        """
        units = float(request.query_params.get('units', 0))
        
        if units <= 0:
            return Response(
                {'error': 'Invalid units'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simple calculation using average rate
        rate_per_unit = Decimal('6.00')
        base_charge = Decimal('50.00')
        energy_charge = Decimal(str(units)) * rate_per_unit
        tax = energy_charge * Decimal('0.05')
        total = base_charge + energy_charge + tax
        
        return Response({
            'success': True,
            'units_consumed': units,
            'base_charge': float(base_charge),
            'energy_charge': float(energy_charge),
            'tax': float(tax),
            'total_amount': float(total),
            'rate_per_unit': float(rate_per_unit)
        })


class SubscriptionViewSet(viewsets.ViewSet):
    """
    ViewSet for subscription management
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        Get all subscription plans
        GET /api/v1/billing/subscriptions/
        """
        subscriptions = Subscription.objects.filter(is_active=True)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        
        return Response({
            'success': True,
            'subscriptions': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def my_subscription(self, request):
        """
        Get user's current subscription
        GET /api/v1/billing/subscriptions/my_subscription/
        """
        subscription = UserSubscription.objects.filter(
            user=request.user,
            status='active'
        ).order_by('-start_date').first()
        
        if not subscription:
            return Response({
                'success': True,
                'message': 'No active subscription',
                'subscription': None
            })
        
        serializer = UserSubscriptionSerializer(subscription)
        return Response({
            'success': True,
            'subscription': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """
        Subscribe to a plan
        POST /api/v1/billing/subscriptions/{id}/subscribe/
        """
        try:
            subscription = Subscription.objects.get(pk=pk, is_active=True)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'Subscription plan not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user already has active subscription
        existing = UserSubscription.objects.filter(
            user=request.user,
            status='active'
        ).first()
        
        if existing and existing.is_valid():
            return Response(
                {'error': 'You already have an active subscription'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new subscription
        start_date = timezone.now()
        if subscription.billing_cycle == 'monthly':
            end_date = start_date + timedelta(days=30)
        elif subscription.billing_cycle == 'quarterly':
            end_date = start_date + timedelta(days=90)
        else:  # yearly
            end_date = start_date + timedelta(days=365)
        
        user_subscription = UserSubscription.objects.create(
            user=request.user,
            subscription=subscription,
            status='active',
            start_date=start_date,
            end_date=end_date,
            auto_renew=True
        )
        
        serializer = UserSubscriptionSerializer(user_subscription)
        return Response({
            'success': True,
            'message': 'Subscription activated successfully',
            'subscription': serializer.data
        }, status=status.HTTP_201_CREATED)

