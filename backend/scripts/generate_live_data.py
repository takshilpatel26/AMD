"""
Real-Time Meter Data Generator for Gram Meter Demo

This script simulates live smart meter readings with:
- Realistic power consumption patterns
- Voltage spikes and drops
- Phantom loads during night hours
- Overcurrent conditions
- Power outages
"""

import os
import sys
import django
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gram_meter.settings')
django.setup()

from meters.models import Meter, MeterReading, Alert, User
from django.utils import timezone
import numpy as np


class MeterDataGenerator:
    """Generate realistic meter readings"""
    
    def __init__(self, meter):
        self.meter = meter
        self.base_voltage = meter.rated_voltage  # 230V typically
        self.max_current = meter.rated_current   # 40A typically
        
        # Usage patterns by hour (0-23)
        self.hourly_load_profile = {
            0: 0.15, 1: 0.12, 2: 0.10, 3: 0.10, 4: 0.12, 5: 0.20,  # Night/Early morning
            6: 0.35, 7: 0.50, 8: 0.60, 9: 0.55, 10: 0.45, 11: 0.40,  # Morning
            12: 0.50, 13: 0.55, 14: 0.45, 15: 0.40, 16: 0.45, 17: 0.55,  # Afternoon
            18: 0.70, 19: 0.85, 20: 0.90, 21: 0.75, 22: 0.50, 23: 0.25   # Evening/Night
        }
        
        self.cumulative_energy = 0.0
        self.anomaly_chance = 0.05  # 5% chance of anomaly per reading
        
    def get_base_load(self, hour):
        """Get base load for current hour"""
        profile_factor = self.hourly_load_profile.get(hour, 0.3)
        
        # Add meter type factor
        type_factors = {
            'residential': 3000,    # 3kW average
            'commercial': 8000,     # 8kW average
            'agricultural': 12000,  # 12kW (water pump)
            'industrial': 25000     # 25kW average
        }
        
        base_power = type_factors.get(self.meter.meter_type, 3000)
        return base_power * profile_factor
    
    def generate_reading(self):
        """Generate a single meter reading"""
        now = timezone.now()
        hour = now.hour
        
        # Base power consumption
        power = self.get_base_load(hour)
        
        # Add random variation (±15%)
        power *= random.uniform(0.85, 1.15)
        
        # Voltage (normally ~230V ±5%)
        voltage = self.base_voltage * random.uniform(0.95, 1.05)
        
        # Calculate current (P = V * I * PF)
        power_factor = random.uniform(0.92, 0.98)
        current = power / (voltage * power_factor) if voltage > 0 else 0
        
        # Frequency (50Hz ±0.5Hz)
        frequency = 50.0 + random.uniform(-0.5, 0.5)
        
        # Temperature (ambient + heat from load)
        temperature = 25 + (current / self.max_current) * 15  # 25-40°C
        
        # Energy increment (kWh)
        energy_increment = (power / 1000) * (5 / 60)  # 5 minutes in hours
        self.cumulative_energy += energy_increment
        
        # Check for anomalies
        is_anomaly = False
        anomaly_type = ""
        
        if random.random() < self.anomaly_chance:
            anomaly_type, voltage, current, power = self._inject_anomaly(
                voltage, current, power, hour
            )
            is_anomaly = True
        
        reading = MeterReading.objects.create(
            meter=self.meter,
            timestamp=now,
            voltage=round(voltage, 2),
            current=round(current, 2),
            power=round(power, 2),
            energy=round(self.cumulative_energy, 3),
            power_factor=round(power_factor, 3),
            frequency=round(frequency, 2),
            temperature=round(temperature, 1),
            is_anomaly=is_anomaly,
            anomaly_type=anomaly_type
        )
        
        # Create alert if critical anomaly
        if is_anomaly and anomaly_type in ['voltage_spike', 'overcurrent', 'power_outage']:
            self._create_alert(reading, anomaly_type)
        
        return reading
    
    def _inject_anomaly(self, voltage, current, power, hour):
        """Inject various types of anomalies"""
        anomaly_types = [
            'voltage_spike',
            'voltage_drop',
            'overcurrent',
            'phantom_load',
            'power_outage'
        ]
        
        # Weighted selection (power outage is rare)
        weights = [0.25, 0.25, 0.25, 0.20, 0.05]
        anomaly_type = random.choices(anomaly_types, weights=weights)[0]
        
        if anomaly_type == 'voltage_spike':
            voltage *= random.uniform(1.15, 1.30)  # 15-30% overvoltage
            power *= 1.10  # Slight power increase
            
        elif anomaly_type == 'voltage_drop':
            voltage *= random.uniform(0.70, 0.85)  # 15-30% undervoltage
            power *= 0.90  # Slight power decrease
            
        elif anomaly_type == 'overcurrent':
            current *= random.uniform(1.50, 2.00)  # 50-100% overcurrent
            power *= 1.40
            
        elif anomaly_type == 'phantom_load':
            # Only during night hours
            if 23 <= hour or hour <= 5:
                power = random.uniform(100, 300)  # 100-300W standby
                current = power / voltage
            else:
                anomaly_type = ""  # Cancel if not night
                
        elif anomaly_type == 'power_outage':
            voltage = random.uniform(0, 20)
            current = 0
            power = 0
        
        return anomaly_type, voltage, current, power
    
    def _create_alert(self, reading, anomaly_type):
        """Create alert for critical anomaly"""
        messages = {
            'voltage_spike': {
                'title': '⚡ High Voltage Alert',
                'message': f'Dangerous voltage spike detected: {reading.voltage}V. Unplug sensitive equipment immediately!',
                'message_hindi': f'खतरनाक वोल्टेज स्पाइक: {reading.voltage}V। संवेदनशील उपकरण तुरंत अनप्लग करें!',
                'message_gujarati': f'ખતરનાક વોલ્ટેજ સ્પાઇક: {reading.voltage}V. સંવેદનશીલ ઉપકરણો તુરંત અનપ્લગ કરો!',
                'action': 'Check voltage stabilizer. Contact electrician if persists.',
                'cost': 200.0,
                'severity': 'critical'
            },
            'overcurrent': {
                'title': '⚠️ Overcurrent Detected',
                'message': f'High current flow: {reading.current}A. Risk of circuit damage.',
                'message_hindi': f'अधिक करंट: {reading.current}A। सर्किट क्षति का जोखिम।',
                'message_gujarati': f'વધુ પ્રવાહ: {reading.current}A. સર્કિટ નુકસાનનું જોખમ.',
                'action': 'Reduce load. Check for short circuit.',
                'cost': 300.0,
                'severity': 'critical'
            },
            'power_outage': {
                'title': '🔌 Power Outage',
                'message': 'Power supply interrupted. Checking grid status...',
                'message_hindi': 'बिजली आपूर्ति बाधित। ग्रिड स्थिति जाँच रहे हैं...',
                'message_gujarati': 'વીજ પુરવઠો બંધ. ગ્રિડ સ્થિતિ તપાસી રહ્યા છીએ...',
                'action': 'Contact utility provider.',
                'cost': 0.0,
                'severity': 'emergency'
            }
        }
        
        alert_data = messages.get(anomaly_type)
        if alert_data:
            Alert.objects.create(
                meter=self.meter,
                reading=reading,
                alert_type=anomaly_type,
                severity=alert_data['severity'],
                title=alert_data['title'],
                message=alert_data['message'],
                message_hindi=alert_data['message_hindi'],
                message_gujarati=alert_data['message_gujarati'],
                recommended_action=alert_data['action'],
                estimated_cost_impact=alert_data['cost']
            )


