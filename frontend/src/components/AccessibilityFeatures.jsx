// Accessibility & Voice Alert Component - High Impact Features
import React, { useState, useEffect, useCallback } from 'react';
import {
  Volume2,
  VolumeX,
  Languages,
  Accessibility,
  Eye,
  EyeOff,
  Sun,
  Moon,
  Wifi,
  WifiOff,
  AlertTriangle,
  Bell,
  BellOff,
  MessageSquare,
  Phone,
  Mic,
  MicOff,
  Settings,
  Check
} from 'lucide-react';
import toast from 'react-hot-toast';

// Voice Alert Messages in Multiple Languages
const VOICE_MESSAGES = {
  en: {
    highVoltage: 'Warning! High voltage detected at {value} volts. Please check your electrical equipment immediately.',
    lowVoltage: 'Alert! Low voltage detected at {value} volts. Contact your electricity provider.',
    anomaly: 'Anomaly detected in your power consumption. Please review your meter readings.',
    billDue: 'Reminder: Your electricity bill of rupees {amount} is due in {days} days.',
    peakHours: 'You are using electricity during peak hours. Consider switching to off-peak usage to save money.',
    savingsTip: 'Great job! You saved {percent} percent on electricity this month compared to last month.',
    welcome: 'Welcome to Gram Meter. Your smart energy monitoring assistant.',
    dailyReport: 'Your daily energy report. Today you consumed {energy} kilowatt hours, costing approximately {cost} rupees.'
  },
  hi: {
    highVoltage: 'चेतावनी! {value} वोल्ट पर उच्च वोल्टेज का पता चला। कृपया तुरंत अपने बिजली के उपकरण की जांच करें।',
    lowVoltage: 'सावधान! {value} वोल्ट पर कम वोल्टेज का पता चला। अपने बिजली प्रदाता से संपर्क करें।',
    anomaly: 'आपकी बिजली खपत में असामान्यता का पता चला है। कृपया अपने मीटर रीडिंग की समीक्षा करें।',
    billDue: 'रिमाइंडर: आपका {amount} रुपये का बिजली बिल {days} दिनों में देय है।',
    peakHours: 'आप पीक आवर्स के दौरान बिजली का उपयोग कर रहे हैं। पैसे बचाने के लिए ऑफ-पीक उपयोग पर स्विच करें।',
    savingsTip: 'बहुत बढ़िया! आपने इस महीने पिछले महीने की तुलना में बिजली पर {percent} प्रतिशत बचत की।',
    welcome: 'ग्राम मीटर में आपका स्वागत है। आपका स्मार्ट ऊर्जा निगरानी सहायक।',
    dailyReport: 'आपकी दैनिक ऊर्जा रिपोर्ट। आज आपने {energy} किलोवाट घंटे की खपत की, जिसकी लागत लगभग {cost} रुपये है।'
  },
  gu: {
    highVoltage: 'ચેતવણી! {value} વોલ્ટ પર ઉચ્ચ વોલ્ટેજ મળી. કૃપા કરીને તમારા વિદ્યુત સાધનોની તાત્કાલિક તપાસ કરો.',
    lowVoltage: 'ચેતવણી! {value} વોલ્ટ પર ઓછું વોલ્ટેજ મળ્યું. તમારા વીજળી પ્રદાતાનો સંપર્ક કરો.',
    anomaly: 'તમારા વીજળી વપરાશમાં વિસંગતતા મળી છે. કૃપા કરીને તમારા મીટર રીડિંગની સમીક્ષા કરો.',
    billDue: 'રીમાઇન્ડર: તમારું {amount} રૂપિયાનું વીજળી બિલ {days} દિવસમાં બાકી છે.',
    peakHours: 'તમે પીક અવર્સ દરમિયાન વીજળીનો ઉપયોગ કરી રહ્યા છો. પૈસા બચાવવા ઓફ-પીક ઉપયોગ પર સ્વિચ કરો.',
    savingsTip: 'શાબાશ! તમે આ મહિને ગયા મહિનાની સરખામણીમાં વીજળી પર {percent} ટકા બચત કરી.',
    welcome: 'ગ્રામ મીટરમાં આપનું સ્વાગત છે. તમારો સ્માર્ટ ઊર્જા મોનિટરિંગ સહાયક.',
    dailyReport: 'તમારો દૈનિક ઊર્જા રિપોર્ટ. આજે તમે {energy} કિલોવોટ કલાકનો વપરાશ કર્યો, જેની અંદાજિત કિંમત {cost} રૂપિયા છે.'
  }
};

