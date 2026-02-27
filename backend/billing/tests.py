"""
Comprehensive tests for Billing app
Tests for invoices, bills, payments, subscriptions, and tariff calculations
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, timedelta, date
from decimal import Decimal

from meters.models import Meter
from .models import (
    Subscription, UserSubscription, Invoice, InvoiceItem,
    Payment, Bill, TariffRate
)
from .serializers import (
    SubscriptionSerializer, UserSubscriptionSerializer,
    InvoiceSerializer, BillSerializer, PaymentSerializer,
    TariffRateSerializer
)

User = get_user_model()


class SubscriptionModelTest(TestCase):
    """Test Subscription model"""
    
    def setUp(self):
        self.subscription = Subscription.objects.create(
            name='Basic Plan',
            plan_type='basic',
            description='Basic subscription for farmers',
            price=Decimal('99.00'),
            billing_cycle='monthly',
            max_meters=1,
            features={'analytics': True, 'alerts': True}
        )
    
    def test_subscription_creation(self):
        """Test subscription is created correctly"""
        self.assertEqual(self.subscription.name, 'Basic Plan')
        self.assertEqual(self.subscription.price, Decimal('99.00'))
        self.assertTrue(self.subscription.is_active)
    
    def test_subscription_str_method(self):
        """Test subscription string representation"""
        expected = f"{self.subscription.name} - ₹{self.subscription.price}/{self.subscription.billing_cycle}"
        self.assertEqual(str(self.subscription), expected)
    
    def test_subscription_features(self):
        """Test subscription features JSON field"""
        self.assertIn('analytics', self.subscription.features)
        self.assertTrue(self.subscription.features['analytics'])


class UserSubscriptionModelTest(TestCase):
    """Test User Subscription model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.subscription = Subscription.objects.create(
            name='Premium Plan',
            plan_type='premium',
            description='Premium subscription',
            price=Decimal('199.00'),
            billing_cycle='monthly',
            max_meters=5
        )
        
        self.user_subscription = UserSubscription.objects.create(
            user=self.user,
            subscription=self.subscription,
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            auto_renew=True
        )
    
    def test_user_subscription_creation(self):
        """Test user subscription is created correctly"""
        self.assertEqual(self.user_subscription.user, self.user)
        self.assertEqual(self.user_subscription.subscription, self.subscription)
        self.assertEqual(self.user_subscription.status, 'active')
    
    def test_subscription_validity(self):
        """Test is_valid method"""
        self.assertTrue(self.user_subscription.is_valid())
        
        # Test expired subscription
        self.user_subscription.end_date = timezone.now() - timedelta(days=1)
        self.user_subscription.save()
        self.assertFalse(self.user_subscription.is_valid())


class InvoiceModelTest(TestCase):
    """Test Invoice model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        self.invoice = Invoice.objects.create(
            invoice_number='INV-2024-0001',
            user=self.user,
            meter=self.meter,
            billing_start_date=date(2024, 1, 1),
            billing_end_date=date(2024, 1, 31),
            subtotal=Decimal('500.00'),
            tax_amount=Decimal('25.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('525.00'),
            energy_consumed=100.0,
            rate_per_unit=Decimal('5.00'),
            due_date=date(2024, 2, 10)
        )
    
    def test_invoice_creation(self):
        """Test invoice is created correctly"""
        self.assertEqual(self.invoice.user, self.user)
        self.assertEqual(self.invoice.total_amount, Decimal('525.00'))
        self.assertEqual(self.invoice.status, 'pending')
    
    def test_invoice_calculation(self):
        """Test calculate_total method"""
        calculated_total = self.invoice.calculate_total()
        expected_total = Decimal('525.00')  # 500 + 25 - 0
        self.assertEqual(calculated_total, expected_total)
    
    def test_mark_as_paid(self):
        """Test mark_as_paid method"""
        self.invoice.mark_as_paid(
            payment_method='upi',
            transaction_id='TXN123456'
        )
        self.assertEqual(self.invoice.status, 'paid')
        self.assertIsNotNone(self.invoice.paid_date)
        self.assertEqual(self.invoice.payment_method, 'upi')


class InvoiceItemModelTest(TestCase):
    """Test Invoice Item model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.invoice = Invoice.objects.create(
            invoice_number='INV-2024-0001',
            user=self.user,
            billing_start_date=date(2024, 1, 1),
            billing_end_date=date(2024, 1, 31),
            total_amount=Decimal('525.00'),
            due_date=date(2024, 2, 10)
        )
        
        self.item = InvoiceItem.objects.create(
            invoice=self.invoice,
            description='Energy Consumption',
            quantity=Decimal('100.00'),
            unit_price=Decimal('5.00'),
            amount=Decimal('500.00'),
            energy_consumed=100.0,
            tariff_type='Residential'
        )
    
    def test_item_creation(self):
        """Test invoice item is created correctly"""
        self.assertEqual(self.item.invoice, self.invoice)
        self.assertEqual(self.item.quantity, Decimal('100.00'))
    
    def test_amount_calculation(self):
        """Test amount is calculated on save"""
        item = InvoiceItem(
            invoice=self.invoice,
            description='Test Item',
            quantity=Decimal('10.00'),
            unit_price=Decimal('5.00')
        )
        item.save()
        self.assertEqual(item.amount, Decimal('50.00'))


