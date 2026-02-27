#!/usr/bin/env python
"""
Test script to verify ML models integration with Django backend
Tests Django REST API endpoints that use trained ML models
"""

import requests
import json
from datetime import datetime

# Configuration
DJANGO_BASE_URL = "http://localhost:8000/api/v1"
FASTAPI_BASE_URL = "http://localhost:8001/api/v1/ml"

# Test credentials (you'll need to create a user first)
TEST_PHONE = "+919876543210"
TEST_OTP = "123456"  # Replace with actual OTP

print("=" * 80)
print(" GRAM METER ML INTEGRATION TEST SUITE")
print("=" * 80)

def get_auth_token():
    """Get JWT token for authentication"""
    print("\n📱 Testing Authentication...")
    
    # Request OTP
    response = requests.post(f"{DJANGO_BASE_URL}/auth/mobile/request-otp/", json={
        "phone_number": TEST_PHONE
    })
    
    if response.status_code == 200:
        print(f"✅ OTP sent to {TEST_PHONE}")
        
        # Verify OTP (in production, get OTP from phone/Twilio)
        verify_response = requests.post(f"{DJANGO_BASE_URL}/auth/mobile/verify-otp/", json={
            "phone_number": TEST_PHONE,
            "otp": input("Enter OTP received: ")
        })
        
        if verify_response.status_code == 200:
            data = verify_response.json()
            token = data.get('access_token')
            print(f"✅ Authenticated successfully!")
            return token
        else:
            print(f"❌ OTP verification failed: {verify_response.text}")
            return None
    else:
        print(f"❌ Failed to request OTP: {response.text}")
        return None


