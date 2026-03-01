import json
import os
import random
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import paho.mqtt.client as mqtt


class GovernmentGridSimulator:
    def __init__(
        self,
        broker: str,
        broker_port: int,
        topic: str,
        num_houses: int,
        publish_interval_seconds: float,
        csv_file: str | None = None,
    ):
        self.broker = broker
        self.broker_port = broker_port
        self.topic = topic
        self.num_houses = num_houses
        self.publish_interval_seconds = publish_interval_seconds
        self.csv_file = csv_file
        self.df_houses = self._load_houses()
        self.client = self._build_mqtt_client()

    def _repo_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def _resolve_csv_path(self) -> Path | None:
        if self.csv_file:
            raw = Path(self.csv_file)
            if raw.is_absolute():
                return raw
            candidates = [
                Path.cwd() / raw,
                self._repo_root() / raw,
                Path(__file__).resolve().parent / raw,
            ]
            for candidate in candidates:
                if candidate.exists():
                    return candidate
            return candidates[0]

        default_candidates = [
            self._repo_root() / 'Admin' / 'dataforgovpanel.csv',
            self._repo_root() / 'backend' / 'distribution' / 'dataforgovpanel.csv',
        ]
        for candidate in default_candidates:
            if candidate.exists():
                return candidate
        return None

    def _load_houses(self) -> pd.DataFrame:
        csv_path = self._resolve_csv_path()

        if csv_path and csv_path.exists():
            df_gov = pd.read_csv(csv_path)
            df_gov = df_gov.dropna(subset=['house_id', 'name'])
            df_gov['house_id'] = df_gov['house_id'].astype(str)
            house_template = df_gov.head(10).to_dict('records')
        else:
            house_template = [
                {'house_id': 'HOUSE-TPL-1', 'name': 'Ramesh Patel'},
                {'house_id': 'HOUSE-TPL-2', 'name': 'Suresh Shah'},
                {'house_id': 'HOUSE-TPL-3', 'name': 'Anita Joshi'},
                {'house_id': 'HOUSE-TPL-4', 'name': 'Mahesh Mehta'},
                {'house_id': 'HOUSE-TPL-5', 'name': 'Kavita Trivedi'},
                {'house_id': 'HOUSE-TPL-6', 'name': 'Amit Desai'},
                {'house_id': 'HOUSE-TPL-7', 'name': 'Geeta Bhatt'},
                {'house_id': 'HOUSE-TPL-8', 'name': 'Sunita Dave'},
                {'house_id': 'HOUSE-TPL-9', 'name': 'Rajesh Modi'},
                {'house_id': 'HOUSE-TPL-10', 'name': 'Seema Soni'},
            ]

        generated_houses = []
        for i in range(self.num_houses):
            base = house_template[i % len(house_template)]
            name_parts = str(base['name']).split()
            first_name = name_parts[0] if name_parts else 'Resident'
            surname = name_parts[-1] if len(name_parts) > 1 else ''
            generated_houses.append(
                {
                    'house_id': f'HOUSE-{i + 1:04d}',
                    'name': f'{first_name} {surname}'.strip(),
                }
            )

        return pd.DataFrame(generated_houses)

    def _build_mqtt_client(self) -> mqtt.Client:
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

        def on_connect(_client, _userdata, _flags, reason_code, _properties=None):
            print(f'MQTT connected to {self.broker}:{self.broker_port} (code={reason_code})')

        def on_disconnect(_client, _userdata, disconnect_flags, reason_code, _properties=None):
            print(f'MQTT disconnected (code={reason_code}, flags={disconnect_flags})')

        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.reconnect_delay_set(min_delay=1, max_delay=30)
        return client

    @staticmethod
    def _get_status_note(voltage: float) -> str:
        if voltage == 0:
            return '🚨 Power Outage'
        if voltage > 280:
            return '⚡ Severe Overvoltage'
        if voltage > 250:
            return '⚠️ High Voltage Surge'
        if voltage < 180:
            return '🛑 Brownout Level'
        if voltage < 210:
            return '📉 Low Supply'
        return '✅ Normal'

    def _generate_house_packet(self, row) -> dict:
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

        return {
            'house_id': str(row['house_id']),
            'name': str(row['name']),
            'voltage': round(float(live_v), 2),
            'usage_kw': round(float(live_p), 3),
            'status_note': self._get_status_note(live_v),
            'last_updated': datetime.now().strftime('%H:%M:%S'),
        }

    def run_forever(self):
        self.client.connect(self.broker, self.broker_port, 60)
        self.client.loop_start()

        print(f'Village Grid Simulator Active. Processing {len(self.df_houses)} nodes...')
        print(f'Publishing to topic: {self.topic}')

        try:
            while True:
                village_snapshot = [
                    self._generate_house_packet(row)
                    for _, row in self.df_houses.iterrows()
                ]

                result = self.client.publish(self.topic, json.dumps(village_snapshot))
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    print(f'Publish failed with code: {result.rc}')

                print(
                    f"Village Sync: {len(village_snapshot)} houses updated at "
                    f"{datetime.now().strftime('%H:%M:%S')}"
                )
                time.sleep(self.publish_interval_seconds)
        finally:
            self.client.loop_stop()
            self.client.disconnect()


def build_from_env() -> GovernmentGridSimulator:
    return GovernmentGridSimulator(
        broker=os.getenv('MQTT_BROKER', 'broker.hivemq.com'),
        broker_port=int(os.getenv('MQTT_BROKER_PORT', '1883')),
        topic=os.getenv('MQTT_TOPIC', 'gram-meter/village/map'),
        num_houses=int(os.getenv('NUM_HOUSES', '500')),
        publish_interval_seconds=float(os.getenv('PUBLISH_INTERVAL_SECONDS', '2')),
        csv_file=os.getenv('CSV_FILE') or None,
    )
