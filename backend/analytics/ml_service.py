"""
ML Service Layer - Integrates trained ML models with Django backend
Loads pickled models and provides predictions for forecasting, anomaly detection, and efficiency scoring
"""

import joblib
import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MLModelService:
    """
    Service class to load and use trained ML models
    Integrates GramBrain analytics engine with Django backend
    """
    
    def __init__(self):
        """Initialize ML models from pickle files"""
        # Get ML directory path
        self.ml_dir = Path(settings.BASE_DIR).parent / 'ML'
        
        # Load trained models
        try:
            self.anomaly_model = joblib.load(self.ml_dir / 'anomaly_model.pkl')
            logger.info("✅ Loaded anomaly_model.pkl successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load anomaly_model.pkl: {e}")
            self.anomaly_model = None
            
        try:
            self.monthly_model = joblib.load(self.ml_dir / 'monthly_model.pkl')
            logger.info("✅ Loaded monthly_model.pkl successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load monthly_model.pkl: {e}")
            self.monthly_model = None
            
        try:
            self.forecast_model = joblib.load(self.ml_dir / 'forecast_model.pkl')
            logger.info("✅ Loaded forecast_model.pkl successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load forecast_model.pkl: {e}")
            self.forecast_model = None
        
        # Professional tariffs for rural India (Gujarat rates)
        self.TARIFFS = {
            "SLAB_1_LIMIT": 100, 
            "RATE_1": 3.5,
            "SLAB_2_LIMIT": 250, 
            "RATE_2": 5.2,
            "BASE_RATE_3": 7.5
        }
        
        logger.info("🧠 ML Service initialized successfully")
    
    def get_slab_cost(self, total_units: float) -> float:
        """
        Calculate electricity cost based on slab-based tariff structure
        
        Args:
            total_units: Total kWh consumed
            
        Returns:
            Total cost in INR
        """
        T = self.TARIFFS
        
        if total_units <= T["SLAB_1_LIMIT"]:
            return total_units * T["RATE_1"]
        elif total_units <= T["SLAB_2_LIMIT"]:
            return (T["SLAB_1_LIMIT"] * T["RATE_1"]) + \
                   (total_units - T["SLAB_1_LIMIT"]) * T["RATE_2"]
        else:
            return (T["SLAB_1_LIMIT"] * T["RATE_1"]) + \
                   (150 * T["RATE_2"]) + \
                   (total_units - T["SLAB_2_LIMIT"]) * T["BASE_RATE_3"]
    
    def detect_anomaly(self, reading_data: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Detect anomalies in meter reading using trained Isolation Forest model
        
        Args:
            reading_data: Dictionary containing:
                - voltage: Voltage reading (V)
                - power: Active power reading (kW)
                - current: Current reading (A)
                - timestamp: Reading timestamp
                
        Returns:
            Tuple of (is_anomaly, severity, message)
        """
        voltage = reading_data.get('voltage', 230)
        power = reading_data.get('power', 0)
        current = reading_data.get('current', 0)
        
        # 1. Deterministic Safety Checks
        if voltage > 285:
            return True, "critical", "CRITICAL: Voltage Surge Detected - Risk of Equipment Damage"
        
        if voltage < 180:
            return True, "warning", "WARNING: Voltage Drop Detected - Brownout Condition"
        
        if current > 50:  # Assuming 50A max rating
            return True, "critical", "CRITICAL: Overcurrent Detected - Circuit Breaker Should Trip"
        
        # Check for phantom load (power usage at unusual hours)
        hour = datetime.now().hour
        if power > 1.0 and (hour >= 0 and hour <= 5):  # Night hours
            return True, "warning", "WARNING: Phantom Load Detected - Check for Leakage"
        
        # 2. AI-based Anomaly Detection
        if self.anomaly_model:
            try:
                # Calculate voltage stability (deviation from 230V standard)
                v_stability = abs(230 - voltage)
                
                # Estimate pump status (1 if power > 3kW, else 0)
                pump_status = 1 if power > 3.0 else 0
                
                # Prepare features for model (must match training data columns)
                features = pd.DataFrame([[
                    power,           # Global_active_power
                    voltage,         # Voltage
                    pump_status,     # Irrigation_Pump
                    v_stability      # Voltage_Stability
                ]], columns=['Global_active_power', 'Voltage', 'Irrigation_Pump', 'Voltage_Stability'])
                
                # Predict anomaly (-1 = anomaly, 1 = normal)
                prediction = self.anomaly_model.predict(features)[0]
                
                if prediction == -1:
                    return True, "warning", "WARNING: Unusual Usage Pattern Detected by AI"
                    
            except Exception as e:
                logger.error(f"Error in ML anomaly detection: {e}")
        
        return False, "info", "Status: Normal - All Parameters Within Range"
    
    def project_monthly_usage(
        self, 
        current_day_of_month: int, 
        kwh_consumed_so_far: float,
        avg_pump_usage: float = 0.0,
        avg_voltage: float = 230.0
    ) -> float:
        """
        Project total monthly energy consumption using trained regression model
        
        Args:
            current_day_of_month: Current day (1-31)
            kwh_consumed_so_far: Energy consumed up to current day (kWh)
            avg_pump_usage: Average pump usage factor (0-1)
            avg_voltage: Average voltage reading (V)
            
        Returns:
            Projected total monthly consumption (kWh)
        """
        days_in_month = 30
        days_remaining = days_in_month - current_day_of_month
        
        if days_remaining <= 0:
            return kwh_consumed_so_far
        
        # Use ML model to predict average daily consumption for remaining days
        if self.monthly_model:
            try:
                # Prepare features for prediction
                features = pd.DataFrame([[avg_pump_usage, avg_voltage]], 
                                       columns=['Irrigation_Pump', 'Voltage'])
                
                predicted_daily_avg = self.monthly_model.predict(features)[0]
                projected_remaining = predicted_daily_avg * days_remaining
                total_projection = kwh_consumed_so_far + projected_remaining
                
                return round(total_projection, 2)
                
            except Exception as e:
                logger.error(f"Error in monthly projection: {e}")
        
        # Fallback: Linear extrapolation
        daily_avg = kwh_consumed_so_far / current_day_of_month if current_day_of_month > 0 else 10
        total_projection = kwh_consumed_so_far + (daily_avg * days_remaining)
        
        return round(total_projection, 2)
    
    def calculate_efficiency_score(self, projected_total: float) -> float:
        """
        Calculate efficiency score based on projected consumption
        
        Args:
            projected_total: Projected monthly consumption (kWh)
            
        Returns:
            Efficiency score (0-100)
        """
        # Higher consumption = Lower efficiency score
        if projected_total <= 100:
            return 95.0
        elif projected_total <= 250:
            return 70 + (250 - projected_total) / 150 * 20
        else:
            return max(10, 50 - (projected_total - 250) / 10)
    
    def get_efficiency_grade(self, score: float) -> str:
        """
        Convert efficiency score to letter grade
        
        Args:
            score: Efficiency score (0-100)
            
        Returns:
            Letter grade (A+ to F)
        """
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def predict_next_hour(self, historical_readings: List[Dict]) -> Dict[str, Any]:
        """
        Predict energy consumption for next hour using time-series model
        
        Args:
            historical_readings: List of recent readings (last 24 hours minimum)
                Each dict should contain: timestamp, power, energy
                
        Returns:
            Dictionary with prediction results
        """
        if not self.forecast_model or len(historical_readings) < 10:
            # Fallback: Use average of last readings
            avg_power = np.mean([r.get('power', 0) for r in historical_readings[-10:]])
            return {
                'predicted_power': round(avg_power, 3),
                'predicted_energy': round(avg_power * 1.0, 3),  # 1 hour
                'confidence_score': 0.6,
                'lower_bound': round(avg_power * 0.8, 3),
                'upper_bound': round(avg_power * 1.2, 3),
                'model_type': 'fallback_average'
            }
        
        try:
            # Prepare time series data
            power_series = [r.get('power', 0) for r in historical_readings[-24:]]
            
            # Make prediction (assuming model expects array of recent values)
            prediction = self.forecast_model.predict([power_series[-10:]])[0]
            
            return {
                'predicted_power': round(prediction, 3),
                'predicted_energy': round(prediction * 1.0, 3),  # 1 hour
                'confidence_score': 0.85,
                'lower_bound': round(prediction * 0.85, 3),
                'upper_bound': round(prediction * 1.15, 3),
                'model_type': 'trained_ml_model'
            }
            
        except Exception as e:
            logger.error(f"Error in forecasting: {e}")
            # Return fallback
            avg_power = np.mean(power_series[-10:]) if power_series else 0
            return {
                'predicted_power': round(avg_power, 3),
                'predicted_energy': round(avg_power * 1.0, 3),
                'confidence_score': 0.5,
                'lower_bound': round(avg_power * 0.8, 3),
                'upper_bound': round(avg_power * 1.2, 3),
                'model_type': 'fallback_on_error'
            }
    
    def predict_weekly_consumption(self, meter_readings: List[Dict]) -> List[Dict]:
        """
        Predict energy consumption for next 7 days
        
        Args:
            meter_readings: Historical meter readings
            
        Returns:
            List of daily predictions
        """
        predictions = []
        
        # Calculate daily average from historical data
        if len(meter_readings) > 0:
            # Group by date and sum energy
            daily_consumption = {}
            for reading in meter_readings:
                date = reading.get('timestamp', datetime.now()).date()
                energy = reading.get('energy', 0)
                if date not in daily_consumption:
                    daily_consumption[date] = 0
                daily_consumption[date] += energy
            
            # Calculate average daily consumption
            if daily_consumption:
                avg_daily = np.mean(list(daily_consumption.values()))
            else:
                avg_daily = 10.0  # Default 10 kWh/day
        else:
            avg_daily = 10.0
        
        # Generate 7-day forecast
        base_date = datetime.now()
        for day in range(1, 8):
            forecast_date = base_date + timedelta(days=day)
            
            # Add some variance (±10%)
            daily_prediction = avg_daily * np.random.uniform(0.9, 1.1)
            
            predictions.append({
                'date': forecast_date.date().isoformat(),
                'predicted_energy': round(daily_prediction, 2),
                'lower_bound': round(daily_prediction * 0.85, 2),
                'upper_bound': round(daily_prediction * 1.15, 2),
                'confidence': 0.75
            })
        
        return predictions
    
    def analyze_consumption_pattern(self, readings: List[Dict]) -> Dict[str, Any]:
        """
        Analyze consumption patterns and provide insights
        
        Args:
            readings: List of meter readings with timestamps
            
        Returns:
            Dictionary with pattern analysis
        """
        if not readings:
            return {
                'pattern': 'insufficient_data',
                'peak_hours': [],
                'off_peak_hours': [],
                'recommendations': ['Need more data for analysis']
            }
        
        # Analyze hourly patterns
        hourly_consumption = {}
        for reading in readings:
            hour = reading.get('timestamp', datetime.now()).hour
            power = reading.get('power', 0)
            
            if hour not in hourly_consumption:
                hourly_consumption[hour] = []
            hourly_consumption[hour].append(power)
        
        # Calculate average per hour
        hourly_avg = {
            hour: np.mean(powers) 
            for hour, powers in hourly_consumption.items()
        }
        
        # Identify peak and off-peak hours
        if hourly_avg:
            sorted_hours = sorted(hourly_avg.items(), key=lambda x: x[1], reverse=True)
            peak_hours = [h for h, _ in sorted_hours[:3]]  # Top 3
            off_peak_hours = [h for h, _ in sorted_hours[-3:]]  # Bottom 3
        else:
            peak_hours = []
            off_peak_hours = []
        
        # Generate recommendations
        recommendations = []
        if peak_hours:
            recommendations.append(f"Shift non-critical loads from {peak_hours[0]}:00 to off-peak hours")
        if any(h in range(0, 6) for h in peak_hours):
            recommendations.append("High night consumption detected - check for phantom loads")
        
        return {
            'pattern': 'analyzed',
            'peak_hours': sorted(peak_hours),
            'off_peak_hours': sorted(off_peak_hours),
            'hourly_average': hourly_avg,
            'recommendations': recommendations,
            'total_readings_analyzed': len(readings)
        }


# Global instance (singleton pattern)
_ml_service_instance = None

def get_ml_service() -> MLModelService:
    """
    Get singleton instance of ML service
    
    Returns:
        MLModelService instance
    """
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = MLModelService()
    return _ml_service_instance
