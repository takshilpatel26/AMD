import paho.mqtt.client as mqtt
import json
import time
import random
import os
import joblib
import pandas as pd
import warnings
import threading
from datetime import datetime
from collections import deque
from analytics_engine import GramBrain

# --- CONFIGURATION & SILENCING ---
warnings.filterwarnings("ignore", category=UserWarning)
BROKER = "broker.hivemq.com"
TOPIC = "gram-meter/live/data"
STATE_FILE = "meter_hardware_state.json"


# --- 1. THE VIRTUAL METER (GENERATOR THREAD) ---
def virtual_meter_thread():
    """Simulates the Hardware Smart Meter"""

    def get_initial_state():
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                return json.load(f).get("cumulative_kwh", 0)
        # Seed 25 days of history (~200-300 kWh)
        return round(sum([random.uniform(6.0, 12.0) for _ in range(25)]), 4)

    client_gen = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client_gen.connect(BROKER, 1883, 60)

    cumulative_kwh = get_initial_state()

    while True:
        now = datetime.now()
        pump_active = 1 if (random.random() < 0.3) else 0
        active_power = (pump_active * 4.5) + random.uniform(0.2, 0.7)
        voltage = 230.0 + random.uniform(-5, 5)

        # Inject Anomaly
        if random.random() < 0.05: voltage = random.uniform(280, 310)

        stability = 100 - abs(230 - voltage)
        cumulative_kwh += (active_power * (2 / 3600))

        # Persist State
        with open(STATE_FILE, "w") as f:
            json.dump({"cumulative_kwh": cumulative_kwh}, f)

        payload = {
            "Global_active_power": round(active_power, 4),
            "Voltage": round(voltage, 2),
            "Irrigation_Pump": pump_active,
            "Voltage_Stability": round(stability, 2),
            "Cumulative_kWh": round(cumulative_kwh, 4),
            "Day_of_Month": now.day,
            "Time": now.strftime("%H:%M:%S")
        }

        client_gen.publish(TOPIC, json.dumps(payload))
        time.sleep(2)


# --- 2. THE AI SERVICE (PROCESSOR THREAD) ---
def ai_service_thread():
    """Processes incoming IoT data and displays the Dashboard"""
    brain = GramBrain()
    next_min_forecaster = joblib.load('forecast_model.pkl')
    power_buffer = deque(maxlen=10)

    def on_message(client, userdata, msg):
        data = json.loads(msg.payload.decode())
        p = data['Global_active_power']
        v = data['Voltage']
        cum_kwh = data['Cumulative_kWh']
        day = data['Day_of_Month']
        power_buffer.append(p)

        # AI Predictions
        proj_total = brain.project_monthly_usage(day, cum_kwh, data['Irrigation_Pump'], v)
        proj_cost = brain.get_slab_cost(proj_total)
        eff_score = brain.calculate_efficiency(proj_total)
        is_anom, _, stat_hi = brain.process_data(data)

        # Dashboard UI
        os.system('cls' if os.name == 'nt' else 'clear')
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f" ⚡ UNIFIED GRAM METER ENGINE | {data['Time']} ")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f" 📍 LIVE SENSOR READING   : {p:.3f} kW | {v:.1f} V")
        print(f" 📈 TOTAL LOAD (HISTORY)  : {cum_kwh:.2f} kWh")
        print("────────────────────────────────────────────────────────────────")
        print(f" 🔮 AI MONTHLY PROJECTION : {proj_total:.2f} kWh")
        print(f" 💰 ESTIMATED MONTHLY BILL: ₹{proj_cost:.2f}")
        print(f" 🎯 EFFICIENCY SCORE      : {eff_score:.1f}%")

        if is_anom:
            print(f"\n 🚨 ALERT: {stat_hi.upper()}")
        else:
            print(f"\n ✅ STATUS: {stat_hi}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(" [Press Ctrl+C to Stop All Systems]")

    client_srv = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client_srv.on_message = on_message
    client_srv.connect(BROKER, 1883, 60)
    client_srv.subscribe(TOPIC)
    client_srv.loop_forever()


# --- 3. EXECUTION ---
if __name__ == "__main__":
    # Start Generator
    t1 = threading.Thread(target=virtual_meter_thread, daemon=True)
    t1.start()

    # Start Service (Main Thread)
    try:
        ai_service_thread()
    except KeyboardInterrupt:
        print("\nStopping Unified Engine...")