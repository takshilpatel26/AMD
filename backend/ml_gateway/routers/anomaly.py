from fastapi import APIRouter, HTTPException
from datetime import datetime
import numpy as np
from typing import List
from ..schemas import (
    AnomalyRequest, AnomalyResponse, AnomalyResult,
    AnomalyType, MeterReadingInput
)
from ..ml_service import get_gram_brain
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def detect_anomalies_with_ml(readings: List[MeterReadingInput], sensitivity: float = 0.5) -> List[AnomalyResult]:
    """
    Detect anomalies using trained Isolation Forest model from GramBrain
    Falls back to statistical methods if ML model unavailable
    """
    anomalies = []
    brain = get_gram_brain()
    
    for reading in readings:
        # Prepare data for ML model
        reading_data = {
            'voltage': reading.voltage,
            'current': reading.current,
            'power': reading.power,
            'timestamp': reading.timestamp
        }
        
        # Try ML-based detection first
        if brain:
            try:
                is_anomaly, severity, message = brain.process_data({
                    'Global_active_power': reading.power / 1000,  # Convert W to kW
                    'Voltage': reading.voltage,
                    'Irrigation_Pump': 1 if reading.power > 3000 else 0,
                    'Voltage_Stability': abs(230 - reading.voltage),
                    'Time': reading.timestamp.strftime("%H:%M:%S")
                })
                
                if is_anomaly:
                    # Determine anomaly type from message
                    anomaly_type = AnomalyType.VOLTAGE_SPIKE
                    if 'Voltage Drop' in message or 'Brownout' in message:
                        anomaly_type = AnomalyType.VOLTAGE_DROP
                    elif 'Overcurrent' in message:
                        anomaly_type = AnomalyType.OVERCURRENT
                    elif 'Phantom Load' in message or 'Leakage' in message:
                        anomaly_type = AnomalyType.PHANTOM_LOAD
                    elif 'Surge' in message:
                        anomaly_type = AnomalyType.VOLTAGE_SPIKE
                    
                    # Calculate anomaly score based on deviation
                    if reading.voltage > 270:
                        score = min(1.0, (reading.voltage - 270) / 50)
                    elif reading.voltage < 180:
                        score = min(1.0, (230 - reading.voltage) / 100)
                    else:
                        score = 0.7
                    
                    # Map severity
                    if 'CRITICAL' in message:
                        severity_level = 'critical'
                        cost_impact = 300.0
                    elif 'WARNING' in message:
                        severity_level = 'warning'
                        cost_impact = 100.0
                    else:
                        severity_level = 'info'
                        cost_impact = 20.0
                    
                    # Recommended action
                    action = "Check equipment immediately"
                    if anomaly_type == AnomalyType.VOLTAGE_SPIKE:
                        action = "Unplug sensitive equipment. Check voltage stabilizer."
                    elif anomaly_type == AnomalyType.VOLTAGE_DROP:
                        action = "Check main connection. Contact utility provider."
                    elif anomaly_type == AnomalyType.OVERCURRENT:
                        action = "Reduce load immediately. Check for short circuits."
                    elif anomaly_type == AnomalyType.PHANTOM_LOAD:
                        action = "Check for leakage. Inspect irrigation pump valves."
                    
                    anomalies.append(AnomalyResult(
                        timestamp=reading.timestamp,
                        is_anomaly=True,
                        anomaly_type=anomaly_type,
                        anomaly_score=round(score, 3),
                        severity=severity_level,
                        message=message,
                        recommended_action=action,
                        estimated_cost_impact=round(cost_impact, 2)
                    ))
                    
            except Exception as e:
                logger.error(f"ML anomaly detection failed: {e}, falling back to statistical")
                # Fall through to statistical detection
        
        # Fallback: Statistical anomaly detection
        if not brain or not anomalies:
            anomaly_detected = False
            anomaly_type = None
            anomaly_score = 0.0
            severity = "info"
            message = ""
            action = ""
            cost_impact = 0.0
            
            # Voltage spike detection
            if reading.voltage > 270:
                anomaly_detected = True
                anomaly_type = AnomalyType.VOLTAGE_SPIKE
                anomaly_score = min(1.0, (reading.voltage - 270) / 50)
                severity = "critical" if reading.voltage > 285 else "warning"
                message = f"High voltage detected: {reading.voltage}V (Standard: 230V)"
                action = "Unplug sensitive equipment immediately. Check stabilizer."
                cost_impact = 200.0 if severity == "critical" else 50.0
            
            # Voltage drop detection
            elif reading.voltage < 180:
                anomaly_detected = True
                anomaly_type = AnomalyType.VOLTAGE_DROP
                anomaly_score = min(1.0, (230 - reading.voltage) / 100)
                severity = "critical" if reading.voltage < 170 else "warning"
                message = f"Low voltage detected: {reading.voltage}V (Standard: 230V)"
                action = "Check main connection. Contact utility if issue persists."
                cost_impact = 150.0 if severity == "critical" else 30.0
            
            # Overcurrent detection
            if reading.current > 40:
                if not anomaly_detected:
                    anomaly_detected = True
                    anomaly_type = AnomalyType.OVERCURRENT
                    anomaly_score = min(1.0, reading.current / 50)
                    severity = "critical" if reading.current > 50 else "warning"
                    message = f"High current detected: {reading.current}A"
                    action = "Check for overloaded circuits. Distribute load."
                    cost_impact = 300.0 if severity == "critical" else 80.0
            
            # Phantom load detection (low but constant power at night)
            hour = reading.timestamp.hour
            if (hour >= 23 or hour <= 5) and 50 < reading.power < 1000:
                anomaly_detected = True
                anomaly_type = AnomalyType.PHANTOM_LOAD
                anomaly_score = 0.6
                severity = "warning"
                message = f"Phantom load detected: {reading.power}W at {hour}:00"
                action = "Check for appliances in standby mode. Inspect for leakage."
                cost_impact = 500.0  # Monthly impact
            
            # Power outage detection
            if reading.voltage < 50 and reading.current < 0.5:
                anomaly_detected = True
                anomaly_type = AnomalyType.POWER_OUTAGE
                anomaly_score = 1.0
                severity = "critical"
                message = f"Power outage detected at {reading.timestamp}"
                action = "Verify main supply. Contact utility provider."
                cost_impact = 0.0
            
            if anomaly_detected:
                anomalies.append(AnomalyResult(
                    timestamp=reading.timestamp,
                    is_anomaly=True,
                    anomaly_type=anomaly_type,
                    anomaly_score=round(anomaly_score, 3),
                    severity=severity,
                    message=message,
                    recommended_action=action,
                    estimated_cost_impact=round(cost_impact, 2)
                ))
    
    return anomalies