// Languages Config
const LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇬🇧', voice: 'en-IN' },
  { code: 'hi', name: 'हिंदी', flag: '🇮🇳', voice: 'hi-IN' },
  { code: 'gu', name: 'ગુજરાતી', flag: '🇮🇳', voice: 'gu-IN' }
];

// Voice Alert Hook
export const useVoiceAlert = () => {
  const [isEnabled, setIsEnabled] = useState(true);
  const [language, setLanguage] = useState('en');
  const [speaking, setSpeaking] = useState(false);
  const [volume, setVolume] = useState(1);
  
  const speak = useCallback((messageKey, params = {}) => {
    if (!isEnabled || typeof window === 'undefined' || !window.speechSynthesis) return;
    
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    let message = VOICE_MESSAGES[language]?.[messageKey] || VOICE_MESSAGES['en'][messageKey];
    if (!message) return;
    
    // Replace parameters
    Object.keys(params).forEach(key => {
      message = message.replace(`{${key}}`, params[key]);
    });
    
    const utterance = new SpeechSynthesisUtterance(message);
    const langConfig = LANGUAGES.find(l => l.code === language);
    utterance.lang = langConfig?.voice || 'en-IN';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = volume;
    
    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    
    window.speechSynthesis.speak(utterance);
  }, [isEnabled, language, volume]);
  
  const stopSpeaking = useCallback(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
    }
  }, []);
  
  return {
    speak,
    stopSpeaking,
    speaking,
    isEnabled,
    setIsEnabled,
    language,
    setLanguage,
    volume,
    setVolume
  };
};

