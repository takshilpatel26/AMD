import paho.mqtt.client as mqtt
import json
from .analytics_engine import GramBrain
from .models import MeterState

brain = GramBrain()


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    is_anomaly, alert_en, alert_hi = brain.process_data(data)

    # Update Django Database for Role A to fetch
    MeterState.objects.create(
        voltage=data['Voltage'],
        power=data['Global_active_power'],
        is_anomaly=is_anomaly,
        alert_hindi=alert_hi
    )

    # IF ANOMALY: Trigger Role C's WhatsApp function
    if is_anomaly:
        send_whatsapp_alert(alert_hi)  # Import from Role C's script


client = mqtt.Client()
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("gram-meter/live/data")
client.loop_start()