@router.post("/detect", response_model=AnomalyResponse)
async def detect_meter_anomalies(request: AnomalyRequest):
    """
    Detect anomalies in meter readings using trained ML model
    
    Uses Isolation Forest model trained on rural India meter data.
    Detects:
    - Voltage spikes/drops
    - Overcurrent conditions
    - Phantom loads
    - Power outages
    
    Falls back to statistical detection if ML model unavailable.
    """
    try:
        logger.info(f"Detecting anomalies for meter {request.meter_id}, readings={len(request.readings)}")
        
        if len(request.readings) < 1:
            raise HTTPException(
                status_code=400,
                detail="At least 1 reading required for anomaly detection"
            )
        
        # Detect anomalies using ML model
        anomalies = detect_anomalies_with_ml(request.readings, request.sensitivity)
        
        response = AnomalyResponse(
            meter_id=request.meter_id,
            total_readings=len(request.readings),
            anomalies_detected=len(anomalies),
            anomalies=anomalies,
            detection_rate=round(len(anomalies) / len(request.readings), 3) if len(request.readings) > 0 else 0.0
        )
        
        logger.info(f"Anomalies detected: {len(anomalies)}/{len(request.readings)}")
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Anomaly detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")


@router.get("/health")
async def anomaly_health():
    """Health check for anomaly detection service"""
    return {
        "status": "healthy",
        "service": "anomaly_detection",
        "detectors": ["voltage", "current", "phantom_load", "power_outage"]
    }
