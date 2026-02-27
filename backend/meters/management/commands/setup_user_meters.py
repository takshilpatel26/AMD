"""
Setup user meters with sample readings, alerts, and analytics data.
Links each user to their dedicated meter with personalized data.
"""

import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from meters.models import User, Meter, MeterReading, Alert
from analytics.models import EfficiencyScore, CarbonImpact, ConsumptionPattern


class Command(BaseCommand):
    help = 'Setup meters for users with sample readings and alerts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours of historical data to generate'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Specific username to setup (default: all users without meters)'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        username = options.get('username')
        
        if username:
            users = User.objects.filter(username=username)
        else:
            # Get users that don't have meters yet
            users = User.objects.filter(meters__isnull=True)
        
        if not users.exists():
            # If all users have meters, get all users
            if username:
                self.stdout.write(self.style.WARNING(f'User {username} not found'))
                return
            users = User.objects.all()
        
        self.stdout.write(f'Setting up meters for {users.count()} users with {hours} hours of data...')
        
        for user in users:
            meter = self.create_or_get_meter(user)
            readings_count = self.generate_readings(meter, hours)
            alerts_count = self.generate_alerts(meter)
            analytics_count = self.generate_analytics(meter, hours)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ {user.username}: Meter {meter.meter_id}, '
                    f'{readings_count} readings, {alerts_count} alerts, '
                    f'{analytics_count} analytics days'
                )
            )
        
        self.stdout.write(self.style.SUCCESS('\n✓ User meter setup complete!'))

    def create_or_get_meter(self, user):
        """Create a meter for the user if they don't have one"""
        meter = user.meters.first()
        if meter:
            return meter
        
        # Generate unique meter ID
        meter_id = f"GM-{user.username.upper()[:6]}-{random.randint(1000, 9999)}"
        
        # Determine meter type based on user role
        meter_types = {
            'farmer': 'agricultural',
            'sarpanch': 'residential',
            'utility': 'commercial',
            'government': 'commercial',
        }
        meter_type = meter_types.get(user.role, 'residential')
        
        # Create meter
        meter = Meter.objects.create(
            meter_id=meter_id,
            user=user,
            meter_type=meter_type,
            manufacturer='Gram Energy Systems',
            model_number='GES-SM-2024',
            installation_date=timezone.now().date() - timedelta(days=random.randint(30, 365)),
            status='active',
            location=f"{user.village or 'Village'}, {user.district or 'District'}, {user.state}",
            latitude=Decimal(str(round(random.uniform(21.5, 24.5), 6))),
            longitude=Decimal(str(round(random.uniform(69.5, 74.5), 6))),
            rated_voltage=230.0,
            rated_current=40.0,
        )
        
        return meter

    def generate_readings(self, meter, hours):
        """Generate realistic meter readings"""
        # Delete old readings for fresh data
        meter.readings.all().delete()
        
        readings = []
        now = timezone.now()
        
        # Base values for this meter
        base_voltage = random.uniform(225, 235)
        base_load = random.uniform(0.5, 3.0)  # kW
        cumulative_energy = random.uniform(100, 1000)  # Starting kWh
        
        for i in range(hours * 6):  # Reading every 10 minutes
            timestamp = now - timedelta(minutes=i * 10)
            hour = timestamp.hour
            
            # Time-of-day load pattern
            if 6 <= hour <= 9:  # Morning peak
                load_factor = random.uniform(1.2, 1.5)
            elif 18 <= hour <= 22:  # Evening peak
                load_factor = random.uniform(1.4, 1.8)
            elif 0 <= hour <= 5:  # Night - low
                load_factor = random.uniform(0.2, 0.4)
            else:  # Normal hours
                load_factor = random.uniform(0.7, 1.1)
            
            # Calculate values
            voltage = base_voltage + random.uniform(-5, 5)
            power = base_load * load_factor * 1000  # Watts
            current = power / voltage if voltage > 0 else 0
            power_factor = random.uniform(0.85, 0.98)
            energy_increment = power / 1000 / 6  # kWh for 10 minutes
            cumulative_energy += energy_increment
            
            # Determine if anomaly
            is_anomaly = False
            anomaly_type = ''
            
            # Random anomaly injection (5% chance)
            if random.random() < 0.05:
                anomaly_roll = random.random()
                if anomaly_roll < 0.3:
                    voltage = voltage * random.uniform(0.85, 0.92)  # Voltage drop
                    is_anomaly = True
                    anomaly_type = 'voltage_drop'
                elif anomaly_roll < 0.5:
                    voltage = voltage * random.uniform(1.08, 1.15)  # Voltage spike
                    is_anomaly = True
                    anomaly_type = 'voltage_spike'
                elif anomaly_roll < 0.7:
                    current = current * random.uniform(1.5, 2.0)  # Overcurrent
                    is_anomaly = True
                    anomaly_type = 'overcurrent'
                else:
                    power = base_load * 0.3 * 1000  # Phantom load (unusual low)
                    is_anomaly = True
                    anomaly_type = 'phantom_load'
            
            reading = MeterReading(
                meter=meter,
                timestamp=timestamp,
                voltage=round(voltage, 2),
                current=round(current, 3),
                power=round(power, 2),
                energy=round(cumulative_energy, 3),
                power_factor=round(power_factor, 3),
                frequency=round(random.uniform(49.8, 50.2), 2),
                temperature=round(random.uniform(25, 45), 1),
                is_anomaly=is_anomaly,
                anomaly_type=anomaly_type,
            )
            readings.append(reading)
        
        # Bulk create
        MeterReading.objects.bulk_create(readings)
        return len(readings)

    def generate_alerts(self, meter):
        """Generate alerts based on anomalous readings"""
        # Delete old alerts
        meter.alerts.all().delete()
        
        # Get anomalous readings
        anomalous_readings = meter.readings.filter(is_anomaly=True).order_by('-timestamp')[:20]
        
        alerts = []
        alert_templates = {
            'voltage_drop': {
                'title': '⚡ Low Voltage Detected',
                'message': 'Voltage dropped below safe threshold. This may indicate power supply issues or excessive load on the line.',
                'severity': 'warning',
            },
            'voltage_spike': {
                'title': '⚡ Voltage Spike Alert',
                'message': 'Sudden voltage increase detected. Unplug sensitive electronics immediately.',
                'severity': 'critical',
            },
            'overcurrent': {
                'title': '🔥 Overcurrent Warning',
                'message': 'Current draw exceeds normal levels. Check for short circuits or overloaded appliances.',
                'severity': 'critical',
            },
            'phantom_load': {
                'title': '👻 Unusual Load Pattern',
                'message': 'Unexpected power consumption detected. May indicate meter tampering or faulty equipment.',
                'severity': 'warning',
            },
        }
        
        for reading in anomalous_readings:
            if reading.anomaly_type and reading.anomaly_type in alert_templates:
                template = alert_templates[reading.anomaly_type]
                
                alert = Alert(
                    meter=meter,
                    reading=reading,
                    alert_type=reading.anomaly_type,
                    severity=template['severity'],
                    status='active',
                    title=template['title'],
                    message=f"{template['message']} Recorded at {reading.timestamp.strftime('%H:%M on %d %b')}. "
                            f"Voltage: {reading.voltage}V, Current: {reading.current}A",
                    recommended_action='Please check your electrical connections and contact support if issue persists.',
                    estimated_cost_impact=Decimal(str(round(random.uniform(50, 500), 2))),
                    created_at=reading.timestamp,
                )
                alerts.append(alert)
        
        # Add some additional random alerts
        alert_types = ['high_consumption', 'billing_alert']
        for _ in range(random.randint(2, 5)):
            alert_type = random.choice(alert_types)
            
            if alert_type == 'high_consumption':
                alert = Alert(
                    meter=meter,
                    alert_type=alert_type,
                    severity='info',
                    status='active',
                    title='📈 Higher Than Usual Consumption',
                    message='Your consumption this week is 15% higher than your average. Consider checking for energy-wasting appliances.',
                    recommended_action='Review usage patterns and turn off unused devices.',
                    estimated_cost_impact=Decimal(str(round(random.uniform(100, 300), 2))),
                )
            else:
                alert = Alert(
                    meter=meter,
                    alert_type=alert_type,
                    severity='info',
                    status='active',
                    title='💰 Bill Estimate Available',
                    message='Your estimated bill for this cycle is ready. Review your consumption breakdown.',
                    recommended_action='Check the billing section for detailed breakdown.',
                )
            alerts.append(alert)
        
        Alert.objects.bulk_create(alerts)
        return len(alerts)

    def generate_analytics(self, meter, hours):
        """Generate analytics data for the meter"""
        days = max(hours // 24, 7)  # At least 7 days
        now = timezone.now()
        
        # Clear old analytics data
        meter.efficiency_scores.all().delete()
        CarbonImpact.objects.filter(meter=meter).delete()
        ConsumptionPattern.objects.filter(meter=meter).delete()
        
        # Generate EfficiencyScore for each day
        efficiency_scores = []
        carbon_impacts = []
        
        for day_offset in range(days):
            date = (now - timedelta(days=day_offset)).date()
            
            # Efficiency Score
            base_score = random.randint(70, 95)
            efficiency_scores.append(EfficiencyScore(
                meter=meter,
                date=date,
                score=base_score,
                power_factor_score=random.randint(80, 98),
                load_profile_score=random.randint(65, 95),
                peak_usage_score=random.randint(60, 90),
                consistency_score=random.randint(75, 95),
                total_energy=round(random.uniform(15, 45), 2),
                optimal_energy=round(random.uniform(12, 35), 2),
                wasted_energy=round(random.uniform(2, 10), 2),
            ))
            
            # Carbon Impact
            total_energy = random.uniform(15, 45)
            carbon_per_kwh = 0.85  # kg CO2 per kWh (India average)
            carbon_impacts.append(CarbonImpact(
                meter=meter,
                date=date,
                energy_consumed=round(total_energy, 2),
                carbon_emitted=round(total_energy * carbon_per_kwh, 2),
                carbon_saved=round(random.uniform(0.5, 3), 2),
                trees_equivalent=round(total_energy * carbon_per_kwh / 21.77, 2),
                renewable_energy_used=round(random.uniform(0, 5), 2),
                renewable_percentage=round(random.uniform(0, 15), 1),
            ))
        
        EfficiencyScore.objects.bulk_create(efficiency_scores)
        CarbonImpact.objects.bulk_create(carbon_impacts)
        
        # Generate weekly consumption pattern
        ConsumptionPattern.objects.create(
            meter=meter,
            pattern_type='weekly',
            period_start=(now - timedelta(days=7)).date(),
            period_end=now.date(),
            total_energy=round(random.uniform(100, 300), 2),
            avg_power=round(random.uniform(800, 2500), 2),
            peak_power=round(random.uniform(3000, 5000), 2),
            peak_time=timezone.now().replace(hour=random.choice([9, 19, 20]), minute=0).time(),
            off_peak_energy=round(random.uniform(20, 60), 2),
            efficiency_score=round(random.uniform(75, 92), 1),
            power_factor_avg=round(random.uniform(0.88, 0.97), 2),
            estimated_cost=Decimal(str(round(random.uniform(500, 2000), 2))),
            potential_savings=Decimal(str(round(random.uniform(50, 300), 2))),
            insights={
                'peak_hours': ['18:00-22:00'],
                'high_usage_days': ['Monday', 'Friday'],
                'trend': 'stable'
            },
            recommendations=[
                'Consider shifting irrigation to off-peak hours',
                'Your power factor is good, maintain it',
                'LED lighting can reduce consumption by 10%'
            ]
        )
        
        return days
