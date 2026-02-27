"""
Advanced ML Models for Energy Analytics
Includes: LSTM Forecasting, Isolation Forest Anomaly Detection, Advanced Efficiency Scoring
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class LSTMForecaster:
    """
    LSTM-based energy forecasting model
    Note: This is a simplified implementation. For production, use TensorFlow/PyTorch
    """
    
    def __init__(self, lookback=24):
        self.lookback = lookback
        self.scaler = StandardScaler()
    
    def prepare_data(self, readings):
        """Prepare time series data for LSTM"""
        # Extract features: power, voltage, current, hour, day_of_week
        features = []
        for r in readings:
            hour = r['timestamp'].hour if hasattr(r['timestamp'], 'hour') else 0
            day = r['timestamp'].weekday() if hasattr(r['timestamp'], 'weekday') else 0
            features.append([
                r.get('power', 0),
                r.get('voltage', 230),
                r.get('current', 0),
                hour,
                day
            ])
        return np.array(features)
    
    def forecast(self, historical_readings, forecast_hours=24):
        """
        Generate forecast using exponential smoothing (simplified LSTM alternative)
        In production, replace with actual LSTM model
        """
        if len(historical_readings) < self.lookback:
            logger.warning(f"Insufficient data: {len(historical_readings)} < {self.lookback}")
            # Use simple average
            avg_power = np.mean([r.get('power', 0) for r in historical_readings])
            return self._generate_naive_forecast(avg_power, forecast_hours)
        
        # Extract power values
        power_values = np.array([r.get('power', 0) for r in historical_readings])
        
        # Apply exponential smoothing
        alpha = 0.3  # Smoothing factor
        forecasts = []
        
        # Initialize with last actual value
        last_value = power_values[-1]
        
        for _ in range(forecast_hours):
            # Exponential smoothing forecast
            forecast = alpha * last_value + (1 - alpha) * np.mean(power_values[-self.lookback:])
            
            # Add hourly pattern variation
            hour_factor = self._get_hour_factor(_)
            forecast *= hour_factor
            
            forecasts.append(forecast)
            last_value = forecast
        
        return forecasts
    
    def _get_hour_factor(self, hour_offset):
        """Get hourly load pattern factor"""
        # Simplified hourly pattern (0-23 hours)
        patterns = [
            0.5,  # 00:00 - Low
            0.45, # 01:00
            0.4,  # 02:00
            0.4,  # 03:00
            0.45, # 04:00
            0.5,  # 05:00
            0.7,  # 06:00 - Morning rise
            0.85, # 07:00
            0.95, # 08:00
            0.90, # 09:00
            0.85, # 10:00
            0.85, # 11:00
            0.90, # 12:00 - Noon
            0.85, # 13:00
            0.80, # 14:00
            0.85, # 15:00
            0.90, # 16:00
            0.95, # 17:00
            1.0,  # 18:00 - Peak evening
            0.95, # 19:00
            0.90, # 20:00
            0.80, # 21:00
            0.70, # 22:00
            0.60, # 23:00
        ]
        return patterns[hour_offset % 24]
    
    def _generate_naive_forecast(self, avg_power, hours):
        """Generate naive forecast with hourly patterns"""
        return [avg_power * self._get_hour_factor(h) for h in range(hours)]
    
    def calculate_confidence(self, historical_readings):
        """Calculate forecast confidence based on data consistency"""
        if len(historical_readings) < 10:
            return 0.5
        
        power_values = [r.get('power', 0) for r in historical_readings]
        std_dev = np.std(power_values)
        mean_val = np.mean(power_values)
        
        # Coefficient of variation
        cv = std_dev / mean_val if mean_val > 0 else 1.0
        
        # Lower CV = higher confidence
        confidence = max(0.5, min(0.95, 1.0 - cv))
        return confidence


class IsolationForestAnomalyDetector:
    """
    Isolation Forest-based anomaly detection
    More sophisticated than statistical thresholds
    """
    
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, historical_readings):
        """Train the Isolation Forest model"""
        if len(historical_readings) < 50:
            logger.warning("Insufficient data for training Isolation Forest")
            return False
        
        # Prepare features
        features = self._extract_features(historical_readings)
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Train model
        self.model.fit(scaled_features)
        self.is_trained = True
        
        logger.info(f"Isolation Forest trained on {len(historical_readings)} readings")
        return True
    
    def detect(self, readings):
        """Detect anomalies using trained model"""
        if not self.is_trained:
            logger.warning("Model not trained, using statistical method")
            return self._statistical_detection(readings)
        
        # Extract features
        features = self._extract_features(readings)
        
        # Scale features
        scaled_features = self.scaler.transform(features)
        
        # Predict anomalies (-1 = anomaly, 1 = normal)
        predictions = self.model.predict(scaled_features)
        scores = self.model.score_samples(scaled_features)
        
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:
                reading = readings[i]
                anomaly_type = self._classify_anomaly(reading)
                anomalies.append({
                    'index': i,
                    'type': anomaly_type,
                    'score': abs(score),
                    'severity': self._calculate_severity(score),
                    'reading': reading
                })
        
        return anomalies
    
    def _extract_features(self, readings):
        """Extract features for anomaly detection"""
        features = []
        for r in readings:
            features.append([
                r.get('voltage', 230),
                r.get('current', 0),
                r.get('power', 0),
                r.get('power_factor', 0.95),
                r.get('frequency', 50),
                r.get('voltage', 230) * r.get('current', 0)  # Apparent power
            ])
        return np.array(features)
    
    def _classify_anomaly(self, reading):
        """Classify the type of anomaly"""
        voltage = reading.get('voltage', 230)
        current = reading.get('current', 0)
        power = reading.get('power', 0)
        
        if voltage > 250:
            return 'voltage_spike'
        elif voltage < 200:
            return 'voltage_drop'
        elif current > 50:
            return 'overcurrent'
        elif power < 100 and current > 0:
            return 'phantom_load'
        elif power == 0 and voltage == 0:
            return 'power_outage'
        else:
            return 'unknown'
    
    def _calculate_severity(self, score):
        """Calculate severity based on anomaly score"""
        abs_score = abs(score)
        if abs_score > 0.5:
            return 'critical'
        elif abs_score > 0.3:
            return 'warning'
        else:
            return 'info'
    
    def _statistical_detection(self, readings):
        """Fallback statistical anomaly detection"""
        # Use z-score method
        features = self._extract_features(readings)
        mean = np.mean(features, axis=0)
        std = np.std(features, axis=0)
        
        anomalies = []
        for i, feature_set in enumerate(features):
            z_scores = np.abs((feature_set - mean) / (std + 1e-10))
            if np.any(z_scores > 2.5):
                reading = readings[i]
                anomalies.append({
                    'index': i,
                    'type': self._classify_anomaly(reading),
                    'score': np.max(z_scores) / 10,  # Normalize to 0-1
                    'severity': 'warning',
                    'reading': reading
                })
        
        return anomalies


class AdvancedEfficiencyAnalyzer:
    """
    Advanced efficiency analysis with machine learning insights
    """
    
    def __init__(self):
        self.weights = {
            'power_factor': 0.30,
            'load_profile': 0.30,
            'peak_usage': 0.20,
            'consistency': 0.20
        }
    
    def analyze(self, readings):
        """Comprehensive efficiency analysis"""
        if len(readings) < 10:
            return {
                'overall_score': 0,
                'grade': 'N/A',
                'breakdown': {},
                'insights': [],
                'recommendations': ['Insufficient data for analysis']
            }
        
        # Calculate component scores
        pf_score = self._calculate_power_factor_score(readings)
        load_score = self._calculate_load_profile_score(readings)
        peak_score = self._calculate_peak_usage_score(readings)
        consistency_score = self._calculate_consistency_score(readings)
        
        # Weighted overall score
        overall_score = (
            pf_score * self.weights['power_factor'] +
            load_score * self.weights['load_profile'] +
            peak_score * self.weights['peak_usage'] +
            consistency_score * self.weights['consistency']
        )
        
        # Generate insights
        insights = self._generate_advanced_insights(
            readings, pf_score, load_score, peak_score, consistency_score
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            pf_score, load_score, peak_score, consistency_score
        )
        
        return {
            'overall_score': int(overall_score),
            'grade': self._get_grade(overall_score),
            'breakdown': {
                'power_factor_score': int(pf_score),
                'load_profile_score': int(load_score),
                'peak_usage_score': int(peak_score),
                'consistency_score': int(consistency_score)
            },
            'insights': insights,
            'recommendations': recommendations,
            'potential_savings': self._calculate_savings(readings, overall_score)
        }
    
    def _calculate_power_factor_score(self, readings):
        """Score based on power factor (ideal: 0.95-1.0)"""
        pf_values = [r.get('power_factor', 0.95) for r in readings]
        avg_pf = np.mean(pf_values)
        
        if avg_pf >= 0.95:
            return 100
        elif avg_pf >= 0.90:
            return 90
        elif avg_pf >= 0.85:
            return 80
        elif avg_pf >= 0.80:
            return 70
        else:
            return 50
    
    def _calculate_load_profile_score(self, readings):
        """Score based on load consistency"""
        power_values = [r.get('power', 0) for r in readings]
        mean_power = np.mean(power_values)
        std_power = np.std(power_values)
        
        cv = std_power / mean_power if mean_power > 0 else 1.0
        
        # Lower CV = more consistent = higher score
        if cv < 0.2:
            return 100
        elif cv < 0.3:
            return 90
        elif cv < 0.4:
            return 80
        elif cv < 0.5:
            return 70
        else:
            return 60
    
    def _calculate_peak_usage_score(self, readings):
        """Score based on peak-to-average ratio"""
        power_values = [r.get('power', 0) for r in readings]
        peak_power = np.max(power_values)
        avg_power = np.mean(power_values)
        
        peak_ratio = peak_power / avg_power if avg_power > 0 else 2.0
        
        if peak_ratio < 1.5:
            return 100
        elif peak_ratio < 2.0:
            return 90
        elif peak_ratio < 2.5:
            return 80
        else:
            return 70
    
    def _calculate_consistency_score(self, readings):
        """Score based on voltage stability"""
        voltage_values = [r.get('voltage', 230) for r in readings]
        deviations = [abs(v - 230) / 230 * 100 for v in voltage_values]
        avg_deviation = np.mean(deviations)
        
        if avg_deviation < 2:
            return 100
        elif avg_deviation < 5:
            return 90
        elif avg_deviation < 8:
            return 80
        else:
            return 70
    
    def _generate_advanced_insights(self, readings, pf, load, peak, consistency):
        """Generate ML-based insights"""
        insights = []
        
        # Power factor insights
        if pf < 85:
            insights.append({
                'category': 'power_factor',
                'message': 'Poor power factor detected. Consider installing capacitor banks.',
                'impact': 'high',
                'potential_savings': self._estimate_pf_savings(readings)
            })
        
        # Load profile insights
        if load < 80:
            insights.append({
                'category': 'load_profile',
                'message': 'Inconsistent load pattern. Implement load scheduling.',
                'impact': 'medium',
                'potential_savings': self._estimate_load_savings(readings)
            })
        
        # Peak usage insights
        if peak < 85:
            insights.append({
                'category': 'peak_usage',
                'message': 'High peak demand. Shift loads to off-peak hours.',
                'impact': 'high',
                'potential_savings': self._estimate_peak_savings(readings)
            })
        
        # Voltage consistency insights
        if consistency < 85:
            insights.append({
                'category': 'voltage_stability',
                'message': 'Voltage fluctuations detected. Check supply quality.',
                'impact': 'medium',
                'potential_savings': 50.0
            })
        
        return insights
    
    def _generate_recommendations(self, pf, load, peak, consistency):
        """Generate actionable recommendations"""
        recommendations = []
        
        if pf < 90:
            recommendations.append("Install power factor correction equipment")
        if load < 85:
            recommendations.append("Implement automated load scheduling")
        if peak < 85:
            recommendations.append("Shift high-power loads to off-peak hours (10 PM - 6 AM)")
        if consistency < 85:
            recommendations.append("Install voltage stabilizer for sensitive equipment")
        
        if not recommendations:
            recommendations.append("Excellent efficiency! Maintain current usage patterns.")
        
        return recommendations
    
    def _estimate_pf_savings(self, readings):
        """Estimate savings from power factor improvement"""
        total_energy = sum(r.get('energy', 0) for r in readings)
        avg_pf = np.mean([r.get('power_factor', 0.95) for r in readings])
        
        # Penalty for PF < 0.9 is typically 1% for each 0.01 below
        if avg_pf < 0.9:
            penalty_percent = (0.9 - avg_pf) * 100
            savings = total_energy * 7.5 * (penalty_percent / 100)
            return round(savings, 2)
        return 0.0
    
    def _estimate_load_savings(self, readings):
        """Estimate savings from load optimization"""
        total_energy = sum(r.get('energy', 0) for r in readings)
        # Assume 5-10% savings from load optimization
        return round(total_energy * 7.5 * 0.075, 2)
    
    def _estimate_peak_savings(self, readings):
        """Estimate savings from peak reduction"""
        power_values = [r.get('power', 0) for r in readings]
        peak_power = np.max(power_values)
        avg_power = np.mean(power_values)
        
        # Savings from reducing demand charges
        excess_peak = max(0, peak_power - avg_power * 1.5)
        savings = excess_peak * 0.001 * 24 * 30 * 7.5  # Monthly savings
        return round(savings, 2)
    
    def _calculate_savings(self, readings, score):
        """Calculate total potential savings"""
        total_energy = sum(r.get('energy', 0) for r in readings)
        current_cost = total_energy * 7.5
        
        # Potential savings based on score gap to 100
        improvement_potential = (100 - score) / 100
        savings = current_cost * improvement_potential * 0.2  # 20% of gap
        
        return round(savings, 2)
    
    def _get_grade(self, score):
        """Convert score to grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'


# Singleton instances
lstm_forecaster = LSTMForecaster()
isolation_forest_detector = IsolationForestAnomalyDetector()
efficiency_analyzer = AdvancedEfficiencyAnalyzer()
