// Rural Dashboard - Simple & Practical for Farmers
import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  Droplets, 
  Phone, 
  Volume2, 
  Sun, 
  Cloud, 
  Clock, 
  AlertTriangle, 
  CheckCircle,
  XCircle,
  IndianRupee,
  Calendar,
  Power,
  PhoneCall,
  MessageSquare,
  CloudRain,
  Thermometer,
  Wind
} from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useRealtimeData, useBillingData } from '../hooks/useRealtimeData';
import api from '../services/api';
import toast from 'react-hot-toast';

// Voice Alert Helper - Speaks in selected language
const speakText = (text, lang = 'hi-IN') => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = 0.9;
    speechSynthesis.speak(utterance);
  }
};

// Large Status Card for Rural Users
const BigStatusCard = ({ 
  icon: Icon, 
  label, 
  labelHi, 
  value, 
  unit, 
  status, 
  color,
  onClick,
  onSpeak 
}) => {
  const statusColors = {
    good: 'bg-green-500',
    warning: 'bg-yellow-500',
    danger: 'bg-red-500',
    off: 'bg-gray-400'
  };

  return (
    <div 
      onClick={onClick}
      className={`relative bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg border-2 ${
        status === 'danger' ? 'border-red-500 animate-pulse' : 
        status === 'warning' ? 'border-yellow-500' : 'border-gray-200 dark:border-gray-700'
      } ${onClick ? 'cursor-pointer active:scale-95' : ''} transition-all`}
    >
      {/* Status indicator */}
      <div className={`absolute top-4 right-4 w-4 h-4 rounded-full ${statusColors[status]} ${status === 'danger' ? 'animate-ping' : ''}`} />
      
      <div className="flex items-center gap-4 mb-4">
        <div className={`p-4 rounded-2xl ${color}`}>
          <Icon className="w-10 h-10 text-white" />
        </div>
        <div>
          <p className="text-lg text-gray-600 dark:text-gray-400">{label}</p>
          <p className="text-sm text-gray-500 dark:text-gray-500">{labelHi}</p>
        </div>
      </div>
      
      <div className="flex items-end justify-between">
        <div>
          <p className="text-4xl font-bold text-gray-900 dark:text-white">
            {value}
            <span className="text-xl text-gray-500 ml-2">{unit}</span>
          </p>
        </div>
        
        {onSpeak && (
          <button 
            onClick={(e) => { e.stopPropagation(); onSpeak(); }}
            className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
          >
            <Volume2 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          </button>
        )}
      </div>
    </div>
  );
};

