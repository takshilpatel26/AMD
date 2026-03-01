import json
import os
import random
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import paho.mqtt.client as mqtt

# --- CONFIGURATION ---
BROKER = "broker.hivemq.com"
TOPIC = "gram-meter/village/map"
CSV_FILE = Path(__file__).resolve().parent / "dataforgovpanel.csv"
NUM_HOUSES = 500  # Generate 500 houses



BASE_DIR = Path(__file__).resolve().parent

# --- CONFIGURATION (Render-friendly via env vars) ---
BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
TOPIC = os.getenv("MQTT_TOPIC", "gram-meter/village/map")
CSV_FILE = os.getenv("CSV_FILE", "dataforgovpanel.csv")
NUM_HOUSES = int(os.getenv("NUM_HOUSES", "500"))
PUBLISH_INTERVAL_SECONDS = float(os.getenv("PUBLISH_INTERVAL_SECONDS", "2"))


def load_houses() -> pd.DataFrame:
    csv_path = BASE_DIR / CSV_FILE
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df_gov = pd.read_csv(csv_path)
    df_gov = df_gov.dropna(subset=["house_id", "name"])
    df_gov["house_id"] = df_gov["house_id"].astype(str)

    house_template = df_gov.head(10).to_dict("records")
    if not house_template:
        raise ValueError("CSV has no valid house data after filtering")

    generated_houses = []
    for i in range(NUM_HOUSES):
        base = house_template[i % len(house_template)]
        name_parts = str(base["name"]).split()
        first_name = name_parts[0] if name_parts else "Resident"
        surname = name_parts[-1] if len(name_parts) > 1 else ""
        generated_houses.append(
            {
                "house_id": f"HOUSE-{i + 1:04d}",
                "name": f"{first_name} {surname}".strip(),
            }
        )

    return pd.DataFrame(generated_houses)


def build_mqtt_client() -> mqtt.Client:
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

    def on_connect(_client, _userdata, _flags, reason_code, _properties=None):
        print(f"MQTT connected to {BROKER}:{BROKER_PORT} (code={reason_code})")

    def on_disconnect(_client, _userdata, disconnect_flags, reason_code, _properties=None):
        print(f"MQTT disconnected (code={reason_code}, flags={disconnect_flags})")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    return client


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

def run_simulator():
    df_gov = load_houses()
    client = build_mqtt_client()
    client.connect(BROKER, BROKER_PORT, 60)
    client.loop_start()

    print(f"Village Grid Simulator Active. Processing {len(df_gov)} nodes...")
    print(f"Publishing to topic: {TOPIC}")

    try:
        while True:
            village_snapshot = []

            for _, row in df_gov.iterrows():
                chance = random.random()

                if chance < 0.001:
                    live_v = 0.0
                    live_p = 0.0
                elif chance < 0.003:
                    live_v = random.uniform(260.0, 310.0)
                    live_p = random.uniform(0.5, 2.0)
                elif chance < 0.103:
                    live_v = random.uniform(245.0, 260.0)
                    live_p = random.uniform(0.5, 8.0)
                else:
                    live_v = 230.0 + random.uniform(-15.0, 15.0)
                    live_p = random.uniform(0.5, 8.0)

                status = get_status_note(live_v)

                house_packet = {
                    "house_id": str(row["house_id"]),
                    "name": str(row["name"]),
                    "voltage": round(float(live_v), 2),
                    "usage_kw": round(float(live_p), 3),
                    "status_note": status,
                    "last_updated": datetime.now().strftime("%H:%M:%S"),
                }
                village_snapshot.append(house_packet)

            payload = json.dumps(village_snapshot)
            result = client.publish(TOPIC, payload)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"Publish failed with code: {result.rc}")

            print(f"Village Sync: {len(village_snapshot)} houses updated at {datetime.now().strftime('%H:%M:%S')}")
            time.sleep(PUBLISH_INTERVAL_SECONDS)
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    run_simulator()