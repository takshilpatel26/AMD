import paho.mqtt.client as mqtt
import pandas as pd
import json
import time
import random
from datetime import datetime

# --- CONFIGURATION ---
BROKER = "broker.hivemq.com"
TOPIC = "gram-meter/village/map"
CSV_FILE = "dataforgovpanel.csv"
NUM_HOUSES = 500  # Generate 500 houses

# Load the base identity data
df_gov = pd.read_csv(CSV_FILE)

# Drop any rows with NaN in critical columns
df_gov = df_gov.dropna(subset=['house_id', 'name'])

# Convert house_id to string to ensure it's not NaN
df_gov['house_id'] = df_gov['house_id'].astype(str)

# Replicate data to get 500 houses
house_template = df_gov.head(10).to_dict('records')
generated_houses = []
for i in range(NUM_HOUSES):
    base = house_template[i % len(house_template)]
    name_parts = base["name"].split()
    first_name = name_parts[0]
    surname = name_parts[-1] if len(name_parts) > 1 else ""
    generated_houses.append({
        'house_id': f'HOUSE-{i+1:04d}',
        'name': f'{first_name} {surname}'.strip()
    })

df_gov = pd.DataFrame(generated_houses)

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, 1883, 60)


def get_status_note(voltage):
    """Rule-based engine to determine status based on live voltage"""
    if voltage == 0:
        return "🚨 Power Outage"
    elif voltage > 280:
        return "⚡ Severe Overvoltage"
    elif voltage > 250:
        return "⚠️ High Voltage Surge"
    elif voltage < 180:
        return "🛑 Brownout Level"
    elif voltage < 210:
        return "📉 Low Supply"
    else:
        return "✅ Normal"


print(f"Village Grid Simulator Active. Processing {len(df_gov)} nodes...")

while True:
    village_snapshot = []

    for _, row in df_gov.iterrows():
        # 1. GENERATE DYNAMIC TELEMETRY
        # Logic: Most houses are normal, very rare outages/surges
        chance = random.random()

        if chance < 0.001:  # 0.1% chance of outage (very rare)
            live_v = 0.0
            live_p = 0.0
        elif chance < 0.003:  # 0.2% chance of surge (very rare)
            live_v = random.uniform(260.0, 310.0)
            live_p = random.uniform(0.5, 2.0)
        elif chance < 0.103:  # 10% chance of high voltage
            live_v = random.uniform(245.0, 260.0)
            live_p = random.uniform(0.5, 8.0)
        else:  # ~89.7% Normal operation with jitter
            live_v = 230.0 + random.uniform(-15.0, 15.0)
            live_p = random.uniform(0.5, 8.0)  # Usage varies by appliance

        # 2. DECIDE STATUS NOTE
        status = get_status_note(live_v)

        # 3. CONSTRUCT PACKET (Preserving house_id and name)
        house_packet = {
            "house_id": str(row['house_id']),
            "name": str(row['name']),
            "voltage": round(float(live_v), 2),
            "usage_kw": round(float(live_p), 3),
            "status_note": status,
            "last_updated": datetime.now().strftime("%H:%M:%S")
        }
        village_snapshot.append(house_packet)

    # 4. BROADCAST
    client.publish(TOPIC, json.dumps(village_snapshot))

    print(f"Village Sync: {len(village_snapshot)} houses updated at {datetime.now().strftime('%H:%M:%S')}")
    time.sleep(2)