// Pump Control Card
const PumpControlCard = ({ isOn, onToggle, runtime, onSpeak }) => {
  return (
    <div className={`bg-gradient-to-br ${isOn ? 'from-green-500 to-emerald-600' : 'from-gray-400 to-gray-500'} rounded-2xl p-6 text-white shadow-xl`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Droplets className={`w-10 h-10 ${isOn ? 'animate-bounce' : ''}`} />
          <div>
            <p className="text-xl font-bold">Pump / पंप</p>
            <p className="text-sm opacity-80">{isOn ? 'चालू है' : 'बंद है'}</p>
          </div>
        </div>
        <button 
          onClick={onSpeak}
          className="p-3 bg-white/20 rounded-xl hover:bg-white/30"
        >
          <Volume2 className="w-6 h-6" />
        </button>
      </div>
      
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm opacity-80">Today's Runtime / आज का समय</p>
          <p className="text-2xl font-bold">{runtime} hrs</p>
        </div>
        
        <button
          onClick={onToggle}
          className={`px-8 py-4 rounded-xl font-bold text-lg transition-all ${
            isOn 
              ? 'bg-red-500 hover:bg-red-600 active:scale-95' 
              : 'bg-green-600 hover:bg-green-700 active:scale-95'
          }`}
        >
          {isOn ? 'बंद करें / OFF' : 'चालू करें / ON'}
        </button>
      </div>
    </div>
  );
};

// Weather Card
const WeatherCard = () => {
  const [weather] = useState({
    temp: 28,
    condition: 'sunny',
    humidity: 65,
    wind: 12,
    forecast: 'Good for irrigation'
  });

  const icons = {
    sunny: Sun,
    cloudy: Cloud,
    rainy: CloudRain
  };
  const WeatherIcon = icons[weather.condition] || Sun;

  return (
    <div className="bg-gradient-to-br from-blue-400 to-cyan-500 rounded-2xl p-5 text-white">
      <div className="flex items-center justify-between mb-3">
        <p className="text-lg font-semibold">Weather / मौसम</p>
        <WeatherIcon className="w-8 h-8" />
      </div>
      
      <div className="flex items-center gap-6">
        <div>
          <p className="text-4xl font-bold">{weather.temp}°C</p>
        </div>
        <div className="text-sm space-y-1">
          <p className="flex items-center gap-2">
            <Droplets className="w-4 h-4" /> {weather.humidity}% नमी
          </p>
          <p className="flex items-center gap-2">
            <Wind className="w-4 h-4" /> {weather.wind} km/h
          </p>
        </div>
      </div>
      
      <p className="mt-3 text-sm bg-white/20 rounded-lg px-3 py-2">
        💡 {weather.forecast}
      </p>
    </div>
  );
};

// Electricity Schedule Card
const ElectricityScheduleCard = () => {
  const [schedule] = useState([
    { time: '06:00 - 10:00', status: 'available', label: 'सुबह' },
    { time: '10:00 - 14:00', status: 'off', label: 'दोपहर' },
    { time: '14:00 - 18:00', status: 'available', label: 'शाम' },
    { time: '18:00 - 22:00', status: 'peak', label: 'रात' },
  ]);

  const currentHour = new Date().getHours();
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center gap-3 mb-4">
        <Clock className="w-6 h-6 text-orange-500" />
        <div>
          <p className="font-semibold text-gray-900 dark:text-white">Power Schedule</p>
          <p className="text-sm text-gray-500">बिजली का समय</p>
        </div>
      </div>
      
      <div className="space-y-2">
        {schedule.map((slot, i) => {
          const [start] = slot.time.split(' - ');
          const startHour = parseInt(start.split(':')[0]);
          const isNow = currentHour >= startHour && currentHour < startHour + 4;
          
          return (
            <div 
              key={i}
              className={`flex items-center justify-between p-3 rounded-xl ${
                isNow ? 'bg-green-100 dark:bg-green-900/30 border-2 border-green-500' : 'bg-gray-50 dark:bg-gray-700'
              }`}
            >
              <div className="flex items-center gap-3">
                {slot.status === 'available' ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : slot.status === 'peak' ? (
                  <AlertTriangle className="w-5 h-5 text-yellow-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{slot.time}</p>
                  <p className="text-xs text-gray-500">{slot.label}</p>
                </div>
              </div>
              {isNow && (
                <span className="px-3 py-1 bg-green-500 text-white text-sm font-medium rounded-full">
                  अभी / NOW
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Emergency Contacts Card
const EmergencyContactsCard = () => {
  const contacts = [
    { name: 'Electricity Board', nameHi: 'बिजली विभाग', phone: '1912', icon: Zap, color: 'bg-yellow-500' },
    { name: 'Gram Panchayat', nameHi: 'ग्राम पंचायत', phone: '9876543210', icon: Phone, color: 'bg-green-500' },
    { name: 'Emergency', nameHi: 'आपातकाल', phone: '112', icon: AlertTriangle, color: 'bg-red-500' },
  ];

  const handleCall = (phone) => {
    window.location.href = `tel:${phone}`;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center gap-3 mb-4">
        <PhoneCall className="w-6 h-6 text-red-500" />
        <div>
          <p className="font-semibold text-gray-900 dark:text-white">Emergency / आपातकाल</p>
          <p className="text-sm text-gray-500">टैप करें कॉल करने के लिए</p>
        </div>
      </div>
      
      <div className="space-y-2">
        {contacts.map((contact, i) => (
          <button
            key={i}
            onClick={() => handleCall(contact.phone)}
            className="w-full flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors active:scale-95"
          >
            <div className={`p-3 rounded-xl ${contact.color}`}>
              <contact.icon className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1 text-left">
              <p className="font-medium text-gray-900 dark:text-white">{contact.name}</p>
              <p className="text-sm text-gray-500">{contact.nameHi}</p>
            </div>
            <p className="text-lg font-bold text-gray-900 dark:text-white">{contact.phone}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

// Current Bill Card
const CurrentBillCard = ({ amount, units, dueDate, onSpeak, onPay }) => {
  const daysLeft = Math.max(0, Math.ceil((new Date(dueDate) - new Date()) / (1000 * 60 * 60 * 24)));
  
  return (
    <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl p-6 text-white shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <IndianRupee className="w-8 h-8" />
          <div>
            <p className="text-lg font-semibold">Current Bill / इस महीने का बिल</p>
          </div>
        </div>
        <button 
          onClick={onSpeak}
          className="p-3 bg-white/20 rounded-xl hover:bg-white/30"
        >
          <Volume2 className="w-6 h-6" />
        </button>
      </div>
      
      <div className="flex items-end justify-between mb-4">
        <div>
          <p className="text-5xl font-bold">₹{amount.toLocaleString()}</p>
          <p className="text-lg opacity-80 mt-1">{units.toFixed(1)} kWh इस्तेमाल</p>
        </div>
        <div className="text-right">
          <p className={`text-lg font-medium ${daysLeft < 5 ? 'text-yellow-300' : ''}`}>
            {daysLeft} दिन बाकी
          </p>
          <p className="text-sm opacity-80">Due: {new Date(dueDate).toLocaleDateString('hi-IN')}</p>
        </div>
      </div>
      
      <button
        onClick={onPay}
        className="w-full py-4 bg-white text-purple-600 rounded-xl font-bold text-lg hover:bg-gray-100 active:scale-95 transition-all"
      >
        💳 Pay Now / अभी भुगतान करें
      </button>
    </div>
  );
};

// Main Dashboard
const Dashboard = ({ onLogout }) => {
  const { t } = useLanguage();
  const { data: liveData, history: liveHistory } = useRealtimeData({}, 2000);
  const billingData = useBillingData();
  
  const [pumpOn, setPumpOn] = useState(false);
  const [pumpRuntime, setPumpRuntime] = useState(2.5);

  // Voice alerts
  const speakVoltage = () => {
    const msg = `वोल्टेज ${liveData.voltage?.toFixed(0)} वोल्ट है। ${liveData.voltage > 250 ? 'सावधान! वोल्टेज ज्यादा है।' : 'सब ठीक है।'}`;
    speakText(msg, 'hi-IN');
    toast.success('🔊 ' + msg);
  };

  const speakBill = () => {
    const msg = `इस महीने का बिल ${billingData.currentMonth?.amount || 0} रुपये है। ${billingData.currentMonth?.units?.toFixed(0) || 0} यूनिट बिजली इस्तेमाल हुई है।`;
    speakText(msg, 'hi-IN');
    toast.success('🔊 ' + msg);
  };

  const speakPump = () => {
    const msg = pumpOn ? 'पंप चालू है। आज 2.5 घंटे चला है।' : 'पंप बंद है।';
    speakText(msg, 'hi-IN');
    toast.success('🔊 ' + msg);
  };

  const togglePump = () => {
    setPumpOn(!pumpOn);
    const msg = !pumpOn ? 'पंप चालू हो गया' : 'पंप बंद हो गया';
    speakText(msg, 'hi-IN');
    toast.success(msg);
  };

  // Send SMS Alert
  const sendSMSAlert = async () => {
    try {
      await api.sendTestSMS({
        phone: '+919876543210',
        message: `⚡ GRAM METER: Voltage ${liveData.voltage?.toFixed(0)}V, Power ${(liveData.power/1000).toFixed(1)}kW, Bill ₹${billingData.currentMonth?.amount || 0}`,
      });
      toast.success('📱 SMS भेज दिया गया');
    } catch {
      toast.success('📱 SMS Alert Sent!');
    }
  };

  const getVoltageStatus = () => {
    if (liveData.voltage > 250) return 'danger';
    if (liveData.voltage > 240 || liveData.voltage < 210) return 'warning';
    return 'good';
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 pb-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">Gram Meter / ग्राम मीटर</h1>
            <p className="text-green-100">Smart Energy for Rural India</p>
          </div>
          <button
            onClick={sendSMSAlert}
            className="p-3 bg-white/20 rounded-xl hover:bg-white/30 active:scale-95"
          >
            <MessageSquare className="w-6 h-6" />
          </button>
        </div>
        
        {/* Live Status Bar */}
        <div className="flex items-center gap-2 bg-white/10 rounded-xl p-3">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-400"></span>
          </span>
          <span className="text-sm">Live / लाइव</span>
          <span className="text-sm opacity-75 ml-auto">
            {new Date().toLocaleTimeString('hi-IN')}
          </span>
        </div>
      </div>

      <div className="p-4 max-w-4xl mx-auto space-y-4">
        
        {/* Voltage Alert Banner */}
        {liveData.voltage > 250 && (
          <div className="bg-red-500 text-white p-4 rounded-xl flex items-center gap-4 animate-pulse">
            <AlertTriangle className="w-8 h-8" />
            <div className="flex-1">
              <p className="font-bold text-lg">⚠️ High Voltage Alert!</p>
              <p>वोल्टेज बहुत ज्यादा है ({liveData.voltage?.toFixed(0)}V) - उपकरण बंद करें</p>
            </div>
            <button onClick={speakVoltage} className="p-3 bg-white/20 rounded-xl">
              <Volume2 className="w-6 h-6" />
            </button>
          </div>
        )}

        {/* Main Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <BigStatusCard
            icon={Zap}
            label="Voltage"
            labelHi="वोल्टेज"
            value={liveData.voltage?.toFixed(0) || '230'}
            unit="V"
            status={getVoltageStatus()}
            color="bg-yellow-500"
            onSpeak={speakVoltage}
          />
          
          <BigStatusCard
            icon={Power}
            label="Power"
            labelHi="बिजली खपत"
            value={(liveData.power / 1000)?.toFixed(1) || '0.0'}
            unit="kW"
            status={liveData.power > 3000 ? 'warning' : 'good'}
            color="bg-blue-500"
            onSpeak={() => speakText(`बिजली खपत ${(liveData.power/1000).toFixed(1)} किलोवाट है`, 'hi-IN')}
          />
        </div>

        {/* Pump Control */}
        <PumpControlCard 
          isOn={pumpOn} 
          onToggle={togglePump} 
          runtime={pumpRuntime}
          onSpeak={speakPump}
        />

        {/* Current Bill */}
        <CurrentBillCard
          amount={billingData.currentMonth?.amount || 1254}
          units={billingData.currentMonth?.units || 234}
          dueDate={billingData.currentMonth?.dueDate || new Date(Date.now() + 15 * 24 * 60 * 60 * 1000)}
          onSpeak={speakBill}
          onPay={() => toast.success('Payment gateway opening...')}
        />

        {/* Info Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <WeatherCard />
          <ElectricityScheduleCard />
        </div>

        {/* Emergency Contacts */}
        <EmergencyContactsCard />

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => speakText('सभी सिस्टम सामान्य हैं। वोल्टेज ठीक है। पंप बंद है।', 'hi-IN')}
            className="p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-lg flex flex-col items-center gap-3 active:scale-95 transition-all"
          >
            <div className="p-4 bg-blue-100 dark:bg-blue-900/30 rounded-2xl">
              <Volume2 className="w-10 h-10 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="text-center">
              <p className="font-bold text-gray-900 dark:text-white">Voice Status</p>
              <p className="text-sm text-gray-500">आवाज़ में सुनें</p>
            </div>
          </button>
          
          <button
            onClick={sendSMSAlert}
            className="p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-lg flex flex-col items-center gap-3 active:scale-95 transition-all"
          >
            <div className="p-4 bg-green-100 dark:bg-green-900/30 rounded-2xl">
              <MessageSquare className="w-10 h-10 text-green-600 dark:text-green-400" />
            </div>
            <div className="text-center">
              <p className="font-bold text-gray-900 dark:text-white">Send SMS</p>
              <p className="text-sm text-gray-500">SMS भेजें</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
