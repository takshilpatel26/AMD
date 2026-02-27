// Company Admin Dashboard - Electricity Distribution Monitoring
// Shows district > village > transformer > house hierarchy with loss detection

import { useState, useEffect, useCallback } from 'react';
import { 
  Building2, MapPin, Zap, Home, AlertTriangle, TrendingDown,
  ChevronRight, RefreshCw, Activity, DollarSign, Search,
  Filter, Bell, CheckCircle, XCircle, Clock, ArrowLeft,
  Gauge, Power, AlertCircle, ThermometerSun
} from 'lucide-react';
import distributionApi from '../services/distributionApi';
import toast from 'react-hot-toast';

// Severity badge colors
const severityColors = {
  critical: 'bg-red-100 text-red-800 border-red-200',
  warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  info: 'bg-blue-100 text-blue-800 border-blue-200',
  emergency: 'bg-purple-100 text-purple-800 border-purple-200',
};

const statusColors = {
  active: 'bg-green-100 text-green-800',
  maintenance: 'bg-yellow-100 text-yellow-800',
  faulty: 'bg-red-100 text-red-800',
  offline: 'bg-gray-100 text-gray-800',
};

const alertTypeIcons = {
  theft_suspected: AlertTriangle,
  power_loss: TrendingDown,
  voltage_drop: Zap,
  equipment_fault: ThermometerSun,
  overload: Gauge,
  line_fault: Power,
};

