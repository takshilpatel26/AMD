"""
Utility Functions - Helper functions used across the project
"""
from decimal import Decimal
from typing import Dict, Any, Optional
import random
import string
from django.utils import timezone
from datetime import timedelta


def generate_meter_id(district: str, village: str) -> str:
    """
    Generate unique meter ID in format: GJ-DISTRICT-XXXXX
    
    Args:
        district: District name (e.g., "ANAND")
        village: Village name (e.g., "BORSAD")
        
    Returns:
        Meter ID string (e.g., "GJ-ANAND-00123")
    """
    district_code = district.upper().replace(" ", "")[:6]
    random_num = ''.join(random.choices(string.digits, k=5))
    return f"GJ-{district_code}-{random_num}"


def calculate_power_factor(voltage: float, current: float, power: float) -> float:
    """
    Calculate power factor from voltage, current, and active power
    
    Args:
        voltage: Voltage in V
        current: Current in A
        power: Active power in W
        
    Returns:
        Power factor (0-1)
    """
    if voltage == 0 or current == 0:
        return 0.0
    
    apparent_power = voltage * current
    if apparent_power == 0:
        return 0.0
    
    pf = min(1.0, abs(power / apparent_power))
    return round(pf, 3)


def calculate_energy(power_w: float, duration_seconds: float) -> float:
    """
    Calculate energy consumption in kWh
    
    Args:
        power_w: Power in watts
        duration_seconds: Duration in seconds
        
    Returns:
        Energy in kWh
    """
    power_kw = power_w / 1000
    duration_hours = duration_seconds / 3600
    energy_kwh = power_kw * duration_hours
    return round(energy_kwh, 4)


def get_tariff_cost(units: float, state: str = "gujarat") -> Decimal:
    """
    Calculate electricity cost based on state tariff
    
    Args:
        units: Energy consumption in kWh
        state: State name (lowercase)
        
    Returns:
        Total cost in INR
    """
    # Gujarat domestic tariff structure
    tariff = {
        "slab_1": {"limit": 100, "rate": 3.5},
        "slab_2": {"limit": 250, "rate": 5.2},
        "slab_3": {"rate": 7.5}
    }
    
    total_cost = Decimal(0)
    remaining = units
    
    # Slab 1: 0-100 units
    if remaining > 0:
        consumed = min(remaining, tariff["slab_1"]["limit"])
        total_cost += Decimal(consumed) * Decimal(str(tariff["slab_1"]["rate"]))
        remaining -= consumed
    
    # Slab 2: 101-250 units
    if remaining > 0:
        consumed = min(remaining, tariff["slab_2"]["limit"] - tariff["slab_1"]["limit"])
        total_cost += Decimal(consumed) * Decimal(str(tariff["slab_2"]["rate"]))
        remaining -= consumed
    
    # Slab 3: 251+ units
    if remaining > 0:
        total_cost += Decimal(remaining) * Decimal(str(tariff["slab_3"]["rate"]))
    
    return total_cost.quantize(Decimal('0.01'))


def get_efficiency_grade(score: float) -> str:
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
    elif score >= 85:
        return "A-"
    elif score >= 80:
        return "B+"
    elif score >= 75:
        return "B"
    elif score >= 70:
        return "B-"
    elif score >= 65:
        return "C+"
    elif score >= 60:
        return "C"
    elif score >= 55:
        return "C-"
    elif score >= 50:
        return "D"
    else:
        return "F"


def translate_message(message: str, language: str) -> str:
    """
    Translate common alert messages to Hindi/Gujarati
    
    Args:
        message: English message
        language: Target language ('hi' or 'gu')
        
    Returns:
        Translated message
    """
    translations = {
        "hi": {  # Hindi
            "High voltage detected": "उच्च वोल्टेज का पता चला",
            "Low voltage detected": "कम वोल्टेज का पता चला",
            "Power outage": "बिजली बंद हो गई",
            "Overcurrent detected": "अधिक करंट का पता चला",
            "Phantom load detected": "रात में बिजली का उपयोग",
            "Meter offline": "मीटर ऑफलाइन है",
            "Check immediately": "तुरंत जांचें",
            "Contact utility": "बिजली विभाग से संपर्क करें"
        },
        "gu": {  # Gujarati
            "High voltage detected": "ઊંચું વોલ્ટેજ મળ્યું",
            "Low voltage detected": "ઓછું વોલ્ટેજ મળ્યું",
            "Power outage": "વીજ બંધ થઈ",
            "Overcurrent detected": "વધારે કરંટ મળ્યું",
            "Phantom load detected": "રાત્રે વીજ વપરાશ",
            "Meter offline": "મીટર ઓફલાઇન છે",
            "Check immediately": "તાત્કાલિક તપાસો",
            "Contact utility": "વીજ વિભાગને સંપર્ક કરો"
        }
    }
    
    if language not in translations:
        return message
    
    # Try to translate each part
    translated = message
    for eng, trans in translations[language].items():
        if eng.lower() in message.lower():
            translated = translated.replace(eng, trans)
    
    return translated


def get_date_range(period: str) -> tuple:
    """
    Get start and end dates for a period
    
    Args:
        period: 'today', 'week', 'month', 'year'
        
    Returns:
        Tuple of (start_date, end_date)
    """
    now = timezone.now()
    
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'week':
        start = now - timedelta(days=7)
        end = now
    elif period == 'month':
        start = now - timedelta(days=30)
        end = now
    elif period == 'year':
        start = now - timedelta(days=365)
        end = now
    else:
        start = now - timedelta(days=1)
        end = now
    
    return start, end


def format_indian_currency(amount: Decimal) -> str:
    """
    Format amount in Indian currency style (₹1,23,456.78)
    
    Args:
        amount: Amount in INR
        
    Returns:
        Formatted string
    """
    amount_str = f"{amount:.2f}"
    parts = amount_str.split('.')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else "00"
    
    # Indian number system: last 3 digits, then groups of 2
    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        
        # Group remaining digits in pairs from right to left
        groups = []
        while remaining:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        
        formatted = ','.join(reversed(groups)) + ',' + last_three
    
    return f"₹{formatted}.{decimal_part}"