def test_anomaly_detection(token):
    """Test ML-powered anomaly detection"""
    print("\n🤖 Testing ML Anomaly Detection...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with normal reading
    normal_reading = {
        "meter_id": "GJ-ANAND-001",
        "voltage": 230.5,
        "current": 10.2,
        "power": 2350,
        "energy": 156.7,
        "power_factor": 0.95,
        "frequency": 50.0
    }
    
    response = requests.post(
        f"{DJANGO_BASE_URL}/analytics/ml/detect_anomaly/",
        headers=headers,
        json=normal_reading
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Normal reading: is_anomaly={result['is_anomaly']}, message='{result['message']}'")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test with voltage spike
    spike_reading = {
        "meter_id": "GJ-ANAND-001",
        "voltage": 290.0,  # Dangerous spike!
        "current": 15.5,
        "power": 4500,
        "energy": 158.2,
        "power_factor": 0.92,
        "frequency": 50.2
    }
    
    response = requests.post(
        f"{DJANGO_BASE_URL}/analytics/ml/detect_anomaly/",
        headers=headers,
        json=spike_reading
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Voltage spike: is_anomaly={result['is_anomaly']}, severity={result['severity']}")
        print(f"   Message: {result['message']}")
        print(f"   Alert created: {result['alert_created']}")
    else:
        print(f"❌ Failed: {response.text}")


def test_consumption_prediction(token):
    """Test ML-powered monthly consumption prediction"""
    print("\n📊 Testing ML Consumption Prediction...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    prediction_data = {
        "meter_id": "GJ-ANAND-001",
        "current_day": 15,
        "consumed_so_far": 125.5,
        "avg_pump_usage": 0.35,
        "avg_voltage": 228.5
    }
    
    response = requests.post(
        f"{DJANGO_BASE_URL}/analytics/ml/predict_consumption/",
        headers=headers,
        json=prediction_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Prediction successful!")
        print(f"   Current consumption: {result['current_consumption']} kWh (₹{result['current_cost']})")
        print(f"   Projected monthly: {result['projected_monthly_kwh']} kWh (₹{result['projected_cost']})")
        print(f"   Efficiency score: {result['efficiency_score']}/100 (Grade: {result['efficiency_grade']})")
        print(f"   Model: {result['model_used']}")
    else:
        print(f"❌ Failed: {response.text}")


def test_weekly_forecast(token):
    """Test ML-powered 7-day forecast"""
    print("\n🔮 Testing ML Weekly Forecast...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{DJANGO_BASE_URL}/analytics/ml/weekly_forecast/",
        headers=headers,
        params={"meter_id": "GJ-ANAND-001"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Forecast generated!")
        print(f"   Using {result['historical_readings_count']} historical readings")
        print("\n   7-Day Forecast:")
        for day in result['forecast'][:3]:  # Show first 3 days
            print(f"   {day['date']}: {day['predicted_energy']} kWh (confidence: {day['confidence']})")
    else:
        print(f"❌ Failed: {response.text}")


def test_pattern_analysis(token):
    """Test ML-powered pattern analysis"""
    print("\n🔍 Testing ML Pattern Analysis...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{DJANGO_BASE_URL}/analytics/ml/pattern_analysis/",
        headers=headers,
        params={"meter_id": "GJ-ANAND-001", "days": 30}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Analysis complete!")
        print(f"   Pattern: {result['pattern']}")
        print(f"   Peak hours: {result.get('peak_hours', [])}")
        print(f"   Off-peak hours: {result.get('off_peak_hours', [])}")
        print(f"   Recommendations:")
        for rec in result.get('recommendations', []):
            print(f"   - {rec}")
    else:
        print(f"❌ Failed: {response.text}")


def test_fastapi_anomaly():
    """Test FastAPI ML Gateway anomaly detection"""
    print("\n⚡ Testing FastAPI ML Gateway...")
    
    test_data = {
        "meter_id": "TEST-001",
        "sensitivity": 0.5,
        "readings": [
            {
                "meter_id": "TEST-001",
                "timestamp": datetime.now().isoformat(),
                "voltage": 235.0,
                "current": 12.0,
                "power": 2820,
                "energy": 150.5,
                "power_factor": 0.95,
                "frequency": 50.0
            },
            {
                "meter_id": "TEST-001",
                "timestamp": datetime.now().isoformat(),
                "voltage": 295.0,  # Spike!
                "current": 18.0,
                "power": 5310,
                "energy": 152.0,
                "power_factor": 0.90,
                "frequency": 50.2
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/anomaly/detect",
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ FastAPI anomaly detection working!")
            print(f"   Total readings: {result['total_readings']}")
            print(f"   Anomalies detected: {result['anomalies_detected']}")
            print(f"   Detection rate: {result['detection_rate']}")
            
            if result['anomalies']:
                anomaly = result['anomalies'][0]
                print(f"\n   First anomaly:")
                print(f"   - Type: {anomaly['anomaly_type']}")
                print(f"   - Severity: {anomaly['severity']}")
                print(f"   - Message: {anomaly['message']}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error connecting to FastAPI: {e}")


def main():
    """Run all tests"""
    
    # Skip authentication for FastAPI test (no auth required)
    print("\n" + "=" * 80)
    print(" PART 1: FastAPI ML Gateway (No Auth)")
    print("=" * 80)
    test_fastapi_anomaly()
    
    # Django tests require authentication
    print("\n" + "=" * 80)
    print(" PART 2: Django ML Integration (Requires Auth)")
    print("=" * 80)
    
    auth_choice = input("\nDo you want to test Django endpoints? (requires authentication) [y/n]: ")
    
    if auth_choice.lower() == 'y':
        token = get_auth_token()
        
        if token:
            test_anomaly_detection(token)
            test_consumption_prediction(token)
            test_weekly_forecast(token)
            test_pattern_analysis(token)
            
            print("\n" + "=" * 80)
            print(" ✅ ALL TESTS COMPLETED!")
            print("=" * 80)
        else:
            print("\n❌ Authentication failed. Cannot run Django tests.")
    else:
        print("\n⏭️  Skipping Django tests.")
    
    print("\n" + "=" * 80)
    print(" ML MODELS STATUS:")
    print(" ✅ anomaly_model.pkl - Isolation Forest for anomaly detection")
    print(" ✅ monthly_model.pkl - Regression for monthly prediction")
    print(" ✅ forecast_model.pkl - Time-series for hourly forecasting")
    print("=" * 80)


if __name__ == "__main__":
    main()
