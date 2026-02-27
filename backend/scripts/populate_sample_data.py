"""
Quick Data Generator - Populate database with sample data for testing
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gram_meter.settings')
django.setup()

from meters.models import User, Meter, MeterReading
from django.utils import timezone
import random


def create_test_users():
    """Create test users"""
    users_data = [
        {
            'username': 'farmer_ramesh',
            'email': 'ramesh@example.com',
            'password': 'password123',
            'first_name': 'Ramesh',
            'last_name': 'Patel',
            'role': 'farmer',
            'village': 'Anand',
            'district': 'Anand',
            'state': 'Gujarat',
            'preferred_language': 'gu'
        },
        {
            'username': 'farmer_priya',
            'email': 'priya@example.com',
            'password': 'password123',
            'first_name': 'Priya',
            'last_name': 'Shah',
            'role': 'farmer',
            'village': 'Anand',
            'district': 'Anand',
            'state': 'Gujarat',
            'preferred_language': 'gu'
        },
        {
            'username': 'sarpanch_kumar',
            'email': 'kumar@example.com',
            'password': 'password123',
            'first_name': 'Kumar',
            'last_name': 'Desai',
            'role': 'sarpanch',
            'village': 'Anand',
            'district': 'Anand',
            'state': 'Gujarat',
            'preferred_language': 'gu'
        }
    ]
    
    created_users = []
    for data in users_data:
        password = data.pop('password')
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults=data
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"✅ Created user: {user.username}")
        else:
            print(f"ℹ️  User exists: {user.username}")
        created_users.append(user)
    
    return created_users


def create_test_meters(users):
    """Create test meters"""
    meters_data = [
        {
            'meter_id': 'GJ-ANAND-001',
            'user': users[0],
            'meter_type': 'agricultural',
            'manufacturer': 'Secure Meters',
            'location': 'Ramesh Farm, Anand'
        },
        {
            'meter_id': 'GJ-ANAND-002',
            'user': users[1],
            'meter_type': 'residential',
            'manufacturer': 'Tata Power',
            'location': 'Priya House, Anand'
        }
    ]
    
    created_meters = []
    for data in meters_data:
        meter, created = Meter.objects.get_or_create(
            meter_id=data['meter_id'],
            defaults={
                **data,
                'model_number': 'SM-300',
                'installation_date': timezone.now().date() - timedelta(days=180),
                'status': 'active',
                'rated_voltage': 230.0,
                'rated_current': 40.0
            }
        )
        if created:
            print(f"✅ Created meter: {meter.meter_id}")
        else:
            print(f"ℹ️  Meter exists: {meter.meter_id}")
        created_meters.append(meter)
    
    return created_meters


def generate_historical_data(meter, days=7):
    """Generate historical data for past N days"""
    print(f"\n📊 Generating {days} days of data for {meter.meter_id}...")
    
    start_time = timezone.now() - timedelta(days=days)
    readings_per_day = 288  # Every 5 minutes
    
    energy_cumulative = 0.0
    readings_created = 0
    
    for day in range(days):
        for reading in range(readings_per_day):
            timestamp = start_time + timedelta(days=day, minutes=reading*5)
            hour = timestamp.hour
            
            # Hourly load profile
            if 0 <= hour < 6:
                power_factor = 0.15
            elif 6 <= hour < 9:
                power_factor = 0.45
            elif 9 <= hour < 18:
                power_factor = 0.50
            elif 18 <= hour < 22:
                power_factor = 0.80
            else:
                power_factor = 0.30
            
            # Base power for meter type
            base_power = 3000 if meter.meter_type == 'residential' else 10000
            power = base_power * power_factor * random.uniform(0.85, 1.15)
            
            voltage = 230 * random.uniform(0.96, 1.04)
            pf = random.uniform(0.92, 0.98)
            current = power / (voltage * pf)
            
            energy_increment = (power / 1000) * (5 / 60)
            energy_cumulative += energy_increment
            
            MeterReading.objects.create(
                meter=meter,
                timestamp=timestamp,
                voltage=round(voltage, 2),
                current=round(current, 2),
                power=round(power, 2),
                energy=round(energy_cumulative, 3),
                power_factor=round(pf, 3),
                frequency=50.0,
                is_anomaly=False
            )
            
            readings_created += 1
    
    print(f"✅ Created {readings_created} readings ({energy_cumulative:.2f} kWh)")


if __name__ == "__main__":
    print("=" * 60)
    print("🌾 Gram Meter - Quick Data Generator")
    print("=" * 60 + "\n")
    
    # Create test data
    print("👥 Creating users...")
    users = create_test_users()
    
    print("\n📟 Creating meters...")
    meters = create_test_meters(users)
    
    print("\n📈 Generating historical readings...")
    for meter in meters:
        generate_historical_data(meter, days=7)
    
    print("\n" + "=" * 60)
    print("✅ Sample data generation complete!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Meters: {Meter.objects.count()}")
    print(f"   Readings: {MeterReading.objects.count()}")
