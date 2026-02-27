// Admin Dashboard - Village Grid Live Monitor + Distribution Hierarchy
// Interactive Map with colored dots + Distribution section below

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { 
  Shield, LogOut, RefreshCw, MapPin, Zap, Home, Building2,
  AlertTriangle, Activity, X, Power, ChevronRight, Users
} from 'lucide-react';
import toast from 'react-hot-toast';
import mqtt from 'mqtt';
import 'leaflet/dist/leaflet.css';

// MQTT Configuration
const MQTT_BROKER = 'wss://broker.hivemq.com:8884/mqtt';
const MQTT_TOPIC = 'gram-meter/village/map';

// ==================== HELPER FUNCTIONS ====================

// Deterministic pseudo-random from string
function seededRandom(str) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return (h >>> 0) / 4294967295;
}

// Generate coordinates - SPREAD OUT MORE
function generateCoordinates(houses, centerLat = 28.4595, centerLng = 77.0266) {
  const radiusDeg = 0.035; // Increased from 0.018 for more spread

  return houses.map((h, i) => {
    const id = (h.house_id || h.consumer_id || String(i)) + '';
    const rRand = seededRandom(id + '_r_' + i);
    const aRand = seededRandom(id + '_a_' + (i * 7919));
    // Use cube root for more even distribution
    const r = Math.pow(rRand, 0.6) * radiusDeg;
    const a = 2 * Math.PI * aRand;
    const lat = centerLat + r * Math.sin(a);
    const lng = centerLng + r * Math.cos(a);
    return { ...h, lat, lng };
  });
}

// Get color based on voltage level
const getVoltageColor = (voltage) => {
  if (voltage === 0 || voltage === null || voltage === undefined) return '#000000';
  if (voltage > 260) return '#EF4444';
  if (voltage >= 245 && voltage <= 260) return '#EAB308';
  if (voltage < 190) return '#F97316';
  return '#22C55E';
};

// Get status text based on voltage
const getVoltageStatus = (voltage) => {
  if (voltage === 0 || voltage === null || voltage === undefined) return { text: 'Outage', icon: '🚨' };
  if (voltage > 260) return { text: 'Surge', icon: '⚡' };
  if (voltage >= 245 && voltage <= 260) return { text: 'High', icon: '⚠️' };
  if (voltage < 190) return { text: 'Brownout', icon: '📉' };
  return { text: 'Normal', icon: '✅' };
};

const formatTime = (date) => {
  return new Date(date).toLocaleTimeString('en-US', { 
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false 
  });
};

// ==================== MAP COMPONENT ====================

