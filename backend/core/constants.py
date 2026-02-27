"""
Constants - Application-wide constants
"""

# User Roles
USER_ROLES = {
    'FARMER': 'farmer',
    'SARPANCH': 'sarpanch',
    'UTILITY': 'utility',
    'GOVERNMENT': 'government'
}

# Languages
LANGUAGES = {
    'ENGLISH': 'en',
    'HINDI': 'hi',
    'GUJARATI': 'gu'
}

# Meter Types
METER_TYPES = {
    'RESIDENTIAL': 'residential',
    'COMMERCIAL': 'commercial',
    'AGRICULTURAL': 'agricultural',
    'INDUSTRIAL': 'industrial'
}

# Meter Status
METER_STATUS = {
    'ACTIVE': 'active',
    'INACTIVE': 'inactive',
    'MAINTENANCE': 'maintenance',
    'FAULTY': 'faulty'
}

# Alert Types
ALERT_TYPES = {
    'VOLTAGE_SPIKE': 'voltage_spike',
    'VOLTAGE_DROP': 'voltage_drop',
    'OVERCURRENT': 'overcurrent',
    'PHANTOM_LOAD': 'phantom_load',
    'POWER_OUTAGE': 'power_outage',
    'MAINTENANCE_REQUIRED': 'maintenance_required',
    'TAMPER_DETECTION': 'tamper_detection',
    'METER_OFFLINE': 'meter_offline'
}

# Alert Severity
ALERT_SEVERITY = {
    'INFO': 'info',
    'WARNING': 'warning',
    'CRITICAL': 'critical',
    'EMERGENCY': 'emergency'
}

# Notification Channels
NOTIFICATION_CHANNELS = {
    'WHATSAPP': 'whatsapp',
    'SMS': 'sms',
    'EMAIL': 'email',
    'PUSH': 'push'
}

# Notification Status
NOTIFICATION_STATUS = {
    'PENDING': 'pending',
    'SENT': 'sent',
    'DELIVERED': 'delivered',
    'FAILED': 'failed',
    'READ': 'read'
}

# Bill Status
BILL_STATUS = {
    'DRAFT': 'draft',
    'PENDING': 'pending',
    'PAID': 'paid',
    'OVERDUE': 'overdue',
    'CANCELLED': 'cancelled'
}

# Payment Methods
PAYMENT_METHODS = {
    'UPI': 'upi',
    'CARD': 'card',
    'NET_BANKING': 'netbanking',
    'WALLET': 'wallet',
    'CASH': 'cash'
}

# Gujarat Tariff Structure (INR per kWh)
GUJARAT_TARIFF = {
    'SLAB_1_LIMIT': 100,
    'SLAB_1_RATE': 3.5,
    'SLAB_2_LIMIT': 250,
    'SLAB_2_RATE': 5.2,
    'SLAB_3_RATE': 7.5,
    'FIXED_CHARGE': 25.0
}

# Electrical Standards (India)
ELECTRICAL_STANDARDS = {
    'NOMINAL_VOLTAGE': 230.0,  # Volts
    'VOLTAGE_TOLERANCE': 6.0,  # ±6% (216-244V)
    'FREQUENCY': 50.0,  # Hz
    'FREQUENCY_TOLERANCE': 0.5,  # ±0.5 Hz
    'MIN_POWER_FACTOR': 0.85
}

# ML Model Thresholds
ML_THRESHOLDS = {
    'ANOMALY_CONFIDENCE': 0.7,
    'FORECAST_CONFIDENCE': 0.75,
    'MIN_TRAINING_SAMPLES': 100
}

# Cache Timeouts (seconds)
CACHE_TIMEOUTS = {
    'USER_PROFILE': 300,  # 5 minutes
    'METER_STATUS': 60,   # 1 minute
    'DASHBOARD_STATS': 120,  # 2 minutes
    'ANALYTICS': 600,  # 10 minutes
    'TARIFF_RATES': 3600  # 1 hour
}

# API Rate Limits (requests per minute)
RATE_LIMITS = {
    'ANON': 20,
    'USER': 100,
    'PREMIUM': 500,
    'ADMIN': 1000
}
