from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MeterType(str, Enum):
    """Meter type enumeration"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    AGRICULTURAL = "agricultural"
    INDUSTRIAL = "industrial"


class AnomalyType(str, Enum):
    """Anomaly type enumeration"""
    VOLTAGE_SPIKE = "voltage_spike"
    VOLTAGE_DROP = "voltage_drop"
    OVERCURRENT = "overcurrent"
    PHANTOM_LOAD = "phantom_load"
    POWER_OUTAGE = "power_outage"


# ===== METER READING SCHEMAS =====

class MeterReadingInput(BaseModel):
    """Input schema for meter reading"""
    meter_id: str
    timestamp: datetime
    voltage: float = Field(..., ge=0, le=500)
    current: float = Field(..., ge=0, le=200)
    power: float = Field(..., ge=0)
    energy: float = Field(..., ge=0)
    power_factor: float = Field(default=0.95, ge=0, le=1)
    frequency: float = Field(default=50.0, ge=45, le=55)
    temperature: Optional[float] = None


class UniversalMeterData(BaseModel):
    """Universal schema for any meter format"""
    raw_data: Dict[str, Any]
    manufacturer: Optional[str] = None
    model: Optional[str] = None


# ===== FORECASTING SCHEMAS =====

class ForecastRequest(BaseModel):
    """Request schema for energy forecasting"""
    meter_id: str
    forecast_hours: int = Field(default=24, ge=1, le=168)  # Max 1 week
    historical_data: Optional[List[MeterReadingInput]] = None


class ForecastResult(BaseModel):
    """Result schema for energy forecast"""
    meter_id: str
    timestamp: datetime
    predicted_energy: float
    predicted_power: float
    confidence_score: float = Field(ge=0, le=1)
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    """Response schema for forecasting"""
    meter_id: str
    forecast_date: datetime
    forecasts: List[ForecastResult]
    model_version: str
    rmse: Optional[float] = None
    mae: Optional[float] = None


# ===== ANOMALY DETECTION SCHEMAS =====

class AnomalyRequest(BaseModel):
    """Request schema for anomaly detection"""
    meter_id: str
    readings: List[MeterReadingInput]
    sensitivity: float = Field(default=0.5, ge=0, le=1)


class AnomalyResult(BaseModel):
    """Result schema for detected anomaly"""
    timestamp: datetime
    is_anomaly: bool
    anomaly_type: Optional[AnomalyType] = None
    anomaly_score: float = Field(ge=0, le=1)
    severity: str  # info, warning, critical
    message: str
    recommended_action: str
    estimated_cost_impact: float


class AnomalyResponse(BaseModel):
    """Response schema for anomaly detection"""
    meter_id: str
    total_readings: int
    anomalies_detected: int
    anomalies: List[AnomalyResult]
    detection_rate: float


# ===== PARSER SCHEMAS =====

class ParserRequest(BaseModel):
    """Request schema for universal parser"""
    meter_data: UniversalMeterData


class ParsedReading(BaseModel):
    """Parsed meter reading in standard format"""
    meter_id: str
    timestamp: datetime
    voltage: float
    current: float
    power: float
    energy: float
    power_factor: float
    frequency: float
    temperature: Optional[float] = None
    metadata: Dict[str, Any] = {}


class ParserResponse(BaseModel):
    """Response schema for parser"""
    success: bool
    parsed_reading: Optional[ParsedReading] = None
    error: Optional[str] = None
    manufacturer_detected: Optional[str] = None


# ===== EFFICIENCY SCORING SCHEMAS =====

class EfficiencyRequest(BaseModel):
    """Request schema for efficiency scoring"""
    meter_id: str
    readings: List[MeterReadingInput]
    meter_type: MeterType = MeterType.RESIDENTIAL


class EfficiencyBreakdown(BaseModel):
    """Breakdown of efficiency components"""
    power_factor_score: int = Field(ge=0, le=100)
    load_profile_score: int = Field(ge=0, le=100)
    peak_usage_score: int = Field(ge=0, le=100)
    consistency_score: int = Field(ge=0, le=100)


class EfficiencyInsight(BaseModel):
    """Efficiency improvement insight"""
    category: str
    message: str
    potential_savings: float  # in ₹
    priority: str  # low, medium, high


class EfficiencyResponse(BaseModel):
    """Response schema for efficiency scoring"""
    meter_id: str
    overall_score: int = Field(ge=0, le=100)
    breakdown: EfficiencyBreakdown
    total_energy: float
    optimal_energy: float
    wasted_energy: float
    cost_impact: float
    insights: List[EfficiencyInsight]
    recommendations: List[str]


# ===== ERROR SCHEMA =====

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
