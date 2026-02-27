"""
Electricity Loss Simulator Service

Simulates transformer-to-house electricity readings with realistic loss scenarios:
- Normal transmission loss (2-5%)
- Voltage drops
- Power theft scenarios
- Equipment faults
- Line faults based on distance
"""

import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from .models import (
    Company, District, Village, Transformer, House,
    ElectricityReading, LossAlert
)


class ElectricitySimulator:
    """Simulates electricity distribution with loss detection"""

    # Configuration
    BASE_VOLTAGE = 230.0  # Standard voltage in India
    NORMAL_LOSS_MIN = 0.02  # 2% minimum normal loss
    NORMAL_LOSS_MAX = 0.05  # 5% maximum normal loss
    
    # Loss scenarios and their probabilities
    SCENARIOS = {
        'normal': 0.70,           # 70% normal readings
        'low_voltage': 0.08,      # 8% low voltage
        'high_loss': 0.10,        # 10% high loss (possible theft)
        'theft': 0.05,            # 5% theft suspected
        'equipment_fault': 0.04,  # 4% equipment issues
        'line_fault': 0.03,       # 3% line faults
    }

    def __init__(self):
        self.rate_per_kwh = Decimal('7.50')  # INR per kWh for loss calculation

    def generate_reading(self, house, scenario=None):
        """Generate a single electricity reading for a house"""
        transformer = house.transformer
        
        # Select scenario if not specified
        if scenario is None:
            scenario = self._select_scenario()
        
        # Base values from transformer
        voltage_sent = float(transformer.output_voltage)
        base_current = float(house.connected_load_kw) * 1000 / voltage_sent  # I = P/V
        
        # Apply scenario-specific modifications
        reading_data = self._apply_scenario(
            scenario, voltage_sent, base_current, house
        )
        
        return reading_data

    def _select_scenario(self):
        """Randomly select a scenario based on probabilities"""
        rand = random.random()
        cumulative = 0
        for scenario, probability in self.SCENARIOS.items():
            cumulative += probability
            if rand <= cumulative:
                return scenario
        return 'normal'

    def _apply_scenario(self, scenario, voltage_sent, base_current, house):
        """Apply scenario-specific modifications to generate reading"""
        
        # Calculate distance-based loss (longer lines = more loss)
        distance = float(house.transformer.houses.count()) * 50 + random.randint(20, 100)
        distance_loss_factor = 1 + (distance / 10000)  # Small increase per 100m
        
        if scenario == 'normal':
            # Normal 2-5% loss
            loss_pct = random.uniform(self.NORMAL_LOSS_MIN, self.NORMAL_LOSS_MAX)
            voltage_received = voltage_sent * (1 - loss_pct * 0.3)  # Voltage loss is smaller
            current_received = base_current * (1 - loss_pct * 0.1)
            status = 'normal'
            
        elif scenario == 'low_voltage':
            # Voltage drop - received voltage is significantly lower
            loss_pct = random.uniform(0.10, 0.15)  # 10-15% voltage drop
            voltage_received = voltage_sent * (1 - loss_pct)
            current_received = base_current * 1.05  # Current slightly higher to compensate
            status = 'low_voltage'
            
        elif scenario == 'high_loss':
            # High power loss - could be inefficiency or early theft signs
            loss_pct = random.uniform(0.08, 0.14)  # 8-14% loss
            voltage_received = voltage_sent * (1 - loss_pct * 0.4)
            current_received = base_current * (1 - loss_pct * 0.6)
            status = 'loss_detected'
            
        elif scenario == 'theft':
            # Suspected theft - significant power loss, voltage relatively stable
            loss_pct = random.uniform(0.15, 0.35)  # 15-35% loss
            voltage_received = voltage_sent * (1 - random.uniform(0.02, 0.05))
            current_received = base_current * (1 - loss_pct)  # Major current drop
            status = 'theft_suspected'
            
        elif scenario == 'equipment_fault':
            # Equipment fault - erratic readings
            loss_pct = random.uniform(0.05, 0.20)
            voltage_received = voltage_sent * random.uniform(0.85, 1.05)
            current_received = base_current * random.uniform(0.7, 1.2)
            status = 'equipment_fault'
            
        elif scenario == 'line_fault':
            # Line fault - major loss, proportional to distance
            loss_pct = random.uniform(0.10, 0.25) * distance_loss_factor
            voltage_received = voltage_sent * (1 - loss_pct * 0.6)
            current_received = base_current * (1 - loss_pct * 0.4)
            status = 'loss_detected'
        else:
            # Default normal
            loss_pct = random.uniform(self.NORMAL_LOSS_MIN, self.NORMAL_LOSS_MAX)
            voltage_received = voltage_sent * (1 - loss_pct * 0.3)
            current_received = base_current * (1 - loss_pct * 0.1)
            status = 'normal'

        # Calculate power
        power_factor = random.uniform(0.85, 0.98)
        power_sent = (voltage_sent * base_current * power_factor) / 1000  # kW
        power_received = (voltage_received * current_received * power_factor) / 1000  # kW
        
        # Calculate energy (assuming 1-hour interval)
        energy_sent = power_sent  # kWh (1 hour)
        energy_received = power_received  # kWh (1 hour)

        return {
            'house': house,
            'transformer': house.transformer,
            'voltage_sent': Decimal(str(round(voltage_sent, 2))),
            'voltage_received': Decimal(str(round(voltage_received, 2))),
            'current_sent': Decimal(str(round(base_current, 2))),
            'current_received': Decimal(str(round(current_received, 2))),
            'power_sent_kw': Decimal(str(round(power_sent, 3))),
            'power_received_kw': Decimal(str(round(power_received, 3))),
            'energy_sent_kwh': Decimal(str(round(energy_sent, 3))),
            'energy_received_kwh': Decimal(str(round(energy_received, 3))),
            'power_factor': Decimal(str(round(power_factor, 2))),
            'frequency': Decimal(str(round(random.uniform(49.8, 50.2), 2))),
            'line_distance_meters': Decimal(str(round(distance, 2))),
            'scenario': scenario,
            'expected_status': status,
        }

    @transaction.atomic
    def create_reading(self, house, scenario=None, timestamp=None):
        """Generate and save a reading, creating alert if needed"""
        reading_data = self.generate_reading(house, scenario)
        
        if timestamp is None:
            timestamp = timezone.now()
        
        # Create the reading
        reading = ElectricityReading.objects.create(
            house=reading_data['house'],
            transformer=reading_data['transformer'],
            voltage_sent=reading_data['voltage_sent'],
            voltage_received=reading_data['voltage_received'],
            current_sent=reading_data['current_sent'],
            current_received=reading_data['current_received'],
            power_sent_kw=reading_data['power_sent_kw'],
            power_received_kw=reading_data['power_received_kw'],
            energy_sent_kwh=reading_data['energy_sent_kwh'],
            energy_received_kwh=reading_data['energy_received_kwh'],
            power_factor=reading_data['power_factor'],
            frequency=reading_data['frequency'],
            line_distance_meters=reading_data['line_distance_meters'],
            reading_timestamp=timestamp,
        )
        
        # Create alert if anomaly detected
        if reading.is_anomaly:
            self._create_alert(reading)
        
        return reading

    def _create_alert(self, reading):
        """Create a loss alert for an anomalous reading"""
        house = reading.house
        transformer = reading.transformer
        village = transformer.village
        district = village.district
        
        # Determine alert type and severity
        alert_type, severity = self._determine_alert_type(reading)
        
        # Calculate estimated financial loss (daily projection)
        power_loss_daily = float(reading.power_loss_kw) * 24  # kWh per day
        estimated_loss = Decimal(str(power_loss_daily)) * self.rate_per_kwh * 30  # Monthly
        
        # Create title and description
        title = self._generate_alert_title(reading, alert_type)
        description = self._generate_alert_description(reading, alert_type)
        
        LossAlert.objects.create(
            reading=reading,
            house=house,
            transformer=transformer,
            village=village,
            district=district,
            alert_type=alert_type,
            severity=severity,
            title=title,
            description=description,
            voltage_loss=reading.voltage_loss,
            voltage_loss_percentage=reading.voltage_loss_percentage,
            power_loss_kw=reading.power_loss_kw,
            power_loss_percentage=reading.power_loss_percentage,
            estimated_financial_loss=estimated_loss,
        )

    def _determine_alert_type(self, reading):
        """Determine alert type and severity based on reading"""
        status = reading.status
        loss_pct = float(reading.power_loss_percentage)
        
        if status == 'theft_suspected' or loss_pct > 15:
            return LossAlert.AlertType.THEFT_SUSPECTED, LossAlert.AlertSeverity.CRITICAL
        elif status == 'low_voltage':
            return LossAlert.AlertType.VOLTAGE_DROP, LossAlert.AlertSeverity.WARNING
        elif status == 'high_voltage':
            return LossAlert.AlertType.EQUIPMENT_FAULT, LossAlert.AlertSeverity.WARNING
        elif status == 'equipment_fault':
            return LossAlert.AlertType.EQUIPMENT_FAULT, LossAlert.AlertSeverity.CRITICAL
        elif loss_pct > 10:
            return LossAlert.AlertType.POWER_LOSS, LossAlert.AlertSeverity.WARNING
        else:
            return LossAlert.AlertType.POWER_LOSS, LossAlert.AlertSeverity.INFO

    def _generate_alert_title(self, reading, alert_type):
        """Generate a descriptive alert title"""
        house = reading.house
        loss_pct = round(float(reading.power_loss_percentage), 1)
        
        titles = {
            'theft_suspected': f"⚠️ Theft Suspected at {house.consumer_id} - {loss_pct}% loss",
            'voltage_drop': f"⚡ Low Voltage at {house.consumer_id} - {reading.voltage_received}V",
            'equipment_fault': f"🔧 Equipment Fault at {house.consumer_id}",
            'power_loss': f"📉 Power Loss at {house.consumer_id} - {loss_pct}%",
            'overload': f"🔴 Overload at {house.consumer_id}",
            'line_fault': f"🔌 Line Fault affecting {house.consumer_id}",
        }
        return titles.get(alert_type, f"Alert at {house.consumer_id}")

    def _generate_alert_description(self, reading, alert_type):
        """Generate detailed alert description"""
        house = reading.house
        transformer = reading.transformer
        
        desc = f"""
Electricity Loss Detected

Location Details:
- Consumer: {house.consumer_name} ({house.consumer_id})
- Address: {house.address}
- Transformer: {transformer.transformer_id} ({transformer.name})
- Village: {transformer.village.name}
- District: {transformer.village.district.name}

Reading Details:
- Voltage Sent: {reading.voltage_sent}V
- Voltage Received: {reading.voltage_received}V
- Voltage Loss: {reading.voltage_loss}V ({reading.voltage_loss_percentage}%)
- Power Sent: {reading.power_sent_kw} kW
- Power Received: {reading.power_received_kw} kW
- Power Loss: {reading.power_loss_kw} kW ({reading.power_loss_percentage}%)
- Line Distance: {reading.line_distance_meters}m

Status: {reading.get_status_display()}
Timestamp: {reading.reading_timestamp}
        """.strip()
        
        return desc

    def simulate_all_houses(self, company=None, district=None, village=None, transformer=None):
        """Generate readings for multiple houses"""
        houses = House.objects.filter(is_active=True, connection_status='active')
        
        if transformer:
            houses = houses.filter(transformer=transformer)
        elif village:
            houses = houses.filter(transformer__village=village)
        elif district:
            houses = houses.filter(transformer__village__district=district)
        elif company:
            houses = houses.filter(transformer__village__district__company=company)
        
        readings = []
        for house in houses:
            reading = self.create_reading(house)
            readings.append(reading)
        
        return readings

    def simulate_historical_data(self, hours=24, houses=None):
        """Generate historical readings for analysis"""
        if houses is None:
            houses = House.objects.filter(is_active=True, connection_status='active')
        
        readings = []
        now = timezone.now()
        
        for hour in range(hours):
            timestamp = now - timedelta(hours=hours - hour)
            for house in houses:
                reading = self.create_reading(house, timestamp=timestamp)
                readings.append(reading)
        
        return readings


# Singleton instance
simulator = ElectricitySimulator()


def generate_sample_reading(house, scenario=None):
    """Convenience function to generate a single reading"""
    return simulator.create_reading(house, scenario)


def generate_all_readings(company=None):
    """Convenience function to generate readings for all houses"""
    return simulator.simulate_all_houses(company=company)


def generate_historical_readings(hours=24):
    """Convenience function to generate historical data"""
    return simulator.simulate_historical_data(hours=hours)
