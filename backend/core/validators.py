"""
Validators - Custom field validators
"""
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re


def validate_phone_number(value):
    """
    Validate Indian phone number format
    Must be 10 digits, optionally with +91 prefix
    """
    pattern = r'^(\+91)?[6-9]\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Invalid phone number. Must be 10 digits starting with 6-9, optionally with +91 prefix.',
            code='invalid_phone'
        )


def validate_meter_id(value):
    """
    Validate meter ID format: GJ-DISTRICT-XXXXX
    """
    pattern = r'^GJ-[A-Z]{3,6}-\d{5}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Invalid meter ID. Must be in format: GJ-DISTRICT-XXXXX',
            code='invalid_meter_id'
        )


def validate_voltage(value):
    """
    Validate voltage reading (must be positive, reasonable range)
    """
    if value < 0:
        raise ValidationError('Voltage cannot be negative', code='negative_voltage')
    if value > 500:
        raise ValidationError('Voltage exceeds maximum limit (500V)', code='voltage_too_high')


def validate_current(value):
    """
    Validate current reading (must be positive, reasonable range)
    """
    if value < 0:
        raise ValidationError('Current cannot be negative', code='negative_current')
    if value > 200:
        raise ValidationError('Current exceeds maximum limit (200A)', code='current_too_high')


def validate_power_factor(value):
    """
    Validate power factor (must be between 0 and 1)
    """
    if not (0 <= value <= 1):
        raise ValidationError(
            'Power factor must be between 0 and 1',
            code='invalid_power_factor'
        )


def validate_gps_coordinates(latitude, longitude):
    """
    Validate GPS coordinates for Gujarat region
    """
    # Gujarat approximate bounds
    if not (20.0 <= latitude <= 25.0):
        raise ValidationError('Latitude out of Gujarat range', code='invalid_latitude')
    if not (68.0 <= longitude <= 75.0):
        raise ValidationError('Longitude out of Gujarat range', code='invalid_longitude')


# Regex validators for common patterns
indian_pincode_validator = RegexValidator(
    regex=r'^\d{6}$',
    message='Invalid PIN code. Must be 6 digits.',
    code='invalid_pincode'
)

meter_serial_validator = RegexValidator(
    regex=r'^[A-Z0-9]{8,16}$',
    message='Invalid meter serial number. Must be 8-16 alphanumeric characters.',
    code='invalid_serial'
)

ifsc_code_validator = RegexValidator(
    regex=r'^[A-Z]{4}0[A-Z0-9]{6}$',
    message='Invalid IFSC code format.',
    code='invalid_ifsc'
)
