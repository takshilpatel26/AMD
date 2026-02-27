from fastapi import APIRouter, HTTPException
from datetime import datetime
import json
import logging
from ..schemas import ParserRequest, ParserResponse, ParsedReading

router = APIRouter()
logger = logging.getLogger(__name__)


def parse_generic_meter(raw_data: dict) -> ParsedReading:
    """Parse generic/unknown meter format"""
    # Try common field names
    meter_id = raw_data.get('meter_id') or raw_data.get('id') or raw_data.get('device_id')
    
    # Timestamp parsing
    timestamp_raw = raw_data.get('timestamp') or raw_data.get('time') or raw_data.get('datetime')
    if isinstance(timestamp_raw, str):
        timestamp = datetime.fromisoformat(timestamp_raw.replace('Z', '+00:00'))
    else:
        timestamp = datetime.now()
    
    # Extract electrical parameters
    voltage = float(raw_data.get('voltage') or raw_data.get('v') or raw_data.get('V') or 230.0)
    current = float(raw_data.get('current') or raw_data.get('i') or raw_data.get('I') or raw_data.get('amp') or 0.0)
    power = float(raw_data.get('power') or raw_data.get('p') or raw_data.get('P') or raw_data.get('watt') or 0.0)
    energy = float(raw_data.get('energy') or raw_data.get('kwh') or raw_data.get('kWh') or 0.0)
    power_factor = float(raw_data.get('power_factor') or raw_data.get('pf') or raw_data.get('PF') or 0.95)
    frequency = float(raw_data.get('frequency') or raw_data.get('freq') or raw_data.get('hz') or 50.0)
    temperature = raw_data.get('temperature') or raw_data.get('temp')
    
    if temperature:
        temperature = float(temperature)
    
    return ParsedReading(
        meter_id=meter_id,
        timestamp=timestamp,
        voltage=voltage,
        current=current,
        power=power,
        energy=energy,
        power_factor=power_factor,
        frequency=frequency,
        temperature=temperature,
        metadata={"raw_keys": list(raw_data.keys())}
    )


def parse_tata_power_meter(raw_data: dict) -> ParsedReading:
    """Parse Tata Power smart meter format"""
    return ParsedReading(
        meter_id=raw_data['device_id'],
        timestamp=datetime.fromisoformat(raw_data['reading_time']),
        voltage=raw_data['volt'],
        current=raw_data['amp'],
        power=raw_data['active_power_w'],
        energy=raw_data['cumulative_kwh'],
        power_factor=raw_data.get('pf', 0.95),
        frequency=raw_data.get('freq_hz', 50.0),
        temperature=raw_data.get('temp_c'),
        metadata={"manufacturer": "Tata Power", "model": raw_data.get('model')}
    )


def parse_bescom_meter(raw_data: dict) -> ParsedReading:
    """Parse BESCOM smart meter format"""
    return ParsedReading(
        meter_id=raw_data['meter_number'],
        timestamp=datetime.strptime(raw_data['timestamp'], '%Y-%m-%d %H:%M:%S'),
        voltage=raw_data['voltage_v'],
        current=raw_data['current_a'],
        power=raw_data['power_w'],
        energy=raw_data['total_energy_kwh'],
        power_factor=raw_data.get('power_factor', 0.95),
        frequency=raw_data.get('frequency', 50.0),
        temperature=None,
        metadata={"manufacturer": "BESCOM", "zone": raw_data.get('zone')}
    )


def parse_secure_meter(raw_data: dict) -> ParsedReading:
    """Parse Secure Meters (Common Indian manufacturer) format"""
    return ParsedReading(
        meter_id=raw_data['serial_no'],
        timestamp=datetime.fromtimestamp(raw_data['unix_time']),
        voltage=raw_data['v_phase_a'],
        current=raw_data['i_phase_a'],
        power=raw_data['active_power'],
        energy=raw_data['kwh_import'],
        power_factor=raw_data['pf'],
        frequency=raw_data['frequency'],
        temperature=raw_data.get('meter_temp'),
        metadata={"manufacturer": "Secure Meters", "firmware": raw_data.get('fw_version')}
    )


@router.post("/parse", response_model=ParserResponse)
async def parse_meter_data(request: ParserRequest):
    """
    Universal parser for different smart meter formats
    
    Supports:
    - Tata Power meters
    - BESCOM meters
    - Secure Meters
    - Generic JSON format
    """
    try:
        raw_data = request.meter_data.raw_data
        manufacturer = request.meter_data.manufacturer
        
        logger.info(f"Parsing meter data, manufacturer={manufacturer}")
        
        # Auto-detect manufacturer if not provided
        if not manufacturer:
            if 'device_id' in raw_data and 'reading_time' in raw_data:
                manufacturer = "Tata Power"
            elif 'meter_number' in raw_data and 'zone' in raw_data:
                manufacturer = "BESCOM"
            elif 'serial_no' in raw_data and 'unix_time' in raw_data:
                manufacturer = "Secure Meters"
            else:
                manufacturer = "Generic"
        
        # Parse based on manufacturer
        if manufacturer == "Tata Power":
            parsed = parse_tata_power_meter(raw_data)
        elif manufacturer == "BESCOM":
            parsed = parse_bescom_meter(raw_data)
        elif manufacturer == "Secure Meters":
            parsed = parse_secure_meter(raw_data)
        else:
            parsed = parse_generic_meter(raw_data)
        
        response = ParserResponse(
            success=True,
            parsed_reading=parsed,
            manufacturer_detected=manufacturer
        )
        
        logger.info(f"Successfully parsed meter data: {parsed.meter_id}")
        return response
        
    except KeyError as e:
        logger.error(f"Missing required field: {str(e)}")
        return ParserResponse(
            success=False,
            error=f"Missing required field: {str(e)}",
            manufacturer_detected=manufacturer
        )
    except Exception as e:
        logger.error(f"Parsing error: {str(e)}")
        return ParserResponse(
            success=False,
            error=f"Parsing failed: {str(e)}"
        )


@router.get("/supported-manufacturers")
async def get_supported_manufacturers():
    """Get list of supported meter manufacturers"""
    return {
        "manufacturers": [
            {
                "name": "Tata Power",
                "models": ["TP-SM-100", "TP-SM-200"],
                "supported": True
            },
            {
                "name": "BESCOM",
                "models": ["BESCOM-SMART-V1", "BESCOM-SMART-V2"],
                "supported": True
            },
            {
                "name": "Secure Meters",
                "models": ["SM-100", "SM-200", "SM-300"],
                "supported": True
            },
            {
                "name": "Generic",
                "models": ["Any JSON format"],
                "supported": True
            }
        ]
    }


@router.get("/health")
async def parser_health():
    """Health check for parser service"""
    return {
        "status": "healthy",
        "service": "universal_parser",
        "supported_formats": ["Tata Power", "BESCOM", "Secure Meters", "Generic"]
    }