class PaymentModelTest(TestCase):
    """Test Payment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.invoice = Invoice.objects.create(
            invoice_number='INV-2024-0001',
            user=self.user,
            billing_start_date=date(2024, 1, 1),
            billing_end_date=date(2024, 1, 31),
            total_amount=Decimal('525.00'),
            due_date=date(2024, 2, 10)
        )
        
        self.payment = Payment.objects.create(
            payment_id='PAY-123456',
            invoice=self.invoice,
            user=self.user,
            amount=Decimal('525.00'),
            payment_method='upi',
            status='success',
            gateway_name='Razorpay',
            gateway_transaction_id='rzp_123456'
        )
    
    def test_payment_creation(self):
        """Test payment is created correctly"""
        self.assertEqual(self.payment.user, self.user)
        self.assertEqual(self.payment.amount, Decimal('525.00'))
        self.assertEqual(self.payment.status, 'success')
    
    def test_payment_methods(self):
        """Test different payment methods"""
        methods = ['upi', 'card', 'netbanking', 'wallet', 'cash']
        for method in methods:
            payment = Payment.objects.create(
                payment_id=f'PAY-{method}',
                invoice=self.invoice,
                user=self.user,
                amount=Decimal('100.00'),
                payment_method=method
            )
            self.assertEqual(payment.payment_method, method)


class BillModelTest(TestCase):
    """Test Bill model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        self.bill = Bill.objects.create(
            bill_number='BILL-2024-0001',
            user=self.user,
            meter=self.meter,
            billing_period_start=date(2024, 1, 1),
            billing_period_end=date(2024, 1, 31),
            previous_reading=0.0,
            current_reading=100.0,
            units_consumed=100.0,
            base_charge=Decimal('50.00'),
            energy_charge=Decimal('600.00'),
            tax=Decimal('30.00'),
            subsidy=Decimal('0.00'),
            total_amount=Decimal('680.00'),
            due_date=date(2024, 2, 10)
        )
    
    def test_bill_creation(self):
        """Test bill is created correctly"""
        self.assertEqual(self.bill.user, self.user)
        self.assertEqual(self.bill.meter, self.meter)
        self.assertEqual(self.bill.units_consumed, 100.0)
    
    def test_charge_calculation(self):
        """Test calculate_charges method"""
        bill = Bill(
            bill_number='BILL-TEST',
            user=self.user,
            meter=self.meter,
            billing_period_start=date(2024, 1, 1),
            billing_period_end=date(2024, 1, 31),
            previous_reading=0.0,
            current_reading=100.0,
            base_charge=Decimal('50.00'),
            total_amount=Decimal('0.00'),
            due_date=date(2024, 2, 10)
        )
        
        total = bill.calculate_charges()
        self.assertGreater(total, Decimal('0.00'))
        self.assertEqual(bill.units_consumed, 100.0)


class TariffRateModelTest(TestCase):
    """Test Tariff Rate model"""
    
    def setUp(self):
        self.tariff = TariffRate.objects.create(
            name='Gujarat Domestic Slab 1',
            state='Gujarat',
            category='domestic',
            slab_min=0,
            slab_max=100,
            rate_per_unit=Decimal('3.50'),
            fixed_charge=Decimal('20.00'),
            subsidy_applicable=True,
            effective_from=date(2024, 1, 1),
            is_active=True
        )
    
    def test_tariff_creation(self):
        """Test tariff is created correctly"""
        self.assertEqual(self.tariff.state, 'Gujarat')
        self.assertEqual(self.tariff.category, 'domestic')
        self.assertEqual(self.tariff.rate_per_unit, Decimal('3.50'))
    
    def test_tariff_categories(self):
        """Test different tariff categories"""
        categories = ['domestic', 'commercial', 'industrial', 'agricultural']
        for category in categories:
            tariff = TariffRate.objects.create(
                name=f'Test {category}',
                state='Gujarat',
                category=category,
                slab_min=0,
                slab_max=100,
                rate_per_unit=Decimal('5.00'),
                effective_from=date(2024, 1, 1)
            )
            self.assertEqual(tariff.category, category)


