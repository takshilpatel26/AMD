// Real-time data simulation hook - Creates realistic meter data updates
import { useState, useEffect, useCallback, useRef } from 'react';

// Simulates real-time meter readings with realistic fluctuations
export const useRealtimeData = (initialData = {}, updateInterval = 2000) => {
  const [data, setData] = useState({
    voltage: initialData.voltage || 230,
    current: initialData.current || 4.5,
    power: initialData.power || 1035,
    energy: initialData.energy || 245.67,
    powerFactor: initialData.powerFactor || 0.95,
    frequency: initialData.frequency || 50.0,
    pumpActive: initialData.pumpActive || false,
    timestamp: new Date(),
    isLive: true,
  });
  
  const [history, setHistory] = useState([]);
  const iterationRef = useRef(0);
  const cumulativeEnergyRef = useRef(initialData.energy || 245.67);

  // Generate realistic fluctuations
  const generateReading = useCallback(() => {
    iterationRef.current += 1;
    const iteration = iterationRef.current;
    const now = new Date();
    const hour = now.getHours();
    
    // Every 15th reading, simulate a voltage event (for demo)
    const isDemoEvent = iteration % 15 === 0;
    
    let voltage, power, pumpActive;
    
    if (isDemoEvent) {
      // Voltage surge scenario
      voltage = 286 + Math.random() * 19; // 286-305V
      pumpActive = true;
      power = 7500 + Math.random() * 500; // High power spike
    } else {
      // Normal operation with time-based patterns
      const baseVoltage = 230;
      // Voltage slightly lower during peak hours (6-9 PM)
      const peakHourDrop = (hour >= 18 && hour <= 21) ? -5 : 0;
      voltage = baseVoltage + peakHourDrop + (Math.random() * 8 - 4);
      
      // Pump more likely during day (6 AM - 6 PM)
      const pumpProbability = (hour >= 6 && hour <= 18) ? 0.4 : 0.15;
      pumpActive = Math.random() < pumpProbability;
      
      // Power based on pump status
      const basePower = pumpActive ? 4500 : 200;
      power = basePower + (Math.random() * 700 - 350);
    }
    
    // Calculate current from power and voltage
    const current = power / voltage;
    
    // Power factor varies slightly
    const powerFactor = 0.92 + Math.random() * 0.07;
    
    // Frequency stays near 50Hz
    const frequency = 49.95 + Math.random() * 0.1;
    
    // Energy accumulation (accelerated for demo)
    const energyIncrement = (power * (updateInterval / 3600000)) * 60; // 60x acceleration
    cumulativeEnergyRef.current += energyIncrement / 1000; // Convert to kWh
    
    return {
      voltage: Math.round(voltage * 10) / 10,
      current: Math.round(current * 100) / 100,
      power: Math.round(power),
      energy: Math.round(cumulativeEnergyRef.current * 100) / 100,
      powerFactor: Math.round(powerFactor * 100) / 100,
      frequency: Math.round(frequency * 100) / 100,
      pumpActive,
      timestamp: now,
      isLive: true,
      isAnomaly: isDemoEvent,
      voltageStability: Math.abs(230 - voltage),
    };
  }, [updateInterval]);

  useEffect(() => {
    const interval = setInterval(() => {
      const newReading = generateReading();
      setData(newReading);
      
      // Keep last 50 readings for charts
      setHistory(prev => {
        const updated = [...prev, newReading];
        return updated.slice(-50);
      });
    }, updateInterval);

    return () => clearInterval(interval);
  }, [generateReading, updateInterval]);

  return { data, history, isLive: true };
};

// Hook for multiple meters with individual fluctuations
export const useMultiMeterData = (meterCount = 5, updateInterval = 3000) => {
  const [meters, setMeters] = useState([]);
  
  useEffect(() => {
    // Initialize meters
    const initialMeters = Array.from({ length: meterCount }, (_, i) => ({
      id: i + 1,
      meter_id: `GJ-ANAND-${String(i + 1).padStart(3, '0')}`,
      name: `Meter ${i + 1}`,
      location: ['Rampur', 'Sundarpur', 'Govindpura', 'Krishnanagar', 'Shantinagar'][i % 5],
      status: 'active',
      voltage: 228 + Math.random() * 4,
      current: 3 + Math.random() * 4,
      power: 800 + Math.random() * 800,
      energy_today: 5 + Math.random() * 10,
      efficiency: 75 + Math.random() * 20,
      last_reading_at: new Date(),
    }));
    setMeters(initialMeters);
  }, [meterCount]);

  useEffect(() => {
    const interval = setInterval(() => {
      setMeters(prev => prev.map(meter => {
        const voltageChange = (Math.random() - 0.5) * 2;
        const powerChange = (Math.random() - 0.5) * 100;
        const newVoltage = Math.max(220, Math.min(240, meter.voltage + voltageChange));
        const newPower = Math.max(100, meter.power + powerChange);
        
        // Random status changes (rare)
        let status = meter.status;
        if (Math.random() < 0.02) {
          status = ['active', 'active', 'active', 'offline', 'alert'][Math.floor(Math.random() * 5)];
        }
        
        return {
          ...meter,
          voltage: Math.round(newVoltage * 10) / 10,
          current: Math.round((newPower / newVoltage) * 100) / 100,
          power: Math.round(newPower),
          energy_today: Math.round((meter.energy_today + newPower * 0.0001) * 100) / 100,
          efficiency: Math.max(50, Math.min(98, meter.efficiency + (Math.random() - 0.5) * 2)),
          status,
          last_reading_at: new Date(),
        };
      }));
    }, updateInterval);

    return () => clearInterval(interval);
  }, [updateInterval]);

  return meters;
};

