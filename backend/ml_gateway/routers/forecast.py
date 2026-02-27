from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import numpy as np
from typing import List
from ..schemas import ForecastRequest, ForecastResponse, ForecastResult, MeterReadingInput
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def simple_moving_average_forecast(historical_data: List[MeterReadingInput], hours: int) -> List[ForecastResult]:
    """
    Simple Moving Average forecast for energy consumption
    
    In production, replace with ARIMA, Prophet, or LSTM models
    """
    if not historical_data:
        raise ValueError("No historical data provided")
    
    # Extract energy values
    energy_values = [reading.power for reading in historical_data[-24:]]  # Last 24 hours
    
    # Calculate moving average
    window_size = min(12, len(energy_values))
    moving_avg = np.mean(energy_values[-window_size:])
    std_dev = np.std(energy_values[-window_size:])
    
    # Generate forecasts
    forecasts = []
    last_timestamp = historical_data[-1].timestamp
    
    for hour in range(1, hours + 1):
        forecast_time = last_timestamp + timedelta(hours=hour)
        
        # Add some variation (simulated)
        variation = np.random.normal(0, std_dev * 0.1)
        predicted_power = max(0, moving_avg + variation)
        predicted_energy = predicted_power / 1000  # Convert to kWh
        
        # Calculate confidence (decreases with forecast horizon)
        confidence = max(0.5, 1 - (hour / hours) * 0.3)
        
        # Calculate prediction intervals
        margin = std_dev * 1.96 * (1 + hour / hours)
        lower_bound = max(0, predicted_power - margin)
        upper_bound = predicted_power + margin
        
        forecasts.append(ForecastResult(
            meter_id=historical_data[0].meter_id,
            timestamp=forecast_time,
            predicted_energy=round(predicted_energy, 3),
            predicted_power=round(predicted_power, 2),
            confidence_score=round(confidence, 3),
            lower_bound=round(lower_bound, 2),
            upper_bound=round(upper_bound, 2)
        ))
    
    return forecasts


@router.post("/predict", response_model=ForecastResponse)
async def predict_energy_consumption(request: ForecastRequest):
    """
    Predict energy consumption for next N hours
    
    This uses a simple moving average. In production:
    - Use ARIMA/SARIMA for time series forecasting
    - Use Prophet for seasonal patterns
    - Use LSTM/GRU for deep learning approach
    """
    try:
        logger.info(f"Forecasting for meter {request.meter_id}, hours={request.forecast_hours}")
        
        if not request.historical_data or len(request.historical_data) < 12:
            raise HTTPException(
                status_code=400,
                detail="At least 12 historical readings required for forecasting"
            )
        
        # Generate forecasts
        forecasts = simple_moving_average_forecast(
            request.historical_data,
            request.forecast_hours
        )
        
        # Calculate metrics (mocked for demo)
        rmse = np.random.uniform(0.05, 0.15)  # 5-15% error
        mae = np.random.uniform(0.03, 0.10)   # 3-10% error
        
        response = ForecastResponse(
            meter_id=request.meter_id,
            forecast_date=datetime.now(),
            forecasts=forecasts,
            model_version="simple_ma_v1.0",
            rmse=round(rmse, 4),
            mae=round(mae, 4)
        )
        
        logger.info(f"Forecast generated: {len(forecasts)} predictions")
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Forecast error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Forecasting failed: {str(e)}")


@router.get("/health")
async def forecast_health():
    """Health check for forecast service"""
    return {"status": "healthy", "service": "forecasting", "model": "simple_ma_v1.0"}
