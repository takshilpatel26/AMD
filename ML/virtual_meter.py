import paho.mqtt.client as mqtt
import json
import time
import random
import os
import numpy as np  # Required for Monte Carlo distributions
from datetime import datetime

# --- CONFIGURATION ---
STATE_FILE = "meter_hardware_state.json"
BROKER = "broker.hivemq.com"
TOPIC = "gram-meter/live/data"
DEMO_ACCELERATION = 60 

def get_meter_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f).get("cumulative_kwh", 0)
    return round(sum([random.uniform(8.0, 12.0) for _ in range(25)]), 4)

def save_meter_state(val):
    with open(STATE_FILE, "w") as f:
        json.dump({"cumulative_kwh": val}, f)

# --- MONTE CARLO ENGINE ---
def monte_carlo_simulator(mode="normal"):
    """
    Simulates electrical parameters using probabilistic distributions
    instead of flat random ranges.
    """
    if mode == "surge":
        # Monte Carlo: Extreme Outlier Distribution (Surge)
        # We simulate 1000 'scenarios' and pick a high-end sample
        samples = np.random.normal(295, 10, 1000) 
        voltage = np.percentile(samples, 95) # Picking a severe spike scenario
        power = np.random.triangular(6.0, 7.5, 9.0) # High power draw during fault
        return voltage, power
    
    else:
        # Monte Carlo: Normal Distribution (Bell Curve)
        # Most readings stay near 230V (Standard Deviation of 2)
        voltage_samples = np.random.normal(230, 2, 1000)
        voltage = np.mean(random.choices(voltage_samples, k=10))
        
        # Power follows a multi-modal distribution (Pump On vs Off)
        is_pump = 1 if (random.random() < 0.3) else 0
        if is_pump:
            power = np.random.normal(4.5, 0.2) # Pump power is steady
        else:
            power = np.random.exponential(0.5) # Household power is low but spikes
        
        return voltage, power, is_pump

# --- MQTT SETUP ---
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, 1883, 60)

cumulative_kwh = get_meter_state()
iteration = 0

print(f"📡 Monte Carlo Digital Twin Active. Baseline: {cumulative_kwh} kWh")

while True:
    iteration += 1
    now = datetime.now()
    is_demo_event = (iteration % 15 == 0)

    # EXECUTE MONTE CARLO SIMULATION
    if is_demo_event:
        voltage, active_power = monte_carlo_simulator(mode="surge")
        pump_active = 1
        event_msg = "!!! MONTE CARLO EVENT: GRID INSTABILITY !!!"
    else:
        voltage, active_power, pump_active = monte_carlo_simulator(mode="normal")
        event_msg = "Monte Carlo: Normal Stochastic State"

    # CALCULATE STABILITY
    stability = abs(230 - voltage)

    # ACCELERATED ENERGY MATH
    energy_consumed = (active_power * (2 / 3600)) * DEMO_ACCELERATION
    cumulative_kwh += energy_consumed
    save_meter_state(cumulative_kwh)

    # DATA PACKET
    payload = {
        "Global_active_power": round(float(active_power), 4),
        "Voltage": round(float(voltage), 2),
        "Irrigation_Pump": int(pump_active),
        "Voltage_Stability": round(float(stability), 2),
        "Energy_kWh": round(float(cumulative_kwh), 4),
        "Day_of_Month": now.day,
        "Time": now.strftime("%H:%M:%S")
    }

    client.publish(TOPIC, json.dumps(payload))
    print(f"[{now.strftime('%H:%M:%S')}] {event_msg}")
    print(f"   ⚡ {active_power:.2f}kW | 🔋 {voltage:.1f}V | 📊 MC Distribution: Gaussian")
    print("-" * 40)

    time.sleep(2)