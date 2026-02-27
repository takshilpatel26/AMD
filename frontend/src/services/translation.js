// Dynamic Translation Service using MyMemory API (Fast & Reliable)
// Supports all major Indian languages - No external packages required!

export const INDIAN_LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা' },
  { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ' },
  { code: 'as', name: 'Assamese', nativeName: 'অসমীয়া' },
  { code: 'ur', name: 'Urdu', nativeName: 'اردو' },
  { code: 'sa', name: 'Sanskrit', nativeName: 'संस्कृतम्' },
];

// Base English text that will be translated
export const BASE_TRANSLATIONS = {
  // Navbar & Header
  title: "Gram Meter",
  dashboard: "Dashboard",
  settings: "Settings",
  smartMeter: "Smart Meter",
  smartMeterDashboard: "Smart Meter Dashboard",
  selectLanguage: "Select Language",
  
  // KPI Cards
  liveUsage: "Live Usage",
  dailyCost: "Today's Cost",
  efficiency: "Efficiency Score",
  normal: "Normal Load",
  updated: "Updated",
  justNow: "Just now",
  excellent: "Excellent Consumption",
  voltage: "Voltage",
  currentPower: "Current Power",
  powerConsumption: "Power Consumption",
  
  // Chart
  chartTitle: "24-Hour Consumption Trend",
  usage: "Usage",
  time: "Time",
  
  // Alerts
  alerts: "Smart Alerts",
  voltageSpike: "Voltage Spike",
  spikeMessage: "Spike detected at {time}. Check your water pump.",
  peakHours: "Peak Hours",
  peakMessage: "Rates are high right now. Reduce load.",
  anomalyDetected: "Anomaly Detected",
  highUsage: "High Usage Alert",
  billForecast: "Bill Forecast",
  forecastMessage: "Estimated bill: ₹{amount} if current usage continues",
  highVoltageAlert: "High Voltage Alert",
  dangerHighVoltage: "Danger! Voltage is too high",
  
  // Actions
  simulateAlert: "Simulate WhatsApp Alert",
  viewDetails: "View Details",
  acknowledge: "Acknowledge",
  sending: "Sending...",
  listen: "Listen",
  listenVoltage: "Listen Voltage",
  listenBill: "Listen Bill",
  pumpStatus: "Pump Status",
  
  // Stats
  todayUsage: "Today's Usage",
  thisMonth: "This Month",
  thisWeek: "This Week",
  avgDaily: "Avg. Daily",
  thisMonthBill: "This Month's Bill",
  units: "Units",
  dueDate: "Due Date",
  pay: "Pay",
  payment: "Payment",
  
  // Status
  online: "Online",
  offline: "Offline Mode",
  syncing: "Syncing...",
  lastSync: "Last synced",
  
  // Notifications
  alertSent: "Alert sent successfully!",
  dataUpdated: "Data updated",
  offlineWarning: "You're offline. Showing cached data.",
  backOnline: "Back online!",
  noAlerts: "No alerts at the moment",
  
  // Bill Forecast
  projectedMonthly: "Projected Monthly",
  vsLastMonth: "Vs Last Month",
  
  // Pump Control
  pumpControl: "Pump Control",
  turnOn: "Turn ON",
  turnOff: "Turn OFF",
  pumpOn: "Pump is ON",
  pumpOff: "Pump is OFF",
  todayRuntime: "Today's Runtime",
  pumpTurnedOn: "Pump turned on",
  pumpTurnedOff: "Pump turned off",
  
  // Weather
  todayWeather: "Today's Weather",
  humidity: "Humidity",
  wind: "Wind",
  
  // Power Schedule
  powerSchedule: "Power Schedule",
  electricitySchedule: "Electricity Schedule",
  scheduled: "Scheduled",
  currentlyOn: "Currently ON",
  
  // Emergency
  emergency: "Emergency",
  emergencyContacts: "Emergency Contacts",
  tapToCall: "Tap to call",
  electricityBoard: "Electricity Board",
  gramPanchayat: "Gram Panchayat",
  fireEmergency: "Fire Emergency",
  
  // Appliances
  waterPump: "Water Pump",
  refrigerator: "Refrigerator",
  lights: "Lights",
  fan: "Fan",
  ac: "Air Conditioner",
  
  // Units
  kw: "kW",
  kwh: "kWh",
  rupee: "₹",
  volts: "V",
  hours: "hrs",
  
  // Voice Messages (for Text-to-Speech)
  voltageNormal: "Voltage is normal. Everything is fine.",
  voltageLow: "Warning! Voltage is low.",
  voltageHigh: "Danger! Voltage is too high.",
  billMessage: "This month's bill is {amount} rupees. {units} units of electricity used.",
  
  // Footer
  poweredBy: "Powered by SmartBijli Squad",
  version: "v1.0",
  
  // Language Selection
  languageChanged: "Language changed to",
  indianLanguages: "Indian Languages",
};

// Translation cache to avoid repeated API calls
const translationCache = {};

/**
 * Translate text using MyMemory Translation API (Fast, Free, No Package Required)
 * MyMemory is a collaborative translation database with excellent coverage
 */
async function translateText(text, targetLang) {
  if (targetLang === 'en') return text;
  
  const cacheKey = `${text}_${targetLang}`;
  if (translationCache[cacheKey]) {
    return translationCache[cacheKey];
  }

  try {
    // Use MyMemory API - free, reliable, no package needed
    const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=en|${targetLang}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      const translatedText = data.responseData.translatedText;
      translationCache[cacheKey] = translatedText;
      return translatedText;
    }
  } catch (error) {
    console.error('Translation error:', error);
  }

  // Return original text on error
  return text;
}

/**
 * Translate all base translations to target language
 * Uses parallel translation for speed
 */
export async function translateAllTexts(targetLang) {
  if (targetLang === 'en') {
    return BASE_TRANSLATIONS;
  }

  // Check if we have cached translations for this language
  const cacheKey = `all_translations_${targetLang}`;
  const cached = localStorage.getItem(cacheKey);
  
  if (cached) {
    try {
      return JSON.parse(cached);
    } catch (error) {
      console.warn('Invalid cache, re-translating:', error);
    }
  }

  // Translate all texts via API in parallel batches
  const translations = {};
  const entries = Object.entries(BASE_TRANSLATIONS);
  
  // Batch translations in groups of 5 to avoid overwhelming the API
  const batchSize = 5;
  for (let i = 0; i < entries.length; i += batchSize) {
    const batch = entries.slice(i, i + batchSize);
    const promises = batch.map(async ([key, value]) => {
      const translated = await translateText(value, targetLang);
      return [key, translated];
    });
    
    const results = await Promise.all(promises);
    results.forEach(([key, value]) => {
      translations[key] = value;
    });
  }

  // Cache the translations
  try {
    localStorage.setItem(cacheKey, JSON.stringify(translations));
  } catch (e) {
    console.warn('Could not cache translations:', e);
  }

  return translations;
}

/**
 * Detect user's preferred language from browser
 */
export function detectUserLanguage() {
  const browserLang = navigator.language.split('-')[0];
  const supportedLang = INDIAN_LANGUAGES.find(lang => lang.code === browserLang);
  return supportedLang ? browserLang : 'en';
}

/**
 * Clear translation cache (useful when switching languages frequently)
 */
export function clearTranslationCache() {
  Object.keys(localStorage).forEach(key => {
    if (key.startsWith('all_translations_')) {
      localStorage.removeItem(key);
    }
  });
  Object.keys(translationCache).forEach(key => {
    delete translationCache[key];
  });
}