def create_sample_data():
    """Create sample users and meters for testing"""
    print("📝 Creating sample data...")
    
    # Create test user if doesn't exist
    user, created = User.objects.get_or_create(
        username='farmer_ramesh',
        defaults={
            'email': 'ramesh@example.com',
            'first_name': 'Ramesh',
            'last_name': 'Patel',
            'role': 'farmer',
            'phone_number': '+919876543210',
            'whatsapp_number': '+919876543210',
            'village': 'Anand',
            'district': 'Anand',
            'state': 'Gujarat',
            'preferred_language': 'gu'
        }
    )
    
    if created:
        user.set_password('password123')
        user.save()
        print(f"✅ Created user: {user.username}")
    
    # Create test meter if doesn't exist
    meter, created = Meter.objects.get_or_create(
        meter_id='GJ-ANAND-001',
        defaults={
            'user': user,
            'meter_type': 'agricultural',
            'manufacturer': 'Secure Meters',
            'model_number': 'SM-300',
            'installation_date': timezone.now().date() - timedelta(days=180),
            'status': 'active',
            'location': 'Ramesh Farm, Anand Village',
            'latitude': 22.5645,
            'longitude': 72.9289,
            'rated_voltage': 230.0,
            'rated_current': 40.0
        }
    )
    
    if created:
        print(f"✅ Created meter: {meter.meter_id}")
    
    return meter


def generate_live_data(meter, duration_minutes=60, interval_seconds=5):
    """
    Generate live meter data for demo
    
    Args:
        meter: Meter object
        duration_minutes: How long to generate data (default 60 minutes)
        interval_seconds: Time between readings (default 5 seconds)
    """
    generator = MeterDataGenerator(meter)
    iterations = (duration_minutes * 60) // interval_seconds
    
    print(f"\n🚀 Starting live data generation for meter: {meter.meter_id}")
    print(f"⏱️  Duration: {duration_minutes} minutes")
    print(f"📊 Interval: {interval_seconds} seconds")
    print(f"🔢 Total readings: {iterations}")
    print("\n" + "=" * 60)
    
    try:
        for i in range(iterations):
            reading = generator.generate_reading()
            
            # Print status every 10 readings
            if (i + 1) % 10 == 0:
                status = "⚠️ ANOMALY" if reading.is_anomaly else "✅ NORMAL"
                print(f"[{i+1}/{iterations}] {status} | "
                      f"V: {reading.voltage}V | I: {reading.current}A | "
                      f"P: {reading.power}W | E: {reading.energy}kWh | "
                      f"PF: {reading.power_factor}")
            
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Data generation stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
    finally:
        print(f"\n{'=' * 60}")
        print(f"✅ Generated {i+1} readings")
        print(f"📊 Total energy: {reading.energy:.2f} kWh")
        print(f"⚠️  Anomalies: {MeterReading.objects.filter(meter=meter, is_anomaly=True).count()}")
        print(f"🚨 Alerts: {Alert.objects.filter(meter=meter, status='active').count()}")


if __name__ == "__main__":
    print("=" * 60)
    print("🌾 Gram Meter - Real-Time Data Generator")
    print("=" * 60)
    
    # Create sample data
    meter = create_sample_data()
    
    # Generate live data (60 minutes, 5 second intervals)
    generate_live_data(meter, duration_minutes=60, interval_seconds=5)
