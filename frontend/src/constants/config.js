// Configuration constants for Gram Meter

// API Configuration
export const API_CONFIG = {
  // Replace with your actual Django backend URL
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 10000, // 10 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
};

// Cache Configuration
export const CACHE_CONFIG = {
  METER_DATA_KEY: 'gram_meter_data',
  ALERTS_KEY: 'gram_meter_alerts',
  LAST_SYNC_KEY: 'gram_meter_last_sync',
  LANGUAGE_KEY: 'gram_meter_language',
  MAX_AGE: 5 * 60 * 1000, // 5 minutes
};

// Polling Configuration (for real-time updates)
export const POLLING_CONFIG = {
  METER_DATA_INTERVAL: 5000, // 5 seconds (reduced from 3s)
  ALERTS_INTERVAL: 15000, // 15 seconds (reduced from 10s)
  ENABLE_POLLING: true,
};

// Efficiency Thresholds
export const EFFICIENCY_THRESHOLDS = {
  A_PLUS: 90,
  A: 80,
  B: 70,
  C: 60,
  D: 50,
};

// Anomaly Types
export const ANOMALY_TYPES = {
  VOLTAGE_SPIKE: 'voltage_spike',
  HIGH_USAGE: 'high_usage',
  PHANTOM_LOAD: 'phantom_load',
  PEAK_HOURS: 'peak_hours',
  APPLIANCE_FAULT: 'appliance_fault',
};

// Alert Severities
export const ALERT_SEVERITY = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
};

// Supported Languages
export const LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી' },
];

// Chart Colors (Mint & Emerald Theme)
export const CHART_COLORS = {
  primary: '#10b981',
  secondary: '#34d399',
  background: '#f0fdf4',
  grid: '#f1f5f9',
  text: '#64748b',
  gradient: {
    start: '#10b981',
    end: '#10b98100',
  },
};

// Mock Data (for fallback)
export const MOCK_METER_DATA = {
  current_power: 1.8,
  daily_cost: 45.20,
  efficiency_score: 94,
  efficiency_grade: 'A+',
  usage_history: [
    { time: '00:00', usage: 0.8 },
    { time: '02:00', usage: 0.6 },
    { time: '04:00', usage: 0.5 },
    { time: '06:00', usage: 1.2 },
    { time: '08:00', usage: 1.8 },
    { time: '10:00', usage: 2.4 },
    { time: '12:00', usage: 1.5 },
    { time: '14:00', usage: 3.1 },
    { time: '16:00', usage: 2.2 },
    { time: '18:00', usage: 2.6 },
    { time: '20:00', usage: 3.4 },
    { time: '22:00', usage: 2.1 },
  ],
  today_usage: 28.5,
  this_week_usage: 185.2,
  this_month_usage: 756.8,
  avg_daily_usage: 25.2,
};

export const MOCK_ALERTS = [
  {
    id: 1,
    type: ANOMALY_TYPES.VOLTAGE_SPIKE,
    severity: ALERT_SEVERITY.CRITICAL,
    message: 'Voltage spike detected',
    details: 'Spike detected at 14:00 PM. Check your water pump.',
    timestamp: new Date().toISOString(),
    acknowledged: false,
  },
  {
    id: 2,
    type: ANOMALY_TYPES.PEAK_HOURS,
    severity: ALERT_SEVERITY.MEDIUM,
    message: 'Peak hours detected',
    details: 'Rates are high right now. Reduce load.',
    timestamp: new Date().toISOString(),
    acknowledged: false,
  },
];