// Stats Card Component
function StatsCard({ icon: Icon, title, value, subtitle, trend, color = 'blue' }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600',
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
        {trend && (
          <span className={`text-xs font-medium ${trend > 0 ? 'text-red-500' : 'text-green-500'}`}>
            {trend > 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>
      <div className="mt-3">
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{title}</p>
        {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      </div>
    </div>
  );
}

// Alert Card Component
function AlertCard({ alert, onAcknowledge, onResolve }) {
  const AlertIcon = alertTypeIcons[alert.alert_type] || AlertTriangle;
  
  return (
    <div className={`p-4 rounded-lg border ${severityColors[alert.severity]} mb-3`}>
      <div className="flex items-start gap-3">
        <AlertIcon className="w-5 h-5 mt-0.5 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-semibold text-sm truncate">{alert.title}</span>
            <span className={`px-2 py-0.5 rounded-full text-xs ${severityColors[alert.severity]}`}>
              {alert.severity}
            </span>
          </div>
          <p className="text-xs opacity-80 mb-2">
            {alert.transformer_id_display} • {alert.village_name}
          </p>
          <div className="flex items-center gap-4 text-xs">
            <span>Loss: {parseFloat(alert.power_loss_percentage || 0).toFixed(1)}%</span>
            <span>{new Date(alert.created_at).toLocaleTimeString()}</span>
          </div>
          {alert.status === 'active' && (
            <div className="flex gap-2 mt-3">
              <button
                onClick={() => onAcknowledge(alert.id)}
                className="px-3 py-1 bg-white/50 hover:bg-white rounded text-xs font-medium flex items-center gap-1"
              >
                <CheckCircle className="w-3 h-3" /> Acknowledge
              </button>
              <button
                onClick={() => onResolve(alert.id)}
                className="px-3 py-1 bg-white/50 hover:bg-white rounded text-xs font-medium flex items-center gap-1"
              >
                <XCircle className="w-3 h-3" /> Resolve
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// District Card Component
function DistrictCard({ district, onClick, isSelected }) {
  return (
    <div
      onClick={onClick}
      className={`p-4 rounded-xl border cursor-pointer transition-all ${
        isSelected 
          ? 'bg-blue-50 border-blue-300 shadow-md' 
          : 'bg-white border-gray-200 hover:border-blue-200 hover:shadow-sm'
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <MapPin className={`w-5 h-5 ${isSelected ? 'text-blue-600' : 'text-gray-400'}`} />
          <h3 className="font-semibold text-gray-900">{district.name}</h3>
        </div>
        <ChevronRight className={`w-5 h-5 ${isSelected ? 'text-blue-600' : 'text-gray-400'}`} />
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="text-gray-500">
          Villages: <span className="font-medium text-gray-700">{district.village_count}</span>
        </div>
        <div className="text-gray-500">
          Alerts: <span className={`font-medium ${district.active_alerts > 0 ? 'text-red-600' : 'text-green-600'}`}>
            {district.active_alerts}
          </span>
        </div>
      </div>
    </div>
  );
}

// Village Card Component
function VillageCard({ village, onClick, isSelected }) {
  return (
    <div
      onClick={onClick}
      className={`p-4 rounded-xl border cursor-pointer transition-all ${
        isSelected 
          ? 'bg-green-50 border-green-300 shadow-md' 
          : 'bg-white border-gray-200 hover:border-green-200 hover:shadow-sm'
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Building2 className={`w-5 h-5 ${isSelected ? 'text-green-600' : 'text-gray-400'}`} />
          <h3 className="font-semibold text-gray-900">{village.name}</h3>
        </div>
        <ChevronRight className={`w-5 h-5 ${isSelected ? 'text-green-600' : 'text-gray-400'}`} />
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="text-gray-500">
          Transformers: <span className="font-medium text-gray-700">{village.transformer_count}</span>
        </div>
        <div className="text-gray-500">
          Alerts: <span className={`font-medium ${village.active_alerts > 0 ? 'text-red-600' : 'text-green-600'}`}>
            {village.active_alerts}
          </span>
        </div>
      </div>
    </div>
  );
}

// Transformer Card Component
function TransformerCard({ transformer, onClick, isSelected }) {
  return (
    <div
      onClick={onClick}
      className={`p-4 rounded-xl border cursor-pointer transition-all ${
        isSelected 
          ? 'bg-yellow-50 border-yellow-300 shadow-md' 
          : 'bg-white border-gray-200 hover:border-yellow-200 hover:shadow-sm'
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Zap className={`w-5 h-5 ${isSelected ? 'text-yellow-600' : 'text-gray-400'}`} />
          <h3 className="font-semibold text-gray-900 text-sm">{transformer.transformer_id}</h3>
        </div>
        <span className={`px-2 py-0.5 rounded-full text-xs ${statusColors[transformer.status]}`}>
          {transformer.status}
        </span>
      </div>
      <p className="text-xs text-gray-500 mb-2">{transformer.name}</p>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="text-gray-500">
          Houses: <span className="font-medium text-gray-700">{transformer.house_count}</span>
        </div>
        <div className="text-gray-500">
          Alerts: <span className={`font-medium ${transformer.active_alerts > 0 ? 'text-red-600' : 'text-green-600'}`}>
            {transformer.active_alerts}
          </span>
        </div>
      </div>
    </div>
  );
}

// House Card Component
function HouseCard({ house, onClick }) {
  const hasAlert = house.has_alert;
  const statusColor = house.status === 'normal' ? 'green' : house.status === 'loss_detected' ? 'yellow' : 'red';
  
  return (
    <div
      onClick={onClick}
      className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-sm ${
        hasAlert ? 'border-red-200 bg-red-50' : 'border-gray-200 bg-white hover:border-blue-200'
      }`}
    >
      <div className="flex items-center gap-2 mb-2">
        <Home className={`w-4 h-4 ${hasAlert ? 'text-red-500' : 'text-gray-400'}`} />
        <span className="font-medium text-sm text-gray-900 truncate">{house.consumer_id}</span>
        {hasAlert && <AlertTriangle className="w-4 h-4 text-red-500 ml-auto" />}
      </div>
      <p className="text-xs text-gray-500 truncate">{house.consumer_name}</p>
      <div className="flex items-center gap-2 mt-2">
        <span className={`w-2 h-2 rounded-full bg-${statusColor}-500`}></span>
        <span className="text-xs text-gray-500 capitalize">{house.status?.replace('_', ' ') || 'Unknown'}</span>
      </div>
    </div>
  );
}

// House Detail Modal
function HouseDetailModal({ house, readings, alerts, onClose }) {
  if (!house) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{house.consumer_id}</h2>
              <p className="text-sm text-gray-500">{house.consumer_name}</p>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full">
              <XCircle className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>
        
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {/* House Info */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <p className="text-sm text-gray-500">Address</p>
              <p className="font-medium text-gray-900">{house.address}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Connection Type</p>
              <p className="font-medium text-gray-900 capitalize">{house.connection_type}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Connected Load</p>
              <p className="font-medium text-gray-900">{house.connected_load_kw} kW</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Meter Number</p>
              <p className="font-medium text-gray-900">{house.meter_number}</p>
            </div>
          </div>

          {/* Latest Reading */}
          {house.latest_reading && (
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Latest Reading</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Voltage Sent</p>
                    <p className="font-bold text-lg text-gray-900">{house.latest_reading.voltage_sent}V</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Voltage Received</p>
                    <p className="font-bold text-lg text-gray-900">{house.latest_reading.voltage_received}V</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Voltage Loss</p>
                    <p className={`font-bold text-lg ${
                      parseFloat(house.latest_reading.voltage_loss_percentage || 0) > 5 ? 'text-red-600' : 'text-green-600'
                    }`}>
                      {parseFloat(house.latest_reading.voltage_loss_percentage || 0).toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">Power Loss</p>
                    <p className={`font-bold text-lg ${
                      parseFloat(house.latest_reading.power_loss_percentage || 0) > 5 ? 'text-red-600' : 'text-green-600'
                    }`}>
                      {parseFloat(house.latest_reading.power_loss_percentage || 0).toFixed(2)}%
                    </p>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    house.latest_reading.status === 'normal' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {house.latest_reading.status?.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Recent Alerts */}
          {alerts && alerts.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Recent Alerts</h3>
              <div className="space-y-2">
                {alerts.slice(0, 5).map((alert) => (
                  <div key={alert.id} className={`p-3 rounded-lg ${severityColors[alert.severity]}`}>
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      <span className="font-medium text-sm">{alert.title}</span>
                    </div>
                    <p className="text-xs mt-1 opacity-80">
                      {new Date(alert.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Main Dashboard Component
export default function CompanyAdminDashboard() {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedDistrict, setSelectedDistrict] = useState(null);
  const [selectedVillage, setSelectedVillage] = useState(null);
  const [selectedTransformer, setSelectedTransformer] = useState(null);
  const [selectedHouse, setSelectedHouse] = useState(null);
  
  const [villages, setVillages] = useState([]);
  const [transformers, setTransformers] = useState([]);
  const [houses, setHouses] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [houseAlerts, setHouseAlerts] = useState([]);
  
  const [simulatorRunning, setSimulatorRunning] = useState(false);

  // Fetch main dashboard data
  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      const data = await distributionApi.getDashboard();
      setDashboardData(data);
      setAlerts(data.recent_alerts || []);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch villages when district selected
  const fetchVillages = useCallback(async (districtId) => {
    try {
      const data = await distributionApi.getDistrictVillages(districtId);
      setVillages(data);
    } catch (error) {
      console.error('Error fetching villages:', error);
      toast.error('Failed to load villages');
    }
  }, []);

  // Fetch transformers when village selected
  const fetchTransformers = useCallback(async (villageId) => {
    try {
      const data = await distributionApi.getVillageTransformers(villageId);
      setTransformers(data);
    } catch (error) {
      console.error('Error fetching transformers:', error);
      toast.error('Failed to load transformers');
    }
  }, []);

  // Fetch houses when transformer selected
  const fetchHouses = useCallback(async (transformerId) => {
    try {
      const data = await distributionApi.getTransformerHouses(transformerId);
      setHouses(data);
    } catch (error) {
      console.error('Error fetching houses:', error);
      toast.error('Failed to load houses');
    }
  }, []);

  // Fetch house details
  const fetchHouseDetails = useCallback(async (houseId) => {
    try {
      const [house, alerts] = await Promise.all([
        distributionApi.getHouse(houseId),
        distributionApi.getHouseAlerts(houseId),
      ]);
      setSelectedHouse(house);
      setHouseAlerts(alerts);
    } catch (error) {
      console.error('Error fetching house details:', error);
      toast.error('Failed to load house details');
    }
  }, []);

  // Run simulator
  const runSimulator = useCallback(async () => {
    try {
      setSimulatorRunning(true);
      const result = await distributionApi.runSimulator({
        company_id: dashboardData?.company?.id,
      });
      toast.success(`Generated ${result.readings_generated} readings, ${result.anomalies_detected} anomalies detected`);
      await fetchDashboard();
    } catch (error) {
      console.error('Error running simulator:', error);
      toast.error('Failed to run simulator');
    } finally {
      setSimulatorRunning(false);
    }
  }, [dashboardData, fetchDashboard]);

  // Alert actions
  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await distributionApi.acknowledgeAlert(alertId);
      toast.success('Alert acknowledged');
      await fetchDashboard();
    } catch (error) {
      toast.error('Failed to acknowledge alert');
    }
  };

  const handleResolveAlert = async (alertId) => {
    try {
      await distributionApi.resolveAlert(alertId);
      toast.success('Alert resolved');
      await fetchDashboard();
    } catch (error) {
      toast.error('Failed to resolve alert');
    }
  };

  // Handle district selection
  const handleDistrictSelect = (district) => {
    setSelectedDistrict(district);
    setSelectedVillage(null);
    setSelectedTransformer(null);
    setVillages([]);
    setTransformers([]);
    setHouses([]);
    fetchVillages(district.id);
  };

  // Handle village selection
  const handleVillageSelect = (village) => {
    setSelectedVillage(village);
    setSelectedTransformer(null);
    setTransformers([]);
    setHouses([]);
    fetchTransformers(village.id);
  };

  // Handle transformer selection
  const handleTransformerSelect = (transformer) => {
    setSelectedTransformer(transformer);
    setHouses([]);
    fetchHouses(transformer.id);
  };

  // Go back navigation
  const handleBack = () => {
    if (selectedTransformer) {
      setSelectedTransformer(null);
      setHouses([]);
    } else if (selectedVillage) {
      setSelectedVillage(null);
      setTransformers([]);
    } else if (selectedDistrict) {
      setSelectedDistrict(null);
      setVillages([]);
    }
  };

  // Initial load
  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  if (loading && !dashboardData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const { company, summary, districts } = dashboardData || {};

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {(selectedDistrict || selectedVillage || selectedTransformer) && (
                <button
                  onClick={handleBack}
                  className="p-2 hover:bg-gray-100 rounded-lg"
                >
                  <ArrowLeft className="w-5 h-5 text-gray-600" />
                </button>
              )}
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  {company?.name || 'Distribution Network'}
                </h1>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <span>{company?.code}</span>
                  {selectedDistrict && (
                    <>
                      <ChevronRight className="w-4 h-4" />
                      <span>{selectedDistrict.name}</span>
                    </>
                  )}
                  {selectedVillage && (
                    <>
                      <ChevronRight className="w-4 h-4" />
                      <span>{selectedVillage.name}</span>
                    </>
                  )}
                  {selectedTransformer && (
                    <>
                      <ChevronRight className="w-4 h-4" />
                      <span>{selectedTransformer.transformer_id}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={runSimulator}
                disabled={simulatorRunning}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 
                         disabled:opacity-50 flex items-center gap-2 text-sm font-medium"
              >
                {simulatorRunning ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Activity className="w-4 h-4" />
                )}
                Run Simulator
              </button>
              <button
                onClick={fetchDashboard}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <RefreshCw className={`w-5 h-5 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
          <StatsCard
            icon={MapPin}
            title="Districts"
            value={summary?.total_districts || 0}
            color="blue"
          />
          <StatsCard
            icon={Building2}
            title="Villages"
            value={summary?.total_villages || 0}
            color="green"
          />
          <StatsCard
            icon={Zap}
            title="Transformers"
            value={summary?.total_transformers || 0}
            color="yellow"
          />
          <StatsCard
            icon={Home}
            title="Houses"
            value={summary?.total_houses || 0}
            color="purple"
          />
          <StatsCard
            icon={AlertTriangle}
            title="Active Alerts"
            value={summary?.active_alerts || 0}
            subtitle={`${summary?.critical_alerts || 0} critical`}
            color="red"
          />
          <StatsCard
            icon={DollarSign}
            title="Est. Daily Loss"
            value={`₹${(summary?.estimated_daily_loss_inr || 0).toLocaleString()}`}
            subtitle={`${(summary?.average_loss_percentage || 0).toFixed(1)}% avg loss`}
            color="red"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-2">
            {/* Districts View */}
            {!selectedDistrict && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Districts</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {districts?.map((district) => (
                    <DistrictCard
                      key={district.id}
                      district={district}
                      onClick={() => handleDistrictSelect(district)}
                      isSelected={false}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Villages View */}
            {selectedDistrict && !selectedVillage && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Villages in {selectedDistrict.name}
                </h2>
                {villages.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Building2 className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No villages found</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {villages.map((village) => (
                      <VillageCard
                        key={village.id}
                        village={village}
                        onClick={() => handleVillageSelect(village)}
                        isSelected={false}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Transformers View */}
            {selectedVillage && !selectedTransformer && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Transformers in {selectedVillage.name}
                </h2>
                {transformers.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Zap className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No transformers found</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {transformers.map((transformer) => (
                      <TransformerCard
                        key={transformer.id}
                        transformer={transformer}
                        onClick={() => handleTransformerSelect(transformer)}
                        isSelected={false}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Houses View */}
            {selectedTransformer && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Houses powered by {selectedTransformer.transformer_id}
                </h2>
                {houses.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Home className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No houses found</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {houses.map((house) => (
                      <HouseCard
                        key={house.id}
                        house={house}
                        onClick={() => fetchHouseDetails(house.id)}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Alerts Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 sticky top-24">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Bell className="w-5 h-5 text-red-500" />
                  Active Alerts
                </h2>
                <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
                  {alerts.length}
                </span>
              </div>
              
              <div className="max-h-[60vh] overflow-y-auto">
                {alerts.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-500 opacity-50" />
                    <p>No active alerts</p>
                    <p className="text-sm mt-1">All systems operating normally</p>
                  </div>
                ) : (
                  alerts.map((alert) => (
                    <AlertCard
                      key={alert.id}
                      alert={alert}
                      onAcknowledge={handleAcknowledgeAlert}
                      onResolve={handleResolveAlert}
                    />
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* House Detail Modal */}
      {selectedHouse && (
        <HouseDetailModal
          house={selectedHouse}
          alerts={houseAlerts}
          onClose={() => {
            setSelectedHouse(null);
            setHouseAlerts([]);
          }}
        />
      )}
    </div>
  );
}