// Hook for real-time alerts
export const useRealtimeAlerts = (updateInterval = 10000) => {
  const [alerts, setAlerts] = useState([]);
  const alertIdRef = useRef(1);

  const alertTypes = [
    { type: 'voltage', priority: 'high', title: 'Voltage Fluctuation', message: 'Voltage exceeded safe threshold' },
    { type: 'power', priority: 'medium', title: 'High Power Usage', message: 'Unusual power consumption detected' },
    { type: 'current', priority: 'critical', title: 'Current Spike', message: 'Sudden current increase detected' },
    { type: 'efficiency', priority: 'low', title: 'Low Efficiency', message: 'Pump efficiency below optimal' },
  ];

  useEffect(() => {
    // Add initial alerts
    const initialAlerts = [
      {
        id: alertIdRef.current++,
        type: 'voltage',
        priority: 'high',
        title: 'Voltage Fluctuation Detected',
        message: 'Voltage reached 287V on Meter GJ-ANAND-001',
        meter_id: 'GJ-ANAND-001',
        meter_name: 'Meter 1 - Rampur',
        status: 'active',
        created_at: new Date(Date.now() - 300000),
      },
      {
        id: alertIdRef.current++,
        type: 'power',
        priority: 'medium',
        title: 'High Power Consumption',
        message: 'Power usage 40% above normal',
        meter_id: 'GJ-ANAND-003',
        meter_name: 'Meter 3 - Govindpura',
        status: 'active',
        created_at: new Date(Date.now() - 600000),
      },
    ];
    setAlerts(initialAlerts);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      // Random chance to add new alert
      if (Math.random() < 0.15) {
        const template = alertTypes[Math.floor(Math.random() * alertTypes.length)];
        const meterNum = Math.floor(Math.random() * 5) + 1;
        
        const newAlert = {
          id: alertIdRef.current++,
          ...template,
          meter_id: `GJ-ANAND-${String(meterNum).padStart(3, '0')}`,
          meter_name: `Meter ${meterNum}`,
          status: 'active',
          created_at: new Date(),
        };
        
        setAlerts(prev => [newAlert, ...prev].slice(0, 20));
      }
    }, updateInterval);

    return () => clearInterval(interval);
  }, [updateInterval]);

  const acknowledgeAlert = (alertId) => {
    setAlerts(prev => prev.map(a => 
      a.id === alertId ? { ...a, status: 'acknowledged' } : a
    ));
  };

  const resolveAlert = (alertId) => {
    setAlerts(prev => prev.map(a => 
      a.id === alertId ? { ...a, status: 'resolved' } : a
    ));
  };

  return { alerts, acknowledgeAlert, resolveAlert };
};

// Hook for analytics data with trends
export const useAnalyticsTrends = () => {
  const [trends, setTrends] = useState({
    consumption: [],
    efficiency: [],
    cost: [],
    carbon: [],
  });

  useEffect(() => {
    // Generate 30 days of historical data
    const now = new Date();
    const consumptionData = [];
    const efficiencyData = [];
    const costData = [];
    const carbonData = [];

    for (let i = 29; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const dateStr = date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
      
      // Base values with weekly patterns
      const dayOfWeek = date.getDay();
      const weekendFactor = (dayOfWeek === 0 || dayOfWeek === 6) ? 0.7 : 1;
      
      const baseConsumption = 8 + Math.random() * 4;
      const consumption = baseConsumption * weekendFactor;
      const efficiency = 70 + Math.random() * 25;
      const cost = consumption * 5.5;
      const carbon = consumption * 0.82; // kg CO2 per kWh

      consumptionData.push({ date: dateStr, value: Math.round(consumption * 100) / 100, fullDate: date });
      efficiencyData.push({ date: dateStr, value: Math.round(efficiency), fullDate: date });
      costData.push({ date: dateStr, value: Math.round(cost * 100) / 100, fullDate: date });
      carbonData.push({ date: dateStr, value: Math.round(carbon * 100) / 100, fullDate: date });
    }

    setTrends({
      consumption: consumptionData,
      efficiency: efficiencyData,
      cost: costData,
      carbon: carbonData,
    });
  }, []);

  return trends;
};