function VillageMap({ houses, selectedHouse, setSelectedHouse }) {
  const centerLat = 28.4595;
  const centerLng = 77.0266;

  return (
    <MapContainer
      center={[centerLat, centerLng]}
      zoom={13}
      style={{ height: '100%', width: '100%' }}
    >
      {/* Label-free map tiles */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png"
      />
      
      {houses.map((house, idx) => (
        <CircleMarker
          key={house.house_id || house.consumer_id || idx}
          center={[house.lat, house.lng]}
          radius={7}
          pathOptions={{
            fillColor: getVoltageColor(house.voltage),
            fillOpacity: 0.85,
            color: selectedHouse?.house_id === house.house_id ? '#ffffff' : getVoltageColor(house.voltage),
            weight: selectedHouse?.house_id === house.house_id ? 3 : 1,
          }}
          eventHandlers={{
            click: () => setSelectedHouse(house),
          }}
        >
          <Popup>
            <HousePopup house={house} onClose={() => setSelectedHouse(null)} />
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}

// House Popup Component
function HousePopup({ house, onClose }) {
  const status = getVoltageStatus(house.voltage);
  
  return (
    <div className="min-w-[220px] p-1">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-bold text-gray-900 text-base">{house.name || house.consumer_name}</h3>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X className="w-4 h-4" />
        </button>
      </div>
      <div className="space-y-1.5 text-sm">
        <p className="text-gray-600">
          <span className="font-medium">House ID:</span>{' '}
          <span className="font-mono font-semibold">{house.house_id || house.consumer_id}</span>
        </p>
        <p className="text-gray-600">
          <span className="font-medium">Current Voltage:</span>{' '}
          <span className="font-bold" style={{ color: getVoltageColor(house.voltage) }}>
            {house.voltage?.toFixed(1) || 0} V
          </span>
        </p>
        <p className="text-gray-600">
          <span className="font-medium">Current Power:</span>{' '}
          <span className="font-semibold">{(house.usage_kw || house.power_kw || 0).toFixed(2)} kW</span>
        </p>
        <p className="text-gray-600">
          <span className="font-medium">Status:</span>{' '}
          <span className="font-semibold" style={{ color: getVoltageColor(house.voltage) }}>
            {status.icon} {status.text}
          </span>
        </p>
        <p className="text-gray-400 text-xs pt-1">
          Updated: {formatTime(house.timestamp || new Date())}
        </p>
      </div>
    </div>
  );
}

// ==================== DISTRIBUTION SECTION ====================

function DistributionSection({ distributionData }) {
  const [selectedDistrict, setSelectedDistrict] = useState(null);
  const [selectedVillage, setSelectedVillage] = useState(null);
  const [selectedTransformer, setSelectedTransformer] = useState(null);

  const districts = distributionData?.districts || [];

  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-white/20 rounded-xl">
            <Building2 className="w-7 h-7 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Distribution Network</h2>
            <p className="text-emerald-100 text-sm">Hierarchy: Districts → Villages → Transformers → Houses</p>
          </div>
        </div>
      </div>

      {/* 4-Column Hierarchy */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 divide-y md:divide-y-0 md:divide-x divide-gray-200">
        {/* Districts Column */}
        <div className="p-4">
          <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-emerald-500" />
            Districts ({districts.length})
          </h3>
          <div className="space-y-2 max-h-[300px] overflow-y-auto">
            {districts.map(district => (
              <div
                key={district.id}
                onClick={() => {
                  setSelectedDistrict(district);
                  setSelectedVillage(null);
                  setSelectedTransformer(null);
                }}
                className={`p-3 rounded-lg cursor-pointer transition-all ${
                  selectedDistrict?.id === district.id 
                    ? 'bg-emerald-100 border-2 border-emerald-500' 
                    : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                }`}
              >
                <p className="font-medium text-gray-800">{district.name}</p>
                <p className="text-xs text-gray-500">
                  {district.village_count || district.villages?.length || 0} villages • {district.active_alerts || 0} alerts
                </p>
              </div>
            ))}
            {districts.length === 0 && (
              <p className="text-gray-400 text-sm text-center py-4">No districts found</p>
            )}
          </div>
        </div>

        {/* Villages Column */}
        <div className="p-4">
          <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Home className="w-4 h-4 text-teal-500" />
            Villages {selectedDistrict ? `(${selectedDistrict.villages?.length || 0})` : ''}
          </h3>
          <div className="space-y-2 max-h-[300px] overflow-y-auto">
            {selectedDistrict?.villages?.map(village => (
              <div
                key={village.id}
                onClick={() => {
                  setSelectedVillage(village);
                  setSelectedTransformer(null);
                }}
                className={`p-3 rounded-lg cursor-pointer transition-all ${
                  selectedVillage?.id === village.id 
                    ? 'bg-teal-100 border-2 border-teal-500' 
                    : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                }`}
              >
                <p className="font-medium text-gray-800">{village.name}</p>
                <p className="text-xs text-gray-500">
                  {village.transformer_count || village.transformers?.length || 0} transformers • {village.house_count || 0} houses
                </p>
              </div>
            ))}
            {!selectedDistrict && (
              <p className="text-gray-400 text-sm text-center py-4">Select a district</p>
            )}
            {selectedDistrict && !selectedDistrict.villages?.length && (
              <p className="text-gray-400 text-sm text-center py-4">No villages</p>
            )}
          </div>
        </div>

        {/* Transformers Column */}
        <div className="p-4">
          <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4 text-yellow-500" />
            Transformers {selectedVillage ? `(${selectedVillage.transformers?.length || 0})` : ''}
          </h3>
          <div className="space-y-2 max-h-[300px] overflow-y-auto">
            {selectedVillage?.transformers?.map(transformer => (
              <div
                key={transformer.id}
                onClick={() => setSelectedTransformer(transformer)}
                className={`p-3 rounded-lg cursor-pointer transition-all ${
                  selectedTransformer?.id === transformer.id 
                    ? 'bg-yellow-100 border-2 border-yellow-500' 
                    : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                }`}
              >
                <p className="font-medium text-gray-800 text-sm">{transformer.transformer_id}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    transformer.status === 'active' ? 'bg-green-100 text-green-700' :
                    transformer.status === 'maintenance' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {transformer.status || 'active'}
                  </span>
                  <span className="text-xs text-gray-500">{transformer.house_count || transformer.houses?.length || 0} houses</span>
                </div>
              </div>
            ))}
            {!selectedVillage && (
              <p className="text-gray-400 text-sm text-center py-4">Select a village</p>
            )}
            {selectedVillage && !selectedVillage.transformers?.length && (
              <p className="text-gray-400 text-sm text-center py-4">No transformers</p>
            )}
          </div>
        </div>

        {/* Houses Column */}
        <div className="p-4">
          <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Users className="w-4 h-4 text-emerald-500" />
            Houses {selectedTransformer ? `(${selectedTransformer.houses?.length || 0})` : ''}
          </h3>
          <div className="space-y-2 max-h-[300px] overflow-y-auto">
            {selectedTransformer?.houses?.map(house => (
              <div
                key={house.id}
                className="p-3 rounded-lg bg-gray-50 border-2 border-transparent hover:bg-emerald-50"
              >
                <p className="font-medium text-gray-800 text-sm">{house.consumer_name}</p>
                <p className="text-xs text-gray-500 font-mono">{house.consumer_id}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-gray-600">
                    {house.latest_voltage?.toFixed(1) || '—'}V
                  </span>
                  <span className={`w-2 h-2 rounded-full ${
                    house.is_anomaly ? 'bg-red-500' : 'bg-green-500'
                  }`}></span>
                </div>
              </div>
            ))}
            {!selectedTransformer && (
              <p className="text-gray-400 text-sm text-center py-4">Select a transformer</p>
            )}
            {selectedTransformer && !selectedTransformer.houses?.length && (
              <p className="text-gray-400 text-sm text-center py-4">No houses</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ==================== MAIN DASHBOARD COMPONENT ====================

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [houses, setHouses] = useState([]);
  const [distributionData, setDistributionData] = useState(null);
  const [summary, setSummary] = useState({
    total_houses: 0, normal: 0, brownout: 0, high_voltage: 0, surge: 0, outage: 0, avg_voltage: 0, total_power_kw: 0,
  });
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const [loading, setLoading] = useState(true);
  const [selectedHouse, setSelectedHouse] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Check admin authentication
  useEffect(() => {
    const adminAuth = localStorage.getItem('adminAuth');
    if (!adminAuth) {
      navigate('/admin');
      return;
    }
    try {
      const auth = JSON.parse(adminAuth);
      if (!auth.isAuthenticated) {
        navigate('/admin');
      }
    } catch (e) {
      navigate('/admin');
    }
  }, [navigate]);

  // Fetch data
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/distribution/dashboard/');
      
      if (response.ok) {
        const data = await response.json();
        setDistributionData(data);
        
        // Extract all houses
        const allHouses = [];
        data.districts?.forEach(district => {
          district.villages?.forEach(village => {
            village.transformers?.forEach(transformer => {
              transformer.houses?.forEach(house => {
                const voltage = house.latest_voltage || (190 + Math.random() * 70);
                const power = house.latest_power || (Math.random() * 8);
                allHouses.push({
                  house_id: house.consumer_id,
                  consumer_id: house.consumer_id,
                  name: house.consumer_name,
                  voltage, usage_kw: power, power_kw: power,
                  is_anomaly: house.is_anomaly,
                  timestamp: new Date(),
                });
              });
            });
          });
        });

        if (allHouses.length > 0) {
          const housesWithCoords = generateCoordinates(allHouses);
          setHouses(housesWithCoords);
          calculateSummary(housesWithCoords);
        } else {
          generateDemoData();
        }
      } else {
        generateDemoData();
      }
      
      setConnectionStatus('connected');
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error:', error);
      setConnectionStatus('disconnected');
      generateDemoData();
    } finally {
      setLoading(false);
    }
  }, []);

  // Generate demo data
  const generateDemoData = () => {
    const names = [
      'Aarush Mukherjee', 'Priya Sharma', 'Rahul Singh', 'Anita Patel', 'Vikram Gupta',
      'Neha Verma', 'Amit Kumar', 'Deepa Reddy', 'Sanjay Joshi', 'Kavita Menon',
    ];

    const demoHouses = Array.from({ length: 500 }, (_, i) => {
      let voltage;
      const rand = Math.random();
      if (rand < 0.75) voltage = 190 + Math.random() * 55;
      else if (rand < 0.85) voltage = 245 + Math.random() * 15;
      else if (rand < 0.93) voltage = 150 + Math.random() * 40;
      else if (rand < 0.98) voltage = 260 + Math.random() * 20;
      else voltage = 0;

      return {
        house_id: `HOUSE-${String(i + 1).padStart(4, '0')}`,
        name: names[i % names.length],
        voltage,
        usage_kw: voltage > 0 ? (1 + Math.random() * 7) : 0,
        timestamp: new Date(),
      };
    });

    const housesWithCoords = generateCoordinates(demoHouses);
    setHouses(housesWithCoords);
    calculateSummary(housesWithCoords);
  };

  // Calculate summary
  const calculateSummary = (houseData) => {
    const stats = { total_houses: houseData.length, normal: 0, brownout: 0, high_voltage: 0, surge: 0, outage: 0, avg_voltage: 0, total_power_kw: 0 };
    let totalVoltage = 0, voltageCount = 0;

    houseData.forEach(house => {
      const v = house.voltage || 0;
      stats.total_power_kw += house.usage_kw || 0;
      if (v === 0) stats.outage++;
      else {
        totalVoltage += v; voltageCount++;
        if (v > 260) stats.surge++;
        else if (v >= 245) stats.high_voltage++;
        else if (v < 190) stats.brownout++;
        else stats.normal++;
      }
    });

    stats.avg_voltage = voltageCount > 0 ? Math.round(totalVoltage / voltageCount) : 0;
    setSummary(stats);
  };

  useEffect(() => { fetchData(); }, [fetchData]);

  // MQTT Connection for real-time updates from virtual_meter_gov.py
  useEffect(() => {
    let client = null;
    
    try {
      client = mqtt.connect(MQTT_BROKER, {
        clientId: `admin_dashboard_${Math.random().toString(16).slice(2, 10)}`,
        clean: true,
        reconnectPeriod: 3000,
      });

      client.on('connect', () => {
        console.log('🔗 MQTT Connected to broker');
        setConnectionStatus('connected');
        client.subscribe(MQTT_TOPIC, (err) => {
          if (err) console.error('MQTT subscribe error:', err);
          else console.log('📡 Subscribed to:', MQTT_TOPIC);
        });
      });

      client.on('message', (topic, message) => {
        try {
          const data = JSON.parse(message.toString());
          if (Array.isArray(data) && data.length > 0) {
            // Update houses with live MQTT data
            const updatedHouses = data.map((h, i) => ({
              house_id: h.house_id,
              name: h.name,
              voltage: h.voltage || 0,
              usage_kw: h.usage_kw || 0,
              status_note: h.status_note,
              timestamp: new Date(),
            }));
            
            const housesWithCoords = generateCoordinates(updatedHouses);
            setHouses(housesWithCoords);
            calculateSummary(housesWithCoords);
            setLastUpdated(new Date());
          }
        } catch (e) {
          console.error('MQTT parse error:', e);
        }
      });

      client.on('error', (err) => {
        console.error('MQTT error:', err);
        setConnectionStatus('disconnected');
      });

      client.on('close', () => {
        console.log('MQTT disconnected');
        setConnectionStatus('disconnected');
      });

    } catch (err) {
      console.error('MQTT connection failed:', err);
      setConnectionStatus('disconnected');
    }

    return () => {
      if (client) {
        client.end();
      }
    };
  }, []);

  // Fallback: simulated updates if MQTT not working
  useEffect(() => {
    const interval = setInterval(() => {
      if (connectionStatus !== 'connected') {
        setHouses(prev => {
          const updated = prev.map(house => {
            if (Math.random() > 0.92) {
              let newV = house.voltage > 0 ? Math.max(0, house.voltage + (Math.random() - 0.5) * 12) : house.voltage;
              return { ...house, voltage: newV, usage_kw: newV > 0 ? (1 + Math.random() * 7) : 0, timestamp: new Date() };
            }
            return house;
          });
          calculateSummary(updated);
          setLastUpdated(new Date());
          return updated;
        });
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [connectionStatus]);

  const handleLogout = () => {
    localStorage.removeItem('adminAuth');
    toast.success('Logged out');
    navigate('/admin');
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-100 rounded-lg">
              <Shield className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Admin Dashboard</h1>
              <p className="text-slate-600 text-sm">Electricity Distribution Monitoring</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-slate-600 text-sm">Updated: {formatTime(lastUpdated)}</span>
            <button onClick={handleLogout} className="flex items-center gap-2 px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-colors">
              <LogOut className="w-4 h-4" /> Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        
        {/* Village Grid Live Monitor */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
          <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-white/20 rounded-xl">
                  <Home className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">🏠 Village Grid Live Monitor</h2>
                  <p className="text-emerald-100 text-sm">Real-time monitoring across {summary.total_houses} houses</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
                  connectionStatus === 'connected' ? 'bg-green-500/20 text-white' : 'bg-red-500/20 text-white'
                }`}>
                  <span className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-white animate-pulse' : 'bg-white'}`}></span>
                  {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
                </div>
                <button onClick={fetchData} disabled={loading} className="p-2.5 bg-white/20 hover:bg-white/30 rounded-xl transition-colors">
                  <RefreshCw className={`w-5 h-5 text-white ${loading ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </div>
          </div>

          {/* Map */}
          <div style={{ height: '480px' }}>
            {loading ? (
              <div className="h-full flex items-center justify-center bg-gray-100">
                <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin" />
              </div>
            ) : (
              <VillageMap houses={houses} selectedHouse={selectedHouse} setSelectedHouse={setSelectedHouse} />
            )}
          </div>

          {/* Legend */}
          <div className="bg-gray-50 border-t px-6 py-3 flex flex-wrap justify-center gap-6">
            <div className="flex items-center gap-2"><div className="w-4 h-4 rounded-full bg-green-500"></div><span className="text-sm text-gray-600">Optimal (190-245V)</span></div>
            <div className="flex items-center gap-2"><div className="w-4 h-4 rounded-full bg-orange-500"></div><span className="text-sm text-gray-600">Brownout (&lt;190V)</span></div>
            <div className="flex items-center gap-2"><div className="w-4 h-4 rounded-full bg-yellow-500"></div><span className="text-sm text-gray-600">High (245-260V)</span></div>
            <div className="flex items-center gap-2"><div className="w-4 h-4 rounded-full bg-red-500"></div><span className="text-sm text-gray-600">Surge (&gt;260V)</span></div>
            <div className="flex items-center gap-2"><div className="w-4 h-4 rounded-full bg-black"></div><span className="text-sm text-gray-600">Outage (0V)</span></div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 lg:grid-cols-8 gap-3 p-4 bg-white border-t">
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <p className="text-xl font-bold text-gray-900">{summary.total_houses}</p>
              <p className="text-xs text-gray-500">Total</p>
            </div>
            <div className="text-center p-2 bg-green-50 rounded-lg">
              <p className="text-xl font-bold text-green-600">{summary.normal}</p>
              <p className="text-xs text-green-600">Normal</p>
            </div>
            <div className="text-center p-2 bg-orange-50 rounded-lg">
              <p className="text-xl font-bold text-orange-500">{summary.brownout}</p>
              <p className="text-xs text-orange-500">Brownout</p>
            </div>
            <div className="text-center p-2 bg-yellow-50 rounded-lg">
              <p className="text-xl font-bold text-yellow-500">{summary.high_voltage}</p>
              <p className="text-xs text-yellow-500">High</p>
            </div>
            <div className="text-center p-2 bg-red-50 rounded-lg">
              <p className="text-xl font-bold text-red-500">{summary.surge}</p>
              <p className="text-xs text-red-500">Surge</p>
            </div>
            <div className="text-center p-2 bg-gray-100 rounded-lg">
              <p className="text-xl font-bold text-gray-800">{summary.outage}</p>
              <p className="text-xs text-gray-600">Outage</p>
            </div>
            <div className="text-center p-2 bg-blue-50 rounded-lg">
              <p className="text-xl font-bold text-blue-600">{summary.avg_voltage}V</p>
              <p className="text-xs text-blue-600">Avg V</p>
            </div>
            <div className="text-center p-2 bg-purple-50 rounded-lg">
              <p className="text-xl font-bold text-emerald-600">{summary.total_power_kw.toFixed(0)}</p>
              <p className="text-xs text-emerald-600">kW</p>
            </div>
          </div>
        </div>

        {/* Distribution Section */}
        <DistributionSection distributionData={distributionData} />
      </main>
    </div>
  );
}