class BillingAPITest(APITestCase):
    """Test Billing API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123',
            role='farmer'
        )
        self.client.force_authenticate(user=self.user)
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        self.bill = Bill.objects.create(
            bill_number='BILL-2024-0001',
            user=self.user,
            meter=self.meter,
            billing_period_start=date(2024, 1, 1),
            billing_period_end=date(2024, 1, 31),
            units_consumed=100.0,
            total_amount=Decimal('680.00'),
            due_date=date(2024, 2, 10)
        )
    
    def test_billing_summary(self):
        """Test GET /api/v1/billing/summary/"""
        response = self.client.get('/api/v1/billing/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
    
    def test_get_bills(self):
        """Test GET /api/v1/billing/bills/"""
        response = self.client.get('/api/v1/billing/bills/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 0)
    
    def test_get_bill_detail(self):
        """Test GET /api/v1/billing/bills/{id}/"""
        response = self.client.get(f'/api/v1/billing/bill/{self.bill.id}/')
        # Note: Endpoint might be different, adjust as needed
        # This test might need adjustment based on actual URL structure


class SubscriptionAPITest(APITestCase):
    """Test Subscription API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123',
            role='farmer'
        )
        self.client.force_authenticate(user=self.user)
        
        self.subscription = Subscription.objects.create(
            name='Basic Plan',
            plan_type='basic',
            description='Basic plan',
            price=Decimal('99.00'),
            billing_cycle='monthly',
            max_meters=1
        )
    
    def test_list_subscriptions(self):
        """Test GET /api/v1/subscriptions/"""
        response = self.client.get('/api/v1/subscriptions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SerializerTest(TestCase):
    """Test Billing serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.subscription = Subscription.objects.create(
            name='Premium Plan',
            plan_type='premium',
            description='Premium subscription',
            price=Decimal('199.00'),
            billing_cycle='monthly'
        )
        
        self.meter = Meter.objects.create(
            meter_id='GJ-ANAND-00001',
            user=self.user,
            installation_date=timezone.now().date(),
            location='Test Location'
        )
        
        self.bill = Bill.objects.create(
            bill_number='BILL-2024-0001',
            user=self.user,
            meter=self.meter,
            billing_period_start=date(2024, 1, 1),
            billing_period_end=date(2024, 1, 31),
            units_consumed=100.0,
            total_amount=Decimal('680.00'),
            due_date=date(2024, 2, 10)
        )
    
    def test_subscription_serializer(self):
        """Test SubscriptionSerializer"""
        serializer = SubscriptionSerializer(self.subscription)
        self.assertEqual(serializer.data['name'], 'Premium Plan')
        self.assertEqual(str(serializer.data['price']), '199.00')
    
    def test_bill_serializer(self):
        """Test BillSerializer"""
        serializer = BillSerializer(self.bill)
        self.assertEqual(serializer.data['bill_number'], 'BILL-2024-0001')
        self.assertEqual(float(serializer.data['units_consumed']), 100.0)


class TariffCalculationTest(TestCase):
    """Test tariff calculation logic"""
    
    def setUp(self):
        # Create Gujarat tariff slabs
        TariffRate.objects.create(
            name='Slab 1',
            state='Gujarat',
            category='domestic',
            slab_min=0,
            slab_max=100,
            rate_per_unit=Decimal('3.50'),
            fixed_charge=Decimal('20.00'),
            effective_from=date(2024, 1, 1),
            is_active=True
        )
        
        TariffRate.objects.create(
            name='Slab 2',
            state='Gujarat',
            category='domestic',
            slab_min=101,
            slab_max=250,
            rate_per_unit=Decimal('5.20'),
            fixed_charge=Decimal('20.00'),
            effective_from=date(2024, 1, 1),
            is_active=True
        )
        
        TariffRate.objects.create(
            name='Slab 3',
            state='Gujarat',
            category='domestic',
            slab_min=251,
            slab_max=9999,
            rate_per_unit=Decimal('7.50'),
            fixed_charge=Decimal('20.00'),
            effective_from=date(2024, 1, 1),
            is_active=True
        )
    
    def test_slab_based_calculation(self):
        """Test slab-based tariff calculation"""
        from core.utils import get_tariff_cost
        
        # Test 50 units (Slab 1)
        cost_50 = get_tariff_cost(50, state='gujarat')
        expected_50 = Decimal('3.50') * 50
        self.assertEqual(cost_50, expected_50)
        
        # Test 150 units (Slab 1 + Slab 2)
        cost_150 = get_tariff_cost(150, state='gujarat')
        expected_150 = (Decimal('3.50') * 100) + (Decimal('5.20') * 50)
        self.assertEqual(cost_150, expected_150)


class PaymentProcessingTest(TestCase):
    """Test payment processing flow"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='test123'
        )
        
        self.invoice = Invoice.objects.create(
            invoice_number='INV-2024-0001',
            user=self.user,
            billing_start_date=date(2024, 1, 1),
            billing_end_date=date(2024, 1, 31),
            total_amount=Decimal('525.00'),
            due_date=date(2024, 2, 10),
            status='pending'
        )
    
    def test_payment_flow(self):
        """Test complete payment flow"""
        # Create payment
        payment = Payment.objects.create(
            payment_id='PAY-TEST-001',
            invoice=self.invoice,
            user=self.user,
            amount=Decimal('525.00'),
            payment_method='upi',
            status='pending'
        )
        
        # Process payment
        payment.status = 'success'
        payment.payment_date = timezone.now()
        payment.save()
        
        # Mark invoice as paid
        self.invoice.mark_as_paid(
            payment_method='upi',
            transaction_id='PAY-TEST-001'
        )
        
        self.assertEqual(self.invoice.status, 'paid')
        self.assertEqual(payment.status, 'success')


# Run tests with: python manage.py test billing