// Hook for billing data with real-time calculation
export const useBillingData = () => {
  const [billing, setBilling] = useState({
    currentMonth: {
      units: 0,
      amount: 0,
      dueDate: null,
      status: 'pending',
    },
    bills: [],
    invoices: [],
  });
  
  const [liveUnits, setLiveUnits] = useState(0);

  // Gujarat Agricultural Electricity Tariff Slabs (2024-25)
  const calculateBill = (units) => {
    // Slab 1: 0-100 units @ ₹3.50/unit
    // Slab 2: 101-250 units @ ₹5.20/unit  
    // Slab 3: 251+ units @ ₹7.50/unit
    // Fixed charges: ₹50/month
    // Electricity duty: 15%
    
    let baseAmount = 0;
    if (units <= 100) {
      baseAmount = units * 3.5;
    } else if (units <= 250) {
      baseAmount = 100 * 3.5 + (units - 100) * 5.2;
    } else {
      baseAmount = 100 * 3.5 + 150 * 5.2 + (units - 250) * 7.5;
    }
    
    const fixedCharges = 50;
    const electricityDuty = baseAmount * 0.15;
    
    return {
      baseAmount: Math.round(baseAmount),
      fixedCharges,
      electricityDuty: Math.round(electricityDuty),
      total: Math.round(baseAmount + fixedCharges + electricityDuty)
    };
  };

  useEffect(() => {
    const now = new Date();
    const dayOfMonth = now.getDate();
    
    // Calculate current month usage based on day of month
    // Assuming ~8 kWh per day average for agricultural meter
    const baseUnits = dayOfMonth * 8 + Math.random() * 20;
    setLiveUnits(Math.round(baseUnits));
    
    const currentBill = calculateBill(baseUnits);
    
    // Generate past 6 months bills
    const pastBills = [];
    for (let i = 1; i <= 6; i++) {
      const billDate = new Date(now);
      billDate.setMonth(billDate.getMonth() - i);
      
      // Seasonal variation - summer months higher usage
      const month = billDate.getMonth();
      const seasonalFactor = (month >= 3 && month <= 6) ? 1.3 : (month >= 10 || month <= 1) ? 0.8 : 1;
      const units = Math.round((150 + Math.random() * 100) * seasonalFactor);
      const billCalc = calculateBill(units);
      
      pastBills.push({
        id: i,
        bill_number: `BILL-${billDate.getFullYear()}${String(billDate.getMonth() + 1).padStart(2, '0')}`,
        month: billDate.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' }),
        units_consumed: units,
        base_amount: billCalc.baseAmount,
        fixed_charges: billCalc.fixedCharges,
        electricity_duty: billCalc.electricityDuty,
        amount: billCalc.total,
        due_date: new Date(billDate.getFullYear(), billDate.getMonth() + 1, 15),
        status: 'paid',
        payment_date: new Date(billDate.getFullYear(), billDate.getMonth() + 1, 10),
        created_at: billDate,
      });
    }

    setBilling({
      currentMonth: {
        units: Math.round(baseUnits),
        baseAmount: currentBill.baseAmount,
        fixedCharges: currentBill.fixedCharges,
        electricityDuty: currentBill.electricityDuty,
        amount: currentBill.total,
        dueDate: new Date(now.getFullYear(), now.getMonth() + 1, 15),
        status: 'pending',
        daysRemaining: Math.max(0, 15 - dayOfMonth + new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()),
      },
      bills: pastBills,
      invoices: pastBills.map(b => ({
        ...b,
        invoice_number: b.bill_number.replace('BILL', 'INV'),
      })),
    });
  }, []);

  // Update live units every 10 seconds to simulate meter running
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveUnits(prev => {
        const newUnits = prev + (Math.random() * 0.05); // Add small increment
        const newBill = calculateBill(newUnits);
        setBilling(b => ({
          ...b,
          currentMonth: {
            ...b.currentMonth,
            units: Math.round(newUnits * 100) / 100,
            baseAmount: newBill.baseAmount,
            amount: newBill.total,
          }
        }));
        return newUnits;
      });
    }, 10000);
    
    return () => clearInterval(interval);
  }, []);

  return billing;
};

export default useRealtimeData;
