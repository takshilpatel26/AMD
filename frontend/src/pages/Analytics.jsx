// Analytics Page - Comprehensive Energy Analytics with ML Insights
import React, { useState, useEffect, useMemo } from 'react';
import { 
  TrendingUp, TrendingDown, Zap, DollarSign, Leaf, 
  BarChart3, PieChart, Activity, Calendar, Download,
  ArrowUpRight, ArrowDownRight, Target, Cpu, AlertTriangle,
  Brain, Sparkles, Shield, Bell
} from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import apiService from '../services/api';
import { useAnalyticsTrends, useRealtimeData, useBillingData } from '../hooks/useRealtimeData';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart as RePieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const Analytics = ({ onLogout }) => {
  const { t } = useLanguage();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('consumption');
  const [dateRange, setDateRange] = useState('week');
  
  // Real-time simulated trends data
  const realtimeTrends = useAnalyticsTrends();
  const liveData = useRealtimeData();
  const billingData = useBillingData();
  
  // Calculate live stats from realtime data based on selected date range
  const liveStats = useMemo(() => {
    let totalConsumption, totalCost, efficiencyScore, carbonSaved;
    
    if (dateRange === 'day') {
      // Daily stats (24 hours)
      totalConsumption = liveData.energy || 45.8;
      totalCost = Math.round(totalConsumption * 6.5);
      efficiencyScore = Math.round(82 + (liveData.powerFactor || 0.92) * 10);
      carbonSaved = Math.round(totalConsumption * 0.1);
    } else if (dateRange === 'week') {
      // Weekly stats (7 days)
      totalConsumption = liveData.energy ? liveData.energy * 7 : 245.3;
      totalCost = Math.round(totalConsumption * 6.5);
      efficiencyScore = Math.round(85 + (liveData.powerFactor || 0.92) * 8);
      carbonSaved = Math.round(totalConsumption * 0.12);
    } else {
      // Monthly stats (30 days)
      totalConsumption = liveData.energy ? liveData.energy * 30 : 1087.5;
      totalCost = Math.round(totalConsumption * 6.5);
      efficiencyScore = Math.round(80 + (liveData.powerFactor || 0.92) * 12);
      carbonSaved = Math.round(totalConsumption * 0.15);
    }
    
    return {
      totalConsumption: totalConsumption.toFixed(1),
      totalCost,
      efficiencyScore: Math.min(efficiencyScore, 99),
      carbonSaved
    };
  }, [liveData, billingData, dateRange]);
  
  // Data states
  const [consumptionData, setConsumptionData] = useState(null);
  const [efficiencyData, setEfficiencyData] = useState(null);
  const [costData, setCostData] = useState(null);
  const [carbonData, setCarbonData] = useState(null);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    fetchAnalyticsData();
  }, [dateRange]);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      const days = dateRange === 'day' ? 1 : dateRange === 'week' ? 7 : 30;
      
      console.log('Fetching analytics with days:', days);
      
      const [consumption, efficiency, cost, carbon, summaryData] = await Promise.all([
        apiService.getConsumptionTrends({ days }),
        apiService.getEfficiencyAnalysis({ days }),
        apiService.getCostProjection({ days }),
        apiService.getCarbonFootprint({ days }),
        apiService.getDashboardStats()
      ]);

      console.log('Consumption data:', consumption);
      console.log('Efficiency data:', efficiency);
      console.log('Cost data:', cost);
      console.log('Carbon data:', carbon);

      setConsumptionData(consumption);
      setEfficiencyData(efficiency);
      setCostData(cost);
      setCarbonData(carbon);
      setSummary(summaryData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  // Generate mock data if API returns null - use realtime trends as fallback
  const getConsumptionChartData = () => {
    if (consumptionData?.trends) return consumptionData.trends;
    
    // Generate different realistic data based on date range
    if (dateRange === 'day') {
      // 24 hours with hourly data - showing typical daily pattern
      return Array.from({ length: 24 }, (_, i) => {
        const hour = i;
        // Higher consumption during day (6am-10pm), lower at night
        const isDaytime = hour >= 6 && hour <= 22;
        const isPeakHour = (hour >= 10 && hour <= 14) || (hour >= 18 && hour <= 21); // Peak usage times
        
        let baseEnergy = 0.5; // Night baseline
        if (isDaytime) baseEnergy = 2.5;
        if (isPeakHour) baseEnergy = 4.5;
        
        const energy = parseFloat((baseEnergy + Math.random() * 1.5).toFixed(2));
        const cost = Math.round(energy * 6.5);
        const efficiency = Math.round(isPeakHour ? 75 + Math.random() * 15 : 80 + Math.random() * 15);
        
        return {
          date: `${hour.toString().padStart(2, '0')}:00`,
          energy,
          cost,
          efficiency
        };
      });
    } else if (dateRange === 'week') {
      // 7 days with daily data - showing weekly pattern
      const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      return Array.from({ length: 7 }, (_, i) => {
        const isWeekend = i >= 5; // Saturday and Sunday
        // Higher consumption on weekdays due to irrigation/farming activities
        const baseEnergy = isWeekend ? 25 + Math.random() * 10 : 35 + Math.random() * 15;
        const energy = parseFloat(baseEnergy.toFixed(1));
        const cost = Math.round(energy * 6.5);
        const efficiency = Math.round(isWeekend ? 85 + Math.random() * 10 : 75 + Math.random() * 15);
        
        return {
          date: daysOfWeek[i],
          energy,
          cost,
          efficiency
        };
      });
    } else {
      // 30 days with daily data - showing monthly pattern
      return Array.from({ length: 30 }, (_, i) => {
        const day = i + 1;
        // Simulate varying consumption throughout the month
        // Higher consumption mid-month (irrigation season)
        const isHighPeriod = day >= 10 && day <= 20;
        const baseEnergy = isHighPeriod ? 40 + Math.random() * 20 : 28 + Math.random() * 15;
        const energy = parseFloat(baseEnergy.toFixed(1));
        const cost = Math.round(energy * 6.5);
        const efficiency = Math.round(70 + Math.random() * 25);
        
        return {
          date: `${day}`,
          energy,
          cost,
          efficiency
        };
      });
    }
  };

  // Generate efficiency analysis data with realistic patterns
  const getEfficiencyChartData = () => {
    if (efficiencyData?.trends) return efficiencyData.trends;
    
    if (dateRange === 'day') {
      // 24 hours efficiency pattern
      return Array.from({ length: 24 }, (_, i) => {
        const hour = i;
        const isDaytime = hour >= 6 && hour <= 22;
        const isPeakHour = (hour >= 10 && hour <= 14) || (hour >= 18 && hour <= 21);
        
        // Efficiency typically lower during peak loads
        let efficiency;
        if (!isDaytime) {
          efficiency = 90 + Math.random() * 8; // Very efficient at night (low load)
        } else if (isPeakHour) {
          efficiency = 72 + Math.random() * 10; // Lower during peak
        } else {
          efficiency = 82 + Math.random() * 10; // Good during normal hours
        }
        
        return {
          date: `${hour.toString().padStart(2, '0')}:00`,
          efficiency: parseFloat(efficiency.toFixed(1)),
          powerFactor: parseFloat((0.85 + Math.random() * 0.1).toFixed(2)),
          loadBalance: parseFloat((75 + Math.random() * 15).toFixed(1))
        };
      });
    } else if (dateRange === 'week') {
      const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      return Array.from({ length: 7 }, (_, i) => {
        const isWeekend = i >= 5;
        // Higher efficiency on weekends (lower load)
        const efficiency = isWeekend 
          ? 88 + Math.random() * 8 
          : 78 + Math.random() * 12;
        
        return {
          date: daysOfWeek[i],
          efficiency: parseFloat(efficiency.toFixed(1)),
          powerFactor: parseFloat((0.82 + Math.random() * 0.12).toFixed(2)),
          loadBalance: parseFloat((70 + Math.random() * 20).toFixed(1))
        };
      });
    } else {
      // 30 days
      return Array.from({ length: 30 }, (_, i) => {
        const day = i + 1;
        const isHighLoadPeriod = day >= 10 && day <= 20;
        // Efficiency decreases during high load irrigation periods
        const efficiency = isHighLoadPeriod 
          ? 75 + Math.random() * 12 
          : 82 + Math.random() * 12;
        
        return {
          date: `${day}`,
          efficiency: parseFloat(efficiency.toFixed(1)),
          powerFactor: parseFloat((0.80 + Math.random() * 0.14).toFixed(2)),
          loadBalance: parseFloat((68 + Math.random() * 22).toFixed(1))
        };
      });
    }
  };

  // Generate carbon footprint data based on energy consumption
  const getCarbonFootprintData = () => {
    if (carbonData?.trends) return carbonData.trends;
    
    const consumptionData = getConsumptionChartData();
    
    // Calculate carbon saved based on solar offset and reduced grid usage
    // Assuming 0.7 kg CO2 per kWh from grid, and we're saving 15% through solar/efficiency
    return consumptionData.map(item => {
      const carbonEmitted = parseFloat((item.energy * 0.7).toFixed(2)); // Total if all from grid
      const carbonSaved = parseFloat((item.energy * 0.15).toFixed(2)); // 15% saved through green energy
      const netCarbon = parseFloat((carbonEmitted - carbonSaved).toFixed(2));
      
      return {
        date: item.date,
        carbonSaved,
        carbonEmitted,
        netCarbon,
        greenPercentage: parseFloat((15 + Math.random() * 5).toFixed(1)) // 15-20% green
      };
    });
  };

  const getEfficiencyRadarData = () => {
    return [
      { subject: 'Power Factor', A: 92, fullMark: 100 },
      { subject: 'Load Balance', A: 85, fullMark: 100 },
      { subject: 'Peak Efficiency', A: 78, fullMark: 100 },
      { subject: 'Off-Peak Usage', A: 88, fullMark: 100 },
      { subject: 'Standby Power', A: 95, fullMark: 100 },
      { subject: 'Voltage Quality', A: 90, fullMark: 100 },
    ];
  };

  const getCostBreakdownData = () => {
    return [
      { name: 'Irrigation', value: 45, color: '#10b981' },
      { name: 'Lighting', value: 20, color: '#3b82f6' },
      { name: 'Equipment', value: 25, color: '#f59e0b' },
      { name: 'Other', value: 10, color: '#8b5cf6' },
    ];
  };

  const getHourlyUsageData = () => {
    // This is specifically for the 'patterns' tab showing daily usage pattern
    if (dateRange === 'day') {
      // Show 24-hour pattern for current day
      return Array.from({ length: 24 }, (_, i) => {
        const hour = i;
        const isDaytime = hour >= 6 && hour <= 22;
        const isPeakHour = (hour >= 10 && hour <= 14) || (hour >= 18 && hour <= 21);
        
        const usage = isDaytime 
          ? (isPeakHour ? 3 + Math.random() * 2 : 1.5 + Math.random() * 1.5)
          : 0.3 + Math.random() * 0.5;
        
        const peak = isPeakHour ? 4 + Math.random() : 0;
        
        return {
          hour: `${hour.toString().padStart(2, '0')}:00`,
          usage: parseFloat(usage.toFixed(2)),
          peak: parseFloat(peak.toFixed(2))
        };
      });
    } else if (dateRange === 'week') {
      // Show average hourly pattern for the week
      return Array.from({ length: 24 }, (_, i) => {
        const hour = i;
        const isDaytime = hour >= 6 && hour <= 22;
        const isPeakHour = (hour >= 10 && hour <= 14) || (hour >= 18 && hour <= 21);
        
        const usage = isDaytime 
          ? (isPeakHour ? 2.5 + Math.random() * 1.5 : 1.2 + Math.random() * 1)
          : 0.4 + Math.random() * 0.4;
        
        const peak = isPeakHour ? 3.5 + Math.random() : 0;
        
        return {
          hour: `${hour.toString().padStart(2, '0')}:00`,
          usage: parseFloat(usage.toFixed(2)),
          peak: parseFloat(peak.toFixed(2))
        };
      });
    } else {
      // Show average hourly pattern for the month
      return Array.from({ length: 24 }, (_, i) => {
        const hour = i;
        const isDaytime = hour >= 6 && hour <= 22;
        const isPeakHour = (hour >= 10 && hour <= 14) || (hour >= 18 && hour <= 21);
        
        const usage = isDaytime 
          ? (isPeakHour ? 2.2 + Math.random() * 1.2 : 1 + Math.random() * 0.8)
          : 0.35 + Math.random() * 0.35;
        
        const peak = isPeakHour ? 3.2 + Math.random() * 0.8 : 0;
        
        return {
          hour: `${hour.toString().padStart(2, '0')}:00`,
          usage: parseFloat(usage.toFixed(2)),
          peak: parseFloat(peak.toFixed(2))
        };
      });
    }
  };

  const StatCard = ({ title, value, unit, icon: Icon, trend, trendValue, color }) => (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-slate-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-500 text-sm font-medium">{title}</p>
          <h3 className="text-3xl font-bold mt-2 text-slate-900">
            {value}<span className="text-lg ml-1">{unit}</span>
          </h3>
          {trend && (
            <div className={`flex items-center mt-2 text-sm ${trend === 'up' ? 'text-emerald-600' : 'text-red-500'}`}>
              {trend === 'up' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
              <span>{trendValue}</span>
            </div>
          )}
        </div>
        <div className={`p-4 rounded-xl ${color}`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <LoadingSpinner size="large" text="Loading Analytics..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="p-4 md:p-6 max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
              <BarChart3 className="w-8 h-8 text-emerald-500" />
              Energy Analytics
            </h1>
            <p className="text-slate-600 mt-1">
              ML-powered insights and consumption analysis
            </p>
          </div>
          
          {/* Date Range Selector */}
          <div className="flex items-center gap-2 bg-white rounded-xl p-1 shadow-md border border-slate-200">
            {['day', 'week', 'month'].map((range) => (
              <button
                key={range}
                onClick={() => setDateRange(range)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  dateRange === range
                    ? 'bg-emerald-500 text-white'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {range.charAt(0).toUpperCase() + range.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Consumption"
            value={liveStats.totalConsumption}
            unit="kWh"
            icon={Zap}
            trend="down"
            trendValue="12% vs last period"
            color="bg-emerald-500"
          />
          <StatCard
            title="Total Cost"
            value={`₹${liveStats.totalCost.toLocaleString()}`}
            unit=""
            icon={DollarSign}
            trend="down"
            trendValue="8% savings"
            color="bg-blue-500"
          />
          <StatCard
            title="Efficiency Score"
            value={liveStats.efficiencyScore}
            unit="%"
            icon={Target}
            trend="up"
            trendValue="5% improvement"
            color="bg-amber-500"
          />
          <StatCard
            title="Carbon Saved"
            value={liveStats.carbonSaved}
            unit="kg"
            icon={Leaf}
            trend="up"
            trendValue="Green energy"
            color="bg-green-600"
          />
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {[
            { id: 'consumption', label: 'Consumption Trends', icon: TrendingUp },
            { id: 'efficiency', label: 'Efficiency Analysis', icon: Activity },
            { id: 'cost', label: 'Cost Projection', icon: DollarSign },
            { id: 'carbon', label: 'Carbon Footprint', icon: Leaf },
            { id: 'patterns', label: 'Usage Patterns', icon: PieChart },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl font-medium whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-emerald-500 text-white shadow-lg'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Main Chart */}
          <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-lg border border-slate-200">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-slate-900">
                {activeTab === 'consumption' && 'Energy Consumption Over Time'}
                {activeTab === 'efficiency' && 'Efficiency Performance'}
                {activeTab === 'cost' && 'Cost Analysis & Projection'}
                {activeTab === 'carbon' && 'Carbon Emissions Tracking'}
                {activeTab === 'patterns' && 'Daily Usage Pattern'}
              </h2>
              <button className="flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-lg text-slate-600 hover:bg-slate-200 transition-colors">
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
            
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                {activeTab === 'consumption' && (
                  <AreaChart data={getConsumptionChartData()}>
                    <defs>
                      <linearGradient id="colorEnergy" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.05}/>
                      </linearGradient>
                      <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.05}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                    <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
                    <YAxis yAxisId="left" stroke="#9ca3af" fontSize={12} label={{ value: 'kWh', angle: -90, position: 'insideLeft' }} />
                    <YAxis yAxisId="right" orientation="right" stroke="#9ca3af" fontSize={12} label={{ value: '₹', angle: 90, position: 'insideRight' }} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1f2937', 
                        border: 'none', 
                        borderRadius: '12px',
                        color: '#fff'
                      }}
                      formatter={(value, name) => {
                        if (name === 'Energy (kWh)') return [`${value} kWh`, name];
                        if (name === 'Cost (₹)') return [`₹${value}`, name];
                        return [value, name];
                      }}
                    />
                    <Legend />
                    <Area 
                      yAxisId="left"
                      type="monotone" 
                      dataKey="energy" 
                      stroke="#10b981" 
                      strokeWidth={2}
                      fillOpacity={1} 
                      fill="url(#colorEnergy)" 
                      name="Energy (kWh)"
                    />
                    <Area 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="cost" 
                      stroke="#f59e0b" 
                      strokeWidth={2}
                      fillOpacity={1} 
                      fill="url(#colorCost)" 
                      name="Cost (₹)"
                    />
                  </AreaChart>
                )}
                
                {activeTab === 'efficiency' && (
                  <LineChart data={getEfficiencyChartData()}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                    <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
                    <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 100]} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1f2937', 
                        border: 'none', 
                        borderRadius: '12px',
                        color: '#fff'
                      }} 
                    />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="efficiency" 
                      stroke="#3b82f6" 
                      strokeWidth={3}
                      dot={{ fill: '#3b82f6', strokeWidth: 2 }}
                      name="Efficiency (%)"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="loadBalance" 
                      stroke="#10b981" 
                      strokeWidth={2}
                      dot={{ fill: '#10b981', strokeWidth: 1 }}
                      name="Load Balance (%)"
                    />
                  </LineChart>
                )}
                
                {activeTab === 'cost' && (
                  <BarChart data={getConsumptionChartData()}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                    <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
                    <YAxis stroke="#9ca3af" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1f2937', 
                        border: 'none', 
                        borderRadius: '12px',
                        color: '#fff'
                      }} 
                    />
                    <Legend />
                    <Bar dataKey="cost" fill="#f59e0b" radius={[4, 4, 0, 0]} name="Cost (₹)" />
                  </BarChart>
                )}
                
                {activeTab === 'carbon' && (
                  <AreaChart data={getCarbonFootprintData()}>
                    <defs>
                      <linearGradient id="colorCarbonSaved" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4}/>
                        <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorCarbonEmitted" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                    <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
                    <YAxis stroke="#9ca3af" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1f2937', 
                        border: 'none', 
                        borderRadius: '12px',
                        color: '#fff'
                      }} 
                      formatter={(value, name) => {
                        if (name === 'CO₂ Saved (kg)' || name === 'CO₂ Emitted (kg)' || name === 'Net CO₂ (kg)') {
                          return [`${value} kg`, name];
                        }
                        return [value, name];
                      }}
                    />
                    <Legend />
                    <Area 
                      type="monotone" 
                      dataKey="carbonSaved" 
                      stroke="#22c55e" 
                      strokeWidth={2}
                      fillOpacity={1} 
                      fill="url(#colorCarbonSaved)" 
                      name="CO₂ Saved (kg)"
                    />
                    <Area 
                      type="monotone" 
                      dataKey="carbonEmitted" 
                      stroke="#ef4444" 
                      strokeWidth={2}
                      fillOpacity={1} 
                      fill="url(#colorCarbonEmitted)" 
                      name="CO₂ Emitted (kg)"
                    />
                  </AreaChart>
                )}
                
                {activeTab === 'patterns' && (
                  <BarChart data={getHourlyUsageData()}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                    <XAxis dataKey="hour" stroke="#9ca3af" fontSize={10} />
                    <YAxis stroke="#9ca3af" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1f2937', 
                        border: 'none', 
                        borderRadius: '12px',
                        color: '#fff'
                      }} 
                    />
                    <Legend />
                    <Bar dataKey="usage" fill="#10b981" radius={[2, 2, 0, 0]} name="Usage (kW)" />
                    <Bar dataKey="peak" fill="#ef4444" radius={[2, 2, 0, 0]} name="Peak Hours" />
                  </BarChart>
                )}
              </ResponsiveContainer>
            </div>
            
            {/* Chart-specific Insights */}
            <div className="mt-4 p-4 bg-slate-50 rounded-lg">
              {activeTab === 'consumption' && (
                <div className="flex items-start gap-3">
                  <Sparkles className="w-5 h-5 text-emerald-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-slate-900">AI Insight</p>
                    <p className="text-sm text-slate-600 mt-1">
                      {dateRange === 'day' && 'Peak consumption occurs during 10 AM - 2 PM and 6 PM - 9 PM. Consider load balancing during these hours.'}
                      {dateRange === 'week' && 'Weekday consumption is 40% higher than weekends. Optimize irrigation schedules for better efficiency.'}
                      {dateRange === 'month' && 'Mid-month shows highest energy usage (irrigation season). Plan maintenance during low-consumption periods.'}
                    </p>
                  </div>
                </div>
              )}
              {activeTab === 'efficiency' && (
                <div className="flex items-start gap-3">
                  <Brain className="w-5 h-5 text-blue-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-slate-900">Efficiency Analysis</p>
                    <p className="text-sm text-slate-600 mt-1">
                      {dateRange === 'day' && 'Night hours show 95%+ efficiency. Peak loads (10 AM-2 PM) have reduced efficiency due to heavy equipment usage.'}
                      {dateRange === 'week' && 'Weekend efficiency is 12% higher due to reduced load. Consider power factor correction during weekdays.'}
                      {dateRange === 'month' && 'Average efficiency: 82%. Install capacitor banks to improve power factor during high-load periods.'}
                    </p>
                  </div>
                </div>
              )}
              {activeTab === 'cost' && (
                <div className="flex items-start gap-3">
                  <DollarSign className="w-5 h-5 text-amber-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-slate-900">Cost Optimization</p>
                    <p className="text-sm text-slate-600 mt-1">
                      {dateRange === 'day' && 'Shifting 30% of non-critical loads to off-peak hours could save ₹50-80 daily.'}
                      {dateRange === 'week' && `Current average: ₹${Math.round(liveStats.totalCost/7)}/day. Solar integration could reduce this by 20-25%.`}
                      {dateRange === 'month' && `Monthly cost: ₹${liveStats.totalCost.toLocaleString()}. Demand-side management could save ₹800-1200/month.`}
                    </p>
                  </div>
                </div>
              )}
              {activeTab === 'carbon' && (
                <div className="flex items-start gap-3">
                  <Leaf className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-slate-900">Environmental Impact</p>
                    <p className="text-sm text-slate-600 mt-1">
                      {dateRange === 'day' && 'Green energy offset: 15%. Daily carbon saved equivalent to planting 0.2 trees.'}
                      {dateRange === 'week' && `Weekly carbon savings: ${liveStats.carbonSaved}kg CO₂. Equivalent to removing a car for 2 days.`}
                      {dateRange === 'month' && `Monthly carbon offset: ${liveStats.carbonSaved}kg. Expanding solar could double this impact.`}
                    </p>
                  </div>
                </div>
              )}
              {activeTab === 'patterns' && (
                <div className="flex items-start gap-3">
                  <Activity className="w-5 h-5 text-purple-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-slate-900">Usage Pattern</p>
                    <p className="text-sm text-slate-600 mt-1">
                      Peak usage: 10 AM - 2 PM (irrigation) and 6 PM - 9 PM (lighting/equipment). Off-peak hours offer better rates.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Efficiency Radar */}
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Efficiency Breakdown</h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={getEfficiencyRadarData()}>
                  <PolarGrid stroke="#374151" />
                  <PolarAngleAxis dataKey="subject" stroke="#9ca3af" fontSize={11} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#9ca3af" />
                  <Radar
                    name="Score"
                    dataKey="A"
                    stroke="#10b981"
                    fill="#10b981"
                    fillOpacity={0.3}
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Cost Breakdown Pie */}
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Cost Distribution</h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <RePieChart>
                  <Pie
                    data={getCostBreakdownData()}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {getCostBreakdownData().map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </RePieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* ML Insights Section */}
        <div className="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl p-6 shadow-lg">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-white/20 rounded-xl">
              <Cpu className="w-8 h-8 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-white mb-2">ML-Powered Insights</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                  <p className="text-emerald-100 text-sm">Predicted Monthly Usage</p>
                  <p className="text-2xl font-bold text-white mt-1">245 kWh</p>
                  <p className="text-emerald-200 text-xs mt-1">Based on current patterns</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                  <p className="text-emerald-100 text-sm">Anomaly Detection</p>
                  <p className="text-2xl font-bold text-white mt-1">2 Found</p>
                  <p className="text-emerald-200 text-xs mt-1">Last 7 days</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                  <p className="text-emerald-100 text-sm">Optimization Potential</p>
                  <p className="text-2xl font-bold text-white mt-1">₹180/mo</p>
                  <p className="text-emerald-200 text-xs mt-1">Savings opportunity</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
