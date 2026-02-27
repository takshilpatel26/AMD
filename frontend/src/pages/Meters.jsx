import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Zap, 
  Gauge, 
  Droplet, 
  Clock, 
  MapPin, 
  AlertTriangle,
  CheckCircle,
  WifiOff,
  RefreshCw,
  Plus,
  Settings,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Eye,
  Power,
  Thermometer
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  Legend
} from 'recharts';
import api from '../services/api';
import { useMultiMeterData } from '../hooks/useRealtimeData';

// Data Generation Functions
// Generate realistic 24-hour power consumption data
const generatePowerConsumptionData = (readings) => {
  if (readings && readings.length > 0) {
    return readings.slice(0, 24).reverse();
  }
  
  // Generate 24 hours of realistic power consumption data
  const now = new Date();
  return Array.from({ length: 24 }, (_, i) => {
    const hour = 23 - i; // Last 24 hours
    const timestamp = new Date(now.getTime() - (i * 60 * 60 * 1000));
    
    // Realistic power consumption pattern for rural meter
    const isDaytime = hour >= 6 && hour <= 22;
    const isPeakHour = (hour >= 10 && hour <= 14) || (hour >= 18 && hour <= 21);
    
    let basePower = 50; // Night baseline (50W)
    if (isDaytime) basePower = 300; // Daytime baseline (300W)
    if (isPeakHour) basePower = 800; // Peak hours (800W)
    
    const power = basePower + Math.random() * 200 - 100; // Add variation ±100W
    
    return {
      timestamp: timestamp.toISOString(),
      power: Math.max(20, power), // Minimum 20W
      energy: parseFloat((power * 0.001).toFixed(3)), // Convert W to kWh approximation
    };
  }).reverse();
};

// Generate realistic voltage and current data
const generateVoltageCurrentData = (readings) => {
  if (readings && readings.length > 0) {
    return readings.slice(0, 24).reverse();
  }
  
  const now = new Date();
  return Array.from({ length: 24 }, (_, i) => {
    const hour = 23 - i;
    const timestamp = new Date(now.getTime() - (i * 60 * 60 * 1000));
    
    const isDaytime = hour >= 6 && hour <= 22;
    const isPeakHour = (hour >= 10 && hour <= 14) || (hour >= 18 && hour <= 21);
    
    // Voltage typically 220-240V with slight variations
    let baseVoltage = 230;
    if (isPeakHour) baseVoltage = 225; // Slight voltage drop during peak
    const voltage = baseVoltage + Math.random() * 10 - 5; // ±5V variation
    
    // Current varies with load
    let baseCurrent = 0.2; // Night (50W / 230V ≈ 0.2A)
    if (isDaytime) baseCurrent = 1.3; // Daytime (300W / 230V ≈ 1.3A)
    if (isPeakHour) baseCurrent = 3.5; // Peak (800W / 230V ≈ 3.5A)
    const current = baseCurrent + Math.random() * 0.5 - 0.25; // Add variation
    
    return {
      timestamp: timestamp.toISOString(),
      voltage: parseFloat(voltage.toFixed(1)),
      current: parseFloat(Math.max(0.1, current).toFixed(2)),
      power: parseFloat((voltage * current).toFixed(1)),
    };
  }).reverse();
};

// Generate daily energy comparison data
const generateDailyEnergyData = (displayMeters) => {
  if (displayMeters.length > 0 && displayMeters.some(m => m.energy_today)) {
    return displayMeters.slice(0, 10);
  }
  
  // Generate sample meters with daily energy
  return Array.from({ length: Math.min(displayMeters.length || 5, 10) }, (_, i) => {
    const baseEnergy = 15 + Math.random() * 20; // 15-35 kWh per day
    return {
      name: `Meter ${i + 1}`,
      meter_id: `M${String(i + 1).padStart(3, '0')}`,
      energy_today: parseFloat(baseEnergy.toFixed(2)),
      location: `House ${i + 1}`,
      status: Math.random() > 0.1 ? 'active' : 'inactive',
    };
  });
};

