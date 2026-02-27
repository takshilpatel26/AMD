import joblib
import pandas as pd
import os
from pathlib import Path
import random


class GramBrain:
    def __init__(self):
        # Get the directory where this file is located
        current_dir = Path(__file__).parent
        
        # LOAD BOTH MODELS HERE with absolute paths
        try:
            self.clf = joblib.load(current_dir / 'anomaly_model.pkl')
            print("✅ Loaded anomaly_model.pkl")
        except Exception as e:
            print(f"⚠️  Could not load anomaly_model.pkl: {e}")
            self.clf = None
            
        try:
            self.monthly_model = joblib.load(current_dir / 'monthly_model.pkl')
            print("✅ Loaded monthly_model.pkl")
        except Exception as e:
            print(f"⚠️  Could not load monthly_model.pkl: {e}")
            self.monthly_model = None

        # Professional TARIFFS for rural India
        self.TARIFFS = {
            "SLAB_1_LIMIT": 100, "RATE_1": 3.5,
            "SLAB_2_LIMIT": 250, "RATE_2": 5.2,
            "BASE_RATE_3": 7.5
        }

    def get_slab_cost(self, total_units):
        T = self.TARIFFS
        if total_units <= T["SLAB_1_LIMIT"]:
            return total_units * T["RATE_1"]
        elif total_units <= T["SLAB_2_LIMIT"]:
            return (T["SLAB_1_LIMIT"] * T["RATE_1"]) + (total_units - T["SLAB_1_LIMIT"]) * T["RATE_2"]
        else:
            return (T["SLAB_1_LIMIT"] * T["RATE_1"]) + (150 * T["RATE_2"]) + (total_units - T["SLAB_2_LIMIT"]) * T[
                "BASE_RATE_3"]

    # def process_data(self, data):
    #     # Deterministic Safety
    #     if data['Voltage'] > 270: return True, "Critical Surge!", "बिजली का झटका!"
    #
    #     # AI Behavioral Check
    #     feat = [[data['Global_active_power'], data['Voltage'], data['Irrigation_Pump'], data['Voltage_Stability']]]
    #     is_anomaly = self.clf.predict(feat)[0]
    #
    #     # Night Leakage Logic
    #     if data['Irrigation_Pump'] > 35 and (data['Time'] < "05:00:00"):
    #         return True, "Potential Leakage", "पंप लीक की जांच करें"
    #
    #     return bool(is_anomaly), "Normal"
    def process_data(self, data):
        # 1. Deterministic Safety Logic
        if data['Voltage'] > 285:
            return True, "CRITICAL: Voltage Surge Detected"

        # 2. CALCULATE THE MISSING FEATURE
        # Voltage Stability is the absolute deviation from the standard 230V
        v_stability = abs(230 - data['Voltage'])

        # 3. AI Anomaly Detection (MATCHING THE TRAINING FEATURES)
        if self.clf:
            # You MUST include every feature used during training in the correct order
            # Based on your previous trainer, these are:
            features = ['Global_active_power', 'Voltage', 'Irrigation_Pump', 'Voltage_Stability']

            input_data = [[
                data['Global_active_power'],
                data['Voltage'],
                data['Irrigation_Pump'],
                v_stability  # The missing piece!
            ]]

            df = pd.DataFrame(input_data, columns=features)
            ai_anomaly = self.clf.predict(df)[0] == -1
        else:
            ai_anomaly = False

        if ai_anomaly:
            return True, "WARNING: Unusual Usage Pattern"

        return False, "Status: Normal"

    def predict_slab_jump(self, current_units, predicted_units):
        total = current_units + predicted_units
        if current_units < 250 and total >= 250:
            return True, "⚠️ Slab Jump Warning: You are entering the High-Tax bracket!"
        return False, "Safe: You are within Slab 1 limits."

    def project_monthly_usage(self, current_day_of_month, kwh_consumed_so_far, avg_pump_usage, avg_voltage):
        days_in_month = 30
        days_remaining = days_in_month - current_day_of_month

        if days_remaining <= 0:
            return kwh_consumed_so_far

        # AI predicts the average kWh for the remaining days based on behavior
        predicted_daily_avg = self.monthly_model.predict([[avg_pump_usage, avg_voltage]])[0]

        projected_remaining = predicted_daily_avg * days_remaining
        total_projection = kwh_consumed_so_far + projected_remaining

        return round(total_projection, 2)

    def calculate_efficiency(self, projected_total):
        # Higher consumption = Lower efficiency score
        if projected_total <= 100: return 95 + random.randint(0, 4)
        if projected_total <= 250: return 70 + (250 - projected_total) / 150 * 20
        return max(10, 50 - (projected_total - 250) / 10)