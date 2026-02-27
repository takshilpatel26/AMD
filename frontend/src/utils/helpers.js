// Utility functions for Gram Meter

/**
 * Format a number as Indian Rupees
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
  }).format(amount);
};

/**
 * Format timestamp to readable date/time
 */
export const formatDateTime = (timestamp) => {
  const date = new Date(timestamp);
  return new Intl.DateTimeFormat('en-IN', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

/**
 * Calculate time ago from timestamp
 */
export const getTimeAgo = (timestamp) => {
  const now = new Date();
  const time = new Date(timestamp);
  const seconds = Math.floor((now - time) / 1000);

  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};

/**
 * Calculate efficiency grade based on score
 */
export const getEfficiencyGrade = (score) => {
  if (score >= 90) return 'A+';
  if (score >= 80) return 'A';
  if (score >= 70) return 'B';
  if (score >= 60) return 'C';
  if (score >= 50) return 'D';
  return 'F';
};

/**
 * Get color based on efficiency score
 */
export const getEfficiencyColor = (score) => {
  if (score >= 80) return 'emerald';
  if (score >= 60) return 'blue';
  if (score >= 40) return 'amber';
  return 'red';
};

/**
 * Format power consumption
 */
export const formatPower = (value, unit = 'kW') => {
  return `${Number(value).toFixed(2)} ${unit}`;
};

/**
 * Detect if user is online
 */
export const isOnline = () => {
  return navigator.onLine;
};

/**
 * Debounce function for performance optimization
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Throttle function for performance optimization
 */
export const throttle = (func, limit) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Deep clone object
 */
export const deepClone = (obj) => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Generate random ID
 */
export const generateId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Interpolate translation strings with values
 */
export const interpolate = (text, values = {}) => {
  return text.replace(/\{(\w+)\}/g, (match, key) => {
    return values[key] !== undefined ? values[key] : match;
  });
};

/**
 * Check if cache is fresh
 */
export const isCacheFresh = (timestamp, maxAge) => {
  if (!timestamp) return false;
  const now = Date.now();
  return now - timestamp < maxAge;
};

/**
 * Calculate forecast based on current usage
 */
export const calculateForecast = (currentUsage, ratePerUnit = 6.5) => {
  const hoursInDay = 24;
  const daysInMonth = 30;
  const estimatedDailyUsage = currentUsage * hoursInDay;
  const estimatedMonthlyUsage = estimatedDailyUsage * daysInMonth;
  const estimatedCost = estimatedMonthlyUsage * ratePerUnit;
  
  return {
    daily: estimatedDailyUsage,
    monthly: estimatedMonthlyUsage,
    cost: estimatedCost,
  };
};

/**
 * Detect anomalies in usage data
 */
export const detectAnomalies = (usageData, threshold = 2.5) => {
  if (!usageData || usageData.length === 0) return [];
  
  const values = usageData.map(d => d.usage);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const stdDev = Math.sqrt(
    values.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / values.length
  );
  
  const anomalies = [];
  usageData.forEach((item, index) => {
    if (Math.abs(item.usage - mean) > threshold * stdDev) {
      anomalies.push({
        index,
        time: item.time,
        usage: item.usage,
        deviation: Math.abs(item.usage - mean),
      });
    }
  });
  
  return anomalies;
};

/**
 * Simulate WhatsApp notification (for demo)
 */
export const simulateWhatsAppAlert = (message, phoneNumber = '+91 98765 43210') => {
  return {
    to: phoneNumber,
    message: message,
    timestamp: new Date().toISOString(),
    status: 'sent',
    channel: 'whatsapp',
  };
};

/**
 * Get alert icon and color based on severity
 */
export const getAlertStyle = (severity) => {
  const styles = {
    critical: {
      bg: 'bg-red-50',
      border: 'border-red-500',
      text: 'text-red-800',
      icon: 'text-red-500',
    },
    high: {
      bg: 'bg-orange-50',
      border: 'border-orange-500',
      text: 'text-orange-800',
      icon: 'text-orange-500',
    },
    medium: {
      bg: 'bg-amber-50',
      border: 'border-amber-500',
      text: 'text-amber-800',
      icon: 'text-amber-500',
    },
    low: {
      bg: 'bg-blue-50',
      border: 'border-blue-500',
      text: 'text-blue-800',
      icon: 'text-blue-500',
    },
  };
  
  return styles[severity] || styles.medium;
};
