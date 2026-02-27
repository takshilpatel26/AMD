import json
import paho.mqtt.client as mqtt
from analytics_engine import GramBrain
import os
from datetime import datetime

brain = GramBrain()
baseline_kwh = None


def on_message(client, userdata, msg):
    global baseline_kwh
    try:
        data = json.loads(msg.payload.decode())
        current_kwh = data.get('Energy_kWh', 250.0)

        # Set baseline on first message to track "Today's" progress
        if baseline_kwh is None: baseline_kwh = current_kwh

        # Get AI/Logic Results
        is_anom, status_msg = brain.process_data(data)

        # Calculate Parameters
        todays_usage = current_kwh - baseline_kwh
        projection = brain.project_monthly_usage(datetime.now().day, current_kwh, data['Irrigation_Pump'],
                                                 data['Voltage'])

        stats = {
            "Live Usage (kW)": round(data['Global_active_power'], 3),
            "Today's Total (kWh)": round(todays_usage, 4),
            "Month's Total (kWh)": round(current_kwh, 2),
            "Today's Cost (INR)": round(brain.get_slab_cost(todays_usage), 2),
            "Efficiency Score (%)": brain.calculate_efficiency(projection),
            "Projected Monthly": projection,
            "System_Status": status_msg
        }

        os.system('cls' if os.name == 'nt' else 'clear')
        print("========================================")
        print("     GRAM METER: REAL-TIME ANALYTICS    ")
        print("========================================")
        print(json.dumps(stats, indent=4))

        # ONLY PRINT ALERT IF ANOMALY IS TRUE
        if is_anom:
            print("\n!!! SECURITY ALERT !!!")
            print(f"NOTIFICATION: {status_msg}")
        else:
            print("\nGrid Health: Stable")

    except Exception as e:
        print(f"Error: {e}")


client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("gram-meter/live/data")
client.loop_forever()