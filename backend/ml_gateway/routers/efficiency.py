from fastapi import APIRouter, HTTPException
import numpy as np
from typing import List
from ..schemas import (
    EfficiencyRequest, EfficiencyResponse, EfficiencyBreakdown,
    EfficiencyInsight, MeterReadingInput
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def calculate_power_factor_score(power_factors: List[float]) -> int:
    """Calculate power factor efficiency score (0-100)"""
    avg_pf = np.mean(power_factors)
    
    # Ideal PF >= 0.95
    if avg_pf >= 0.95:
        score = 100
    elif avg_pf >= 0.90:
        score = 90
    elif avg_pf >= 0.85:
        score = 75
    elif avg_pf >= 0.80:
        score = 60
    else:
        score = max(0, int(avg_pf * 70))
    
    return score


def calculate_load_profile_score(powers: List[float]) -> int:
    """Calculate load profile consistency score (0-100)"""
    # Check for consistent load vs erratic usage
    std_dev = np.std(powers)
    mean_power = np.mean(powers)
    
    if mean_power == 0:
        return 50
    
    coefficient_of_variation = std_dev / mean_power
    
    # Lower CV = more consistent = better score
    if coefficient_of_variation < 0.3:
        score = 100
    elif coefficient_of_variation < 0.5:
        score = 85
    elif coefficient_of_variation < 0.7:
        score = 70
    elif coefficient_of_variation < 1.0:
        score = 55
    else:
        score = 40
    
    return score


def calculate_peak_usage_score(readings: List[MeterReadingInput]) -> int:
    """Calculate peak time usage optimization score (0-100)"""
    peak_hours = [9, 10, 11, 18, 19, 20, 21]  # 9-12 AM and 6-10 PM
    
    peak_usage = 0
    off_peak_usage = 0
    
    for reading in readings:
        hour = reading.timestamp.hour
        if hour in peak_hours:
            peak_usage += reading.power
        else:
            off_peak_usage += reading.power
    
    total_usage = peak_usage + off_peak_usage
    if total_usage == 0:
        return 50
    
    peak_ratio = peak_usage / total_usage
    
    # Less peak usage = better score
    if peak_ratio < 0.3:
        score = 100
    elif peak_ratio < 0.4:
        score = 85
    elif peak_ratio < 0.5:
        score = 70
    elif peak_ratio < 0.6:
        score = 55
    else:
        score = 40
    
    return score


def calculate_consistency_score(readings: List[MeterReadingInput]) -> int:
    """Calculate power quality consistency score (0-100)"""
    voltages = [r.voltage for r in readings]
    
    # Check voltage stability (should be ~230V ±10%)
    voltage_deviations = [abs(v - 230) / 230 for v in voltages]
    avg_deviation = np.mean(voltage_deviations)
    
    if avg_deviation < 0.05:  # <5% deviation
        score = 100
    elif avg_deviation < 0.10:
        score = 85
    elif avg_deviation < 0.15:
        score = 70
    elif avg_deviation < 0.20:
        score = 55
    else:
        score = 40
    
    return score


def generate_insights(
    readings: List[MeterReadingInput],
    breakdown: EfficiencyBreakdown,
    total_energy: float
) -> List[EfficiencyInsight]:
    """Generate actionable efficiency insights"""
    insights = []
    
    # Power factor insights
    avg_pf = np.mean([r.power_factor for r in readings])
    if avg_pf < 0.90:
        savings = total_energy * 7.5 * 0.10  # 10% savings possible
        insights.append(EfficiencyInsight(
            category="Power Factor",
            message=f"Low power factor ({avg_pf:.2f}). Install capacitors to improve.",
            potential_savings=round(savings, 2),
            priority="high"
        ))
    
    # Peak usage insights
    if breakdown.peak_usage_score < 70:
        savings = total_energy * 7.5 * 0.15  # 15% savings by shifting load
        insights.append(EfficiencyInsight(
            category="Load Shifting",
            message="High consumption during peak hours. Shift heavy loads to off-peak.",
            potential_savings=round(savings, 2),
            priority="medium"
        ))
    
    # Voltage stability insights
    voltages = [r.voltage for r in readings]
    if np.std(voltages) > 15:
        insights.append(EfficiencyInsight(
            category="Power Quality",
            message="Unstable voltage detected. Install voltage stabilizer.",
            potential_savings=round(total_energy * 7.5 * 0.05, 2),
            priority="high"
        ))
    
    # Phantom load detection
    night_readings = [r for r in readings if 23 <= r.timestamp.hour or r.timestamp.hour <= 5]
    if night_readings:
        avg_night_power = np.mean([r.power for r in night_readings])
        if avg_night_power > 100:
            monthly_waste = (avg_night_power / 1000) * 6 * 30  # 6 hours * 30 days
            insights.append(EfficiencyInsight(
                category="Phantom Load",
                message=f"Standby power consumption detected: {avg_night_power:.0f}W at night.",
                potential_savings=round(monthly_waste * 7.5, 2),
                priority="medium"
            ))
    
    return insights


@router.post("/score", response_model=EfficiencyResponse)
async def calculate_efficiency_score(request: EfficiencyRequest):
    """
    Calculate comprehensive efficiency score for a meter
    
    Components:
    - Power factor efficiency (30%)
    - Load profile consistency (30%)
    - Peak usage optimization (20%)
    - Power quality consistency (20%)
    """
    try:
        logger.info(f"Calculating efficiency for meter {request.meter_id}, readings={len(request.readings)}")
        
        if len(request.readings) < 24:
            raise HTTPException(
                status_code=400,
                detail="At least 24 readings (1 day) required for efficiency scoring"
            )
        
        # Extract data
        power_factors = [r.power_factor for r in request.readings]
        powers = [r.power for r in request.readings]
        
        # Calculate component scores
        pf_score = calculate_power_factor_score(power_factors)
        load_score = calculate_load_profile_score(powers)
        peak_score = calculate_peak_usage_score(request.readings)
        consistency_score = calculate_consistency_score(request.readings)
        
        # Calculate overall score (weighted average)
        overall_score = int(
            pf_score * 0.30 +
            load_score * 0.30 +
            peak_score * 0.20 +
            consistency_score * 0.20
        )
        
        breakdown = EfficiencyBreakdown(
            power_factor_score=pf_score,
            load_profile_score=load_score,
            peak_usage_score=peak_score,
            consistency_score=consistency_score
        )
        
        # Calculate energy metrics
        total_energy = sum([r.energy for r in request.readings])
        optimal_energy = total_energy * (overall_score / 100)
        wasted_energy = total_energy - optimal_energy
        cost_impact = wasted_energy * 7.5  # ₹7.5 per kWh
        
        # Generate insights
        insights = generate_insights(request.readings, breakdown, total_energy)
        
        # Generate recommendations
        recommendations = []
        if pf_score < 85:
            recommendations.append("Install power factor correction capacitors")
        if peak_score < 70:
            recommendations.append("Shift heavy appliances to off-peak hours (11 PM - 6 AM)")
        if consistency_score < 75:
            recommendations.append("Install voltage stabilizer to protect equipment")
        if load_score < 70:
            recommendations.append("Avoid simultaneous operation of high-power appliances")
        
        if overall_score >= 90:
            recommendations.append("Excellent! Maintain current usage patterns.")
        
        response = EfficiencyResponse(
            meter_id=request.meter_id,
            overall_score=overall_score,
            breakdown=breakdown,
            total_energy=round(total_energy, 3),
            optimal_energy=round(optimal_energy, 3),
            wasted_energy=round(wasted_energy, 3),
            cost_impact=round(cost_impact, 2),
            insights=insights,
            recommendations=recommendations
        )
        
        logger.info(f"Efficiency calculated: {overall_score}% for meter {request.meter_id}")
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Efficiency calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Efficiency calculation failed: {str(e)}")


@router.get("/health")
async def efficiency_health():
    """Health check for efficiency service"""
    return {
        "status": "healthy",
        "service": "efficiency_scoring",
        "components": ["power_factor", "load_profile", "peak_usage", "consistency"]
    }