// Accessibility Settings Panel
const AccessibilityPanel = ({ 
  voiceEnabled, 
  setVoiceEnabled,
  language,
  setLanguage,
  volume,
  setVolume,
  highContrast,
  setHighContrast,
  largeText,
  setLargeText,
  reducedMotion,
  setReducedMotion,
  offlineMode,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-xl bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        aria-label="Accessibility Settings"
      >
        <Accessibility className="w-5 h-5 text-gray-600 dark:text-gray-400" />
      </button>
      
      {isOpen && (
        <div className="absolute right-0 top-12 w-80 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 z-50 overflow-hidden">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-violet-500/10 to-purple-500/10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Accessibility className="w-5 h-5 text-violet-600" />
                <h3 className="font-semibold text-gray-900 dark:text-white">Accessibility</h3>
              </div>
              <button 
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
          </div>
          
          <div className="p-4 space-y-4 max-h-[400px] overflow-y-auto">
            {/* Voice Alerts */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {voiceEnabled ? <Volume2 className="w-4 h-4 text-emerald-500" /> : <VolumeX className="w-4 h-4 text-gray-400" />}
                  <span className="font-medium text-gray-900 dark:text-white">Voice Alerts</span>
                </div>
                <button
                  onClick={() => setVoiceEnabled(!voiceEnabled)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    voiceEnabled ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                >
                  <div className={`w-5 h-5 rounded-full bg-white shadow-sm transform transition-transform ${
                    voiceEnabled ? 'translate-x-6' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>
              
              {voiceEnabled && (
                <div className="ml-6 space-y-3">
                  {/* Volume Slider */}
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Volume</label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={volume}
                      onChange={(e) => setVolume(parseFloat(e.target.value))}
                      className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                    />
                  </div>
                  
                  {/* Language Selection */}
                  <div>
                    <label className="text-xs text-gray-500 block mb-2">Voice Language</label>
                    <div className="grid grid-cols-3 gap-2">
                      {LANGUAGES.map((lang) => (
                        <button
                          key={lang.code}
                          onClick={() => setLanguage(lang.code)}
                          className={`p-2 rounded-lg text-center transition-colors ${
                            language === lang.code
                              ? 'bg-emerald-100 dark:bg-emerald-900/30 border-2 border-emerald-500'
                              : 'bg-gray-100 dark:bg-gray-700 border-2 border-transparent hover:border-gray-300'
                          }`}
                        >
                          <span className="text-lg">{lang.flag}</span>
                          <p className="text-xs mt-1 font-medium">{lang.name}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <hr className="border-gray-200 dark:border-gray-700" />
            
            {/* High Contrast */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4 text-gray-500" />
                <span className="font-medium text-gray-900 dark:text-white">High Contrast</span>
              </div>
              <button
                onClick={() => setHighContrast(!highContrast)}
                className={`w-12 h-6 rounded-full transition-colors ${
                  highContrast ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-600'
                }`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow-sm transform transition-transform ${
                  highContrast ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            
            {/* Large Text */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 text-gray-500 font-bold text-sm">Aa</span>
                <span className="font-medium text-gray-900 dark:text-white">Large Text</span>
              </div>
              <button
                onClick={() => setLargeText(!largeText)}
                className={`w-12 h-6 rounded-full transition-colors ${
                  largeText ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-600'
                }`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow-sm transform transition-transform ${
                  largeText ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            
            {/* Reduced Motion */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Settings className="w-4 h-4 text-gray-500" />
                <span className="font-medium text-gray-900 dark:text-white">Reduced Motion</span>
              </div>
              <button
                onClick={() => setReducedMotion(!reducedMotion)}
                className={`w-12 h-6 rounded-full transition-colors ${
                  reducedMotion ? 'bg-emerald-500' : 'bg-gray-300 dark:bg-gray-600'
                }`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow-sm transform transition-transform ${
                  reducedMotion ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            
            <hr className="border-gray-200 dark:border-gray-700" />
            
            {/* Offline Mode Indicator */}
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-900/50">
              <div className="flex items-center gap-2">
                {offlineMode ? (
                  <WifiOff className="w-4 h-4 text-yellow-500" />
                ) : (
                  <Wifi className="w-4 h-4 text-emerald-500" />
                )}
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {offlineMode ? 'Offline Mode Active' : 'Connected'}
                </span>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                offlineMode 
                  ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                  : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
              }`}>
                {offlineMode ? 'Cached Data' : 'Live'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Voice Alert Button Component  
const VoiceAlertButton = ({ message, messageKey, params, language = 'en', className = '' }) => {
  const [speaking, setSpeaking] = useState(false);
  
  const speak = () => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      toast.error('Voice not supported in this browser');
      return;
    }
    
    window.speechSynthesis.cancel();
    
    const text = message || VOICE_MESSAGES[language]?.[messageKey] || '';
    if (!text) return;
    
    let finalText = text;
    if (params) {
      Object.keys(params).forEach(key => {
        finalText = finalText.replace(`{${key}}`, params[key]);
      });
    }
    
    const utterance = new SpeechSynthesisUtterance(finalText);
    const langConfig = LANGUAGES.find(l => l.code === language);
    utterance.lang = langConfig?.voice || 'en-IN';
    utterance.rate = 0.9;
    
    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    
    window.speechSynthesis.speak(utterance);
  };
  
  const stop = () => {
    window.speechSynthesis.cancel();
    setSpeaking(false);
  };
  
  return (
    <button
      onClick={speaking ? stop : speak}
      className={`p-2 rounded-lg transition-all ${
        speaking 
          ? 'bg-red-100 dark:bg-red-900/30 text-red-600 animate-pulse' 
          : 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 hover:bg-emerald-200'
      } ${className}`}
      title={speaking ? 'Stop' : 'Listen'}
    >
      {speaking ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
    </button>
  );
};

// Emergency SOS Button
const EmergencySOSButton = ({ onActivate, className = '' }) => {
  const [countdown, setCountdown] = useState(null);
  
  const handlePress = () => {
    if (countdown !== null) {
      setCountdown(null);
      return;
    }
    
    setCountdown(3);
  };
  
  useEffect(() => {
    if (countdown === null) return;
    
    if (countdown === 0) {
      onActivate?.();
      toast.success('Emergency alert sent to registered contacts!', { icon: '🚨' });
      setCountdown(null);
      return;
    }
    
    const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown, onActivate]);
  
  return (
    <button
      onClick={handlePress}
      className={`relative p-4 rounded-2xl transition-all ${
        countdown !== null
          ? 'bg-red-600 animate-pulse'
          : 'bg-gradient-to-br from-red-500 to-red-600 hover:from-red-600 hover:to-red-700'
      } text-white shadow-lg ${className}`}
    >
      <div className="flex items-center gap-3">
        <Phone className="w-6 h-6" />
        <div className="text-left">
          <p className="font-bold">
            {countdown !== null ? `Sending in ${countdown}...` : 'Emergency SOS'}
          </p>
          <p className="text-xs opacity-75">
            {countdown !== null ? 'Tap to cancel' : 'Hold for 3 seconds'}
          </p>
        </div>
      </div>
    </button>
  );
};

export { AccessibilityPanel, VoiceAlertButton, EmergencySOSButton, VOICE_MESSAGES, LANGUAGES };
export default AccessibilityPanel;
