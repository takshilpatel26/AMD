import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  AlertCircle, 
  Bell, 
  BellOff,
  CheckCircle, 
  Clock, 
  Filter, 
  Search,
  X,
  ChevronDown,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Zap,
  Thermometer,
  Droplet,
  Activity,
  Eye,
  CheckSquare,
  XCircle,
  BarChart3,
  PieChart as PieChartIcon
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip,
  Legend,
  AreaChart,
  Area
} from 'recharts';
import api from '../services/api';
import { useRealtimeAlerts } from '../hooks/useRealtimeData';

// Priority badge component
const PriorityBadge = ({ priority }) => {
  const config = {
    critical: { bg: 'bg-red-100', text: 'text-red-700', dot: 'bg-red-500' },
    high: { bg: 'bg-orange-100', text: 'text-orange-700', dot: 'bg-orange-500' },
    medium: { bg: 'bg-yellow-100', text: 'text-yellow-700', dot: 'bg-yellow-500' },
    low: { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500' },
  };
  
  const c = config[priority] || config.low;
  
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`}></span>
      {priority.charAt(0).toUpperCase() + priority.slice(1)}
    </span>
  );
};

// Status badge component
const StatusBadge = ({ status }) => {
  const config = {
    active: { bg: 'bg-red-100', text: 'text-red-700', icon: AlertTriangle },
    acknowledged: { bg: 'bg-yellow-100', text: 'text-yellow-700', icon: Eye },
    resolved: { bg: 'bg-green-100', text: 'text-green-700', icon: CheckCircle },
  };
  
  const c = config[status] || config.active;
  const Icon = c.icon;
  
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
      <Icon className="w-3 h-3" />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

// Alert Type Icon
const AlertTypeIcon = ({ type }) => {
  const icons = {
    voltage: Zap,
    current: Activity,
    power: TrendingUp,
    temperature: Thermometer,
    leakage: Droplet,
    default: AlertCircle
  };
  
  const Icon = icons[type?.toLowerCase()] || icons.default;
  return <Icon className="w-5 h-5" />;
};

// Alert Card Component
const AlertCard = ({ alert, onAcknowledge, onResolve, selected, onSelect }) => {
  const timeAgo = (date) => {
    const now = new Date();
    const alertDate = new Date(date);
    const diffMs = now - alertDate;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <div className={`bg-white rounded-xl p-5 shadow-sm border-l-4 transition-all
      ${alert.priority === 'critical' ? 'border-red-500' : 
        alert.priority === 'high' ? 'border-orange-500' : 
        alert.priority === 'medium' ? 'border-yellow-500' : 'border-blue-500'}
      ${selected ? 'ring-2 ring-emerald-500' : ''}`}
    >
      <div className="flex items-start gap-4">
        <input
          type="checkbox"
          checked={selected}
          onChange={() => onSelect(alert.id)}
          className="mt-1 h-4 w-4 text-emerald-600 rounded border-gray-300 focus:ring-emerald-500"
        />
        
        <div className={`p-2 rounded-lg ${
          alert.priority === 'critical' ? 'bg-red-100 text-red-600' :
          alert.priority === 'high' ? 'bg-orange-100 text-orange-600' :
          'bg-yellow-100 text-yellow-600'
        }`}>
          <AlertTypeIcon type={alert.alert_type || alert.type} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h4 className="font-semibold text-slate-900 truncate">
                {alert.title || alert.message || `${alert.alert_type || alert.type} Alert`}
              </h4>
              <p className="text-sm text-slate-600 mt-1">
                Meter: {alert.meter_name || alert.meter_id || 'Unknown'}
              </p>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <PriorityBadge priority={alert.priority || 'medium'} />
              <StatusBadge status={alert.status || 'active'} />
            </div>
          </div>
          
          <p className="text-sm text-slate-700 mt-2 line-clamp-2">
            {alert.description || alert.message || 'No description available'}
          </p>
          
          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <Clock className="w-3 h-3" />
              {timeAgo(alert.created_at || alert.timestamp)}
            </div>
            
            <div className="flex items-center gap-2">
              {alert.status !== 'acknowledged' && alert.status !== 'resolved' && (
                <button
                  onClick={() => onAcknowledge(alert.id)}
                  className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-yellow-700 bg-yellow-100 rounded-lg hover:bg-yellow-200 transition-colors"
                >
                  <Eye className="w-3 h-3" />
                  Acknowledge
                </button>
              )}
              {alert.status !== 'resolved' && (
                <button
                  onClick={() => onResolve(alert.id)}
                  className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-green-700 bg-green-100 rounded-lg hover:bg-green-200 transition-colors"
                >
                  <CheckCircle className="w-3 h-3" />
                  Resolve
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Stats Card
const StatsCard = ({ icon: Icon, label, value, change, color, bgColor }) => (
  <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-slate-600">{label}</p>
        <p className="text-3xl font-bold text-slate-900 mt-1">{value}</p>
      </div>
      <div className={`p-3 rounded-xl ${bgColor}`}>
        <Icon className={`w-6 h-6 ${color}`} />
      </div>
    </div>
    {change !== undefined && (
      <div className={`flex items-center gap-1 mt-2 text-sm ${change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
        {change >= 0 ? <TrendingDown className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
        <span>{Math.abs(change)}% vs last week</span>
      </div>
    )}
  </div>
);

// Main Alerts Page
const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [filteredAlerts, setFilteredAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [selectedAlerts, setSelectedAlerts] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    type: 'all'
  });
  const [showFilters, setShowFilters] = useState(false);
  
  // Real-time simulated alerts (only used as fallback when not authenticated)
  const { 
    alerts: realtimeAlerts, 
    acknowledgeAlert: ackRealtimeAlert, 
    resolveAlert: resolveRealtimeAlert 
  } = useRealtimeAlerts(5000);

  // Fetch alerts from database
  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const data = await api.getAlerts();
      console.log('Fetched alerts from database:', data);
      setAlerts(data || []);
    } catch (err) {
      console.error('Failed to fetch alerts:', err);
      // Use realtime alerts as fallback only if API fails
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };
  
  // Use ONLY database alerts if available, fallback to simulated only if empty
  const displayAlerts = alerts.length > 0 ? alerts : realtimeAlerts.slice(0, 20);

  // Fetch stats
  const fetchStats = async () => {
    try {
      const data = await api.getAlertStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  useEffect(() => {
    fetchAlerts();
    fetchStats();
  }, []);

  // Apply filters
  useEffect(() => {
    let filtered = [...displayAlerts];
    
    if (searchQuery) {
      filtered = filtered.filter(a => 
        (a.title || a.message || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (a.meter_name || a.meter_id || '').toString().toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    if (filters.status !== 'all') {
      filtered = filtered.filter(a => a.status === filters.status);
    }
    
    if (filters.priority !== 'all') {
      filtered = filtered.filter(a => a.priority === filters.priority);
    }
    
    if (filters.type !== 'all') {
      filtered = filtered.filter(a => (a.alert_type || a.type) === filters.type);
    }
    
    setFilteredAlerts(filtered);
  }, [searchQuery, filters, displayAlerts]);

  const handleAcknowledge = async (alertId) => {
    // First try realtime alert
    ackRealtimeAlert(alertId);
    try {
      await api.acknowledgeAlert(alertId);
      setAlerts(alerts.map(a => a.id === alertId ? { ...a, status: 'acknowledged' } : a));
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const handleResolve = async (alertId) => {
    // First try realtime alert
    resolveRealtimeAlert(alertId);
    try {
      await api.resolveAlert(alertId);
      setAlerts(alerts.map(a => a.id === alertId ? { ...a, status: 'resolved' } : a));
    } catch (err) {
      console.error('Failed to resolve alert:', err);
    }
  };

  const handleBulkAcknowledge = async () => {
    try {
      await api.bulkAcknowledgeAlerts(selectedAlerts);
      setAlerts(alerts.map(a => selectedAlerts.includes(a.id) ? { ...a, status: 'acknowledged' } : a));
      setSelectedAlerts([]);
    } catch (err) {
      console.error('Failed to bulk acknowledge:', err);
    }
  };

  const handleSelectAlert = (id) => {
    setSelectedAlerts(prev => 
      prev.includes(id) ? prev.filter(a => a !== id) : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedAlerts.length === filteredAlerts.length) {
      setSelectedAlerts([]);
    } else {
      setSelectedAlerts(filteredAlerts.map(a => a.id));
    }
  };

  // Calculate stats from alerts if API stats not available
  const alertStats = stats || {
    total: alerts.length,
    active: alerts.filter(a => a.status === 'active').length,
    acknowledged: alerts.filter(a => a.status === 'acknowledged').length,
    resolved: alerts.filter(a => a.status === 'resolved').length,
    critical: alerts.filter(a => a.priority === 'critical').length,
  };

  // Chart data
  const priorityChartData = [
    { name: 'Critical', value: alerts.filter(a => a.priority === 'critical').length, color: '#EF4444' },
    { name: 'High', value: alerts.filter(a => a.priority === 'high').length, color: '#F97316' },
    { name: 'Medium', value: alerts.filter(a => a.priority === 'medium').length, color: '#EAB308' },
    { name: 'Low', value: alerts.filter(a => a.priority === 'low').length, color: '#3B82F6' },
  ].filter(d => d.value > 0);

  const statusChartData = [
    { name: 'Active', value: alertStats.active, color: '#EF4444' },
    { name: 'Acknowledged', value: alertStats.acknowledged, color: '#EAB308' },
    { name: 'Resolved', value: alertStats.resolved, color: '#22C55E' },
  ].filter(d => d.value > 0);

  // Alert types for filter
  const alertTypes = [...new Set(alerts.map(a => a.alert_type || a.type).filter(Boolean))];

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 mx-auto text-emerald-500 animate-spin mb-4" />
          <p className="text-slate-600">Loading alerts...</p>
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
            <h1 className="text-2xl font-bold text-slate-900">Alert Center</h1>
            <p className="text-slate-600">Monitor and manage system alerts</p>
          </div>
          <button 
            onClick={() => { fetchAlerts(); fetchStats(); }}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <StatsCard 
            icon={Bell} 
            label="Total Alerts" 
            value={alertStats.total} 
            bgColor="bg-emerald-100"
            color="text-emerald-600"
          />
          <StatsCard 
            icon={AlertTriangle} 
            label="Active" 
            value={alertStats.active}
            change={-12}
            bgColor="bg-red-100"
            color="text-red-600"
          />
          <StatsCard 
            icon={Eye} 
            label="Acknowledged" 
            value={alertStats.acknowledged}
            bgColor="bg-yellow-100"
            color="text-yellow-600"
          />
          <StatsCard 
            icon={CheckCircle} 
            label="Resolved" 
            value={alertStats.resolved}
            change={8}
            bgColor="bg-green-100"
            color="text-green-600"
          />
          <StatsCard 
            icon={AlertCircle} 
            label="Critical" 
            value={alertStats.critical}
            bgColor="bg-orange-100"
            color="text-orange-600"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Alerts List */}
          <div className="lg:col-span-2 space-y-4">
            {/* Search and Filter Bar */}
            <div className="bg-white rounded-xl p-4 shadow-sm border border-slate-200">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search alerts..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-slate-900"
                  />
                </div>
                <button 
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg text-slate-700 hover:bg-gray-200 transition-colors"
                >
                  <Filter className="w-4 h-4" />
                  Filters
                  <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
                </button>
              </div>

              {/* Filter Options */}
              {showFilters && (
                <div className="flex flex-wrap gap-4 mt-4 pt-4 border-t border-slate-200">
                  <div>
                    <label className="block text-xs text-slate-600 mb-1">Status</label>
                    <select
                      value={filters.status}
                      onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                      className="px-3 py-2 bg-gray-50 border border-slate-300 rounded-lg text-sm text-slate-700"
                    >
                      <option value="all">All Status</option>
                      <option value="active">Active</option>
                      <option value="acknowledged">Acknowledged</option>
                      <option value="resolved">Resolved</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-slate-600 mb-1">Priority</label>
                    <select
                      value={filters.priority}
                      onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                      className="px-3 py-2 bg-gray-50 border border-slate-300 rounded-lg text-sm text-slate-700"
                    >
                      <option value="all">All Priorities</option>
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                  {alertTypes.length > 0 && (
                    <div>
                      <label className="block text-xs text-slate-600 mb-1">Type</label>
                      <select
                        value={filters.type}
                        onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                        className="px-3 py-2 bg-gray-50 border border-slate-300 rounded-lg text-sm text-slate-700"
                      >
                        <option value="all">All Types</option>
                        {alertTypes.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Bulk Actions */}
            {selectedAlerts.length > 0 && (
              <div className="bg-blue-50 dark:bg-blue-900/30 rounded-xl p-4 flex items-center justify-between">
                <span className="text-sm text-blue-700 dark:text-blue-400">
                  {selectedAlerts.length} alert{selectedAlerts.length > 1 ? 's' : ''} selected
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleBulkAcknowledge}
                    className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-yellow-700 bg-yellow-100 rounded-lg hover:bg-yellow-200 dark:bg-yellow-900/50 dark:text-yellow-400 transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    Acknowledge All
                  </button>
                  <button
                    onClick={() => setSelectedAlerts([])}
                    className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 transition-colors"
                  >
                    <X className="w-4 h-4" />
                    Clear
                  </button>
                </div>
              </div>
            )}

            {/* Select All */}
            <div className="flex items-center justify-between px-2">
              <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedAlerts.length === filteredAlerts.length && filteredAlerts.length > 0}
                  onChange={handleSelectAll}
                  className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                />
                Select All
              </label>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {filteredAlerts.length} alert{filteredAlerts.length !== 1 ? 's' : ''}
              </span>
            </div>

            {/* Alerts */}
            {filteredAlerts.length === 0 ? (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm text-center">
                <BellOff className="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
                <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300">No Alerts Found</h3>
                <p className="text-gray-500 dark:text-gray-400 mt-2">
                  {searchQuery || filters.status !== 'all' || filters.priority !== 'all' 
                    ? 'Try adjusting your filters' 
                    : 'All systems are running smoothly'}
                </p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[calc(100vh-450px)] overflow-y-auto pr-2">
                {filteredAlerts.map((alert) => (
                  <AlertCard 
                    key={alert.id} 
                    alert={alert} 
                    onAcknowledge={handleAcknowledge}
                    onResolve={handleResolve}
                    selected={selectedAlerts.includes(alert.id)}
                    onSelect={handleSelectAlert}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Charts Sidebar */}
          <div className="space-y-6">
            {/* Priority Distribution */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <PieChartIcon className="w-5 h-5 text-gray-500" />
                By Priority
              </h3>
              {priorityChartData.length > 0 ? (
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={priorityChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={70}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {priorityChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                        formatter={(value, name) => [value, name]}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <p className="text-center text-gray-500 dark:text-gray-400 py-8">No data</p>
              )}
              <div className="grid grid-cols-2 gap-2 mt-4">
                {priorityChartData.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></span>
                    <span className="text-xs text-gray-600 dark:text-gray-400">{item.name}: {item.value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Status Distribution */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-gray-500" />
                By Status
              </h3>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={statusChartData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                    <XAxis type="number" stroke="#9CA3AF" fontSize={12} />
                    <YAxis type="category" dataKey="name" stroke="#9CA3AF" fontSize={12} width={80} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                      formatter={(value) => [value, 'Count']}
                    />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                      {statusChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <button 
                  onClick={() => setFilters({ status: 'active', priority: 'critical', type: 'all' })}
                  className="w-full flex items-center gap-3 px-4 py-3 bg-red-50 dark:bg-red-900/20 rounded-lg text-red-700 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                >
                  <AlertTriangle className="w-5 h-5" />
                  View Critical Alerts
                </button>
                <button 
                  onClick={() => setFilters({ status: 'active', priority: 'all', type: 'all' })}
                  className="w-full flex items-center gap-3 px-4 py-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-yellow-700 dark:text-yellow-400 hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors"
                >
                  <Bell className="w-5 h-5" />
                  View Active Alerts
                </button>
                <button 
                  onClick={() => setFilters({ status: 'all', priority: 'all', type: 'all' })}
                  className="w-full flex items-center gap-3 px-4 py-3 bg-gray-50 dark:bg-gray-700 rounded-lg text-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <RefreshCw className="w-5 h-5" />
                  Clear Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Alerts;