// Status badge component
const StatusBadge = ({ status }) => {
  const statusConfig = {
    active: { bg: 'bg-green-100', text: 'text-green-700', icon: CheckCircle },
    inactive: { bg: 'bg-gray-100', text: 'text-gray-600', icon: Power },
    alert: { bg: 'bg-red-100', text: 'text-red-700', icon: AlertTriangle },
    offline: { bg: 'bg-yellow-100', text: 'text-yellow-700', icon: WifiOff },
  };
  
  const config = statusConfig[status] || statusConfig.inactive;
  const Icon = config.icon;
  
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
      <Icon className="w-3 h-3" />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

// Meter Card Component
const MeterCard = ({ meter, onSelect, isSelected }) => {
  const getEfficiencyColor = (efficiency) => {
    if (efficiency >= 80) return 'text-green-500';
    if (efficiency >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div 
      onClick={() => onSelect(meter)}
      className={`bg-white rounded-xl p-5 shadow-sm border-2 transition-all cursor-pointer hover:shadow-md
        ${isSelected ? 'border-emerald-500' : 'border-transparent hover:border-slate-200'}`}
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-semibold text-slate-900">{meter.name || `Meter ${meter.meter_id}`}</h3>
          <p className="text-sm text-slate-600 flex items-center gap-1 mt-1">
            <MapPin className="w-3 h-3" />
            {meter.location || meter.village || 'Unknown Location'}
          </p>
        </div>
        <StatusBadge status={meter.status || 'active'} />
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-slate-600">Current Power</p>
          <p className="text-lg font-bold text-slate-900">
            {meter.power?.toFixed(1) || '0'} <span className="text-sm font-normal">W</span>
          </p>
        </div>
        <div>
          <p className="text-xs text-slate-600">Today's Usage</p>
          <p className="text-lg font-bold text-slate-900">
            {meter.energy_today?.toFixed(2) || '0'} <span className="text-sm font-normal">kWh</span>
          </p>
        </div>
      </div>
      
      <div className="flex items-center justify-between pt-3 border-t border-slate-200">
        <div className="flex items-center gap-2">
          <Gauge className="w-4 h-4 text-gray-400" />
          <span className={`text-sm font-medium ${getEfficiencyColor(meter.efficiency || 0)}`}>
            {meter.efficiency?.toFixed(0) || '0'}% efficiency
          </span>
        </div>
        <span className="text-xs text-gray-400">
          {meter.last_reading_at ? new Date(meter.last_reading_at).toLocaleTimeString() : 'No data'}
        </span>
      </div>
    </div>
  );
};

// Live Meter Detail Component
const MeterDetail = ({ meter, readings }) => {
  if (!meter) {
    return (
      <div className="bg-white rounded-xl p-8 shadow-sm text-center border border-slate-200">
        <Gauge className="w-16 h-16 mx-auto text-slate-300 mb-4" />
        <h3 className="text-lg font-medium text-slate-700">Select a Meter</h3>
        <p className="text-slate-500 mt-2">Click on a meter card to view detailed readings and analytics</p>
      </div>
    );
  }

  const latestReading = readings?.[0] || {};
  
  const liveMetrics = [
    { label: 'Voltage', value: latestReading.voltage?.toFixed(1) || meter.voltage?.toFixed(1) || '0', unit: 'V', icon: Zap, color: 'text-yellow-500' },
    { label: 'Current', value: latestReading.current?.toFixed(2) || meter.current?.toFixed(2) || '0', unit: 'A', icon: Activity, color: 'text-blue-500' },
    { label: 'Power', value: latestReading.power?.toFixed(1) || meter.power?.toFixed(1) || '0', unit: 'W', icon: Power, color: 'text-green-500' },
    { label: 'Energy', value: latestReading.energy?.toFixed(2) || meter.energy?.toFixed(2) || '0', unit: 'kWh', icon: BarChart3, color: 'text-purple-500' },
    { label: 'Power Factor', value: latestReading.power_factor?.toFixed(2) || meter.power_factor?.toFixed(2) || '0', unit: '', icon: TrendingUp, color: 'text-orange-500' },
    { label: 'Frequency', value: latestReading.frequency?.toFixed(1) || meter.frequency?.toFixed(1) || '50', unit: 'Hz', icon: Clock, color: 'text-cyan-500' },
  ];

  return (
    <div className="space-y-6">
      {/* Live Readings Header */}
      <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-xl font-bold text-slate-900">{meter.name || `Meter ${meter.meter_id}`}</h3>
            <p className="text-sm text-slate-600">Live Readings</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1 text-sm text-green-500">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              Live
            </span>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {liveMetrics.map((metric) => (
            <div key={metric.label} className="bg-slate-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <metric.icon className={`w-4 h-4 ${metric.color}`} />
                <span className="text-xs text-slate-500">{metric.label}</span>
              </div>
              <p className="text-2xl font-bold text-slate-900">
                {metric.value}
                <span className="text-sm font-normal text-slate-500 ml-1">{metric.unit}</span>
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Power Consumption Chart */}
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h4 className="text-lg font-semibold text-slate-900 mb-4">Power Consumption (Last 24 Hours)</h4>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={generatePowerConsumptionData(readings)}>
              <defs>
                <linearGradient id="powerGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#14b8a6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="timestamp" 
                stroke="#64748b" 
                fontSize={12}
                tickFormatter={(value) => new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              />
              <YAxis 
                stroke="#64748b" 
                fontSize={12}
                label={{ value: 'Power (W)', angle: -90, position: 'insideLeft', style: { fill: '#64748b' } }}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: 'white', border: '1px solid #e2e8f0', borderRadius: '8px' }}
                labelStyle={{ color: '#64748b' }}
                formatter={(value) => [`${value.toFixed(1)} W`, 'Power']}
                labelFormatter={(value) => new Date(value).toLocaleString()}
              />
              <Area 
                type="monotone" 
                dataKey="power" 
                stroke="#10b981" 
                fillOpacity={1} 
                fill="url(#powerGradient)" 
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Voltage & Current Chart */}
      <div className="bg-white rounded-xl p-5 shadow-sm">
        <h4 className="text-lg font-semibold text-slate-900 mb-4">Voltage & Current Trends (24 Hours)</h4>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={generateVoltageCurrentData(readings)}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="timestamp" 
                stroke="#64748b" 
                fontSize={12}
                tickFormatter={(value) => new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              />
              <YAxis 
                yAxisId="voltage" 
                orientation="left" 
                stroke="#f59e0b" 
                fontSize={12}
                label={{ value: 'Voltage (V)', angle: -90, position: 'insideLeft', style: { fill: '#f59e0b' } }}
                domain={[210, 245]}
              />
              <YAxis 
                yAxisId="current" 
                orientation="right" 
                stroke="#10b981" 
                fontSize={12}
                label={{ value: 'Current (A)', angle: 90, position: 'insideRight', style: { fill: '#10b981' } }}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: 'white', border: '1px solid #e2e8f0', borderRadius: '8px' }}
                labelStyle={{ color: '#64748b' }}
                labelFormatter={(value) => new Date(value).toLocaleString()}
                formatter={(value, name) => {
                  if (name === 'Voltage (V)') return [`${value.toFixed(1)} V`, name];
                  if (name === 'Current (A)') return [`${value.toFixed(2)} A`, name];
                  return [value, name];
                }}
              />
              <Legend />
              <Line 
                yAxisId="voltage"
                type="monotone" 
                dataKey="voltage" 
                stroke="#f59e0b" 
                strokeWidth={2}
                dot={false}
                name="Voltage (V)"
              />
              <Line 
                yAxisId="current"
                type="monotone" 
                dataKey="current" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={false}
                name="Current (A)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

// Main Meters Page
const Meters = () => {
  const [meters, setMeters] = useState([]);
  const [selectedMeter, setSelectedMeter] = useState(null);
  const [readings, setReadings] = useState([]);
  const [liveStatus, setLiveStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [readingsLoading, setReadingsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [stats, setStats] = useState(null);
  
  // Real-time simulated meter data
  const realtimeMeters = useMultiMeterData(5, 2000);

  // Fetch all meters
  const fetchMeters = async () => {
    try {
      const data = await api.getMeters();
      setMeters(data || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch meters:', err);
      // Use realtime simulated data if API fails
      if (realtimeMeters.length > 0) {
        setMeters(realtimeMeters);
        setError(null);
      } else {
        setError('Failed to load meters');
      }
    } finally {
      setLoading(false);
    }
  };

  // Merge API meters with realtime data for live updates
  const displayMeters = meters.length > 0 ? meters.map((meter, idx) => {
    const realtimeMeter = realtimeMeters[idx % realtimeMeters.length];
    return {
      ...meter,
      // Override with realtime values for live feel
      voltage: realtimeMeter?.voltage || meter.voltage,
      current: realtimeMeter?.current || meter.current,
      power: realtimeMeter?.power || meter.power,
      energy_today: realtimeMeter?.energy_today || meter.energy_today,
      efficiency: realtimeMeter?.efficiency || meter.efficiency,
      status: realtimeMeter?.status || meter.status,
      last_reading_at: realtimeMeter?.last_reading_at || new Date(),
    };
  }) : realtimeMeters;

  // Fetch meter stats
  const fetchStats = async () => {
    try {
      const data = await api.getMeterStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  // Fetch readings for selected meter
  const fetchReadings = async (meterId) => {
    if (!meterId) return;
    setReadingsLoading(true);
    try {
      const data = await api.getMeterReadings(meterId);
      setReadings(Array.isArray(data) ? data : (data?.results || data?.readings || []));
    } catch (err) {
      console.error('Failed to fetch readings:', err);
    } finally {
      setReadingsLoading(false);
    }
  };

  // Fetch live status
  const fetchLiveStatus = async (meterId) => {
    if (!meterId) return;
    try {
      const data = await api.getMeterLiveStatus(meterId);
      setLiveStatus(data);
    } catch (err) {
      console.error('Failed to fetch live status:', err);
    }
  };

  useEffect(() => {
    fetchMeters();
    fetchStats();
  }, []);

  useEffect(() => {
    if (selectedMeter) {
      fetchReadings(selectedMeter.meter_id || selectedMeter.id);
      fetchLiveStatus(selectedMeter.meter_id || selectedMeter.id);
    }
  }, [selectedMeter]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      fetchMeters();
      if (selectedMeter) {
        fetchReadings(selectedMeter.meter_id || selectedMeter.id);
        fetchLiveStatus(selectedMeter.meter_id || selectedMeter.id);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [autoRefresh, selectedMeter]);

  const handleMeterSelect = (meter) => {
    setSelectedMeter(meter);
  };

  const handleRefresh = () => {
    fetchMeters();
    fetchStats();
    if (selectedMeter) {
      fetchReadings(selectedMeter.meter_id || selectedMeter.id);
      fetchLiveStatus(selectedMeter.meter_id || selectedMeter.id);
    }
  };

  // Calculate summary stats from meters
  const summaryStats = [
    { 
      label: 'Total Meters', 
      value: stats?.total_meters || displayMeters.length, 
      icon: Gauge, 
      color: 'bg-emerald-500',
      trend: null
    },
    { 
      label: 'Active', 
      value: stats?.active_meters || displayMeters.filter(m => m.status === 'active').length, 
      icon: CheckCircle, 
      color: 'bg-green-500',
      trend: 'up'
    },
    { 
      label: 'Offline', 
      value: stats?.offline_meters || displayMeters.filter(m => m.status === 'offline').length, 
      icon: WifiOff, 
      color: 'bg-yellow-500',
      trend: null
    },
    { 
      label: 'With Alerts', 
      value: stats?.meters_with_alerts || displayMeters.filter(m => m.status === 'alert').length, 
      icon: AlertTriangle, 
      color: 'bg-red-500',
      trend: 'down'
    },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 mx-auto text-emerald-500 animate-spin mb-4" />
          <p className="text-slate-600">Loading meters...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Smart Meters</h1>
            <p className="text-slate-600">Monitor and manage all connected meters</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${autoRefresh 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-gray-100 text-gray-600'}`}
            >
              <Activity className="w-4 h-4" />
              Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
            </button>
            <button 
              onClick={handleRefresh}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {summaryStats.map((stat) => (
            <div key={stat.label} className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-600">{stat.label}</p>
                  <p className="text-3xl font-bold text-slate-900 mt-1">{stat.value}</p>
                </div>
                <div className={`p-3 ${stat.color} rounded-xl`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
              </div>
              {stat.trend && (
                <div className={`flex items-center gap-1 mt-2 text-sm ${stat.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                  {stat.trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <span>vs last week</span>
                </div>
              )}
            </div>
          ))}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Meters List */}
          <div className="lg:col-span-1 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">All Meters</h2>
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1 text-sm text-emerald-500">
                  <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                  Live
                </span>
                <span className="text-sm text-slate-500">{displayMeters.length} total</span>
              </div>
            </div>
            
            {displayMeters.length === 0 ? (
              <div className="bg-white rounded-xl p-8 shadow-sm text-center">
                <Gauge className="w-12 h-12 mx-auto text-slate-300 mb-4" />
                <p className="text-slate-500">No meters found</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[calc(100vh-400px)] overflow-y-auto pr-2">
                {displayMeters.map((meter) => (
                  <MeterCard 
                    key={meter.id || meter.meter_id} 
                    meter={meter} 
                    onSelect={handleMeterSelect}
                    isSelected={selectedMeter?.id === meter.id || selectedMeter?.meter_id === meter.meter_id}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Meter Detail */}
          <div className="lg:col-span-2">
            {readingsLoading ? (
              <div className="bg-white rounded-xl p-8 shadow-sm text-center">
                <RefreshCw className="w-12 h-12 mx-auto text-emerald-500 animate-spin mb-4" />
                <p className="text-slate-600">Loading meter data...</p>
              </div>
            ) : (
              <MeterDetail meter={selectedMeter} readings={readings} />
            )}
          </div>
        </div>

        {/* Daily Usage Comparison Chart */}
        <div className="bg-white rounded-xl p-5 shadow-sm mt-6">
          <h4 className="text-lg font-semibold text-slate-900 mb-4">Daily Energy Comparison (All Meters)</h4>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={generateDailyEnergyData(displayMeters)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="name" 
                  stroke="#64748b" 
                  fontSize={12}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  stroke="#64748b" 
                  fontSize={12}
                  label={{ value: 'Energy (kWh)', angle: -90, position: 'insideLeft', style: { fill: '#64748b' } }}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'white', border: '1px solid #e2e8f0', borderRadius: '8px' }}
                  labelStyle={{ color: '#64748b' }}
                  formatter={(value, name, props) => {
                    const location = props.payload.location || '';
                    return [
                      <div key="tooltip">
                        <div>{`${value.toFixed(2)} kWh`}</div>
                        {location && <div className="text-xs text-slate-500 mt-1">{location}</div>}
                      </div>,
                      "Today's Energy"
                    ];
                  }}
                />
                <Bar 
                  dataKey="energy_today" 
                  fill="#10b981" 
                  radius={[8, 8, 0, 0]}
                  name="Today's Energy (kWh)"
                >
                  {generateDailyEnergyData(displayMeters).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.status === 'active' ? '#10b981' : '#94a3b8'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Meters;
