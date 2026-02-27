// Custom hooks for Gram Meter - Real API Integration
import { useState, useEffect, useCallback } from 'react';
import apiService from '../services/api';
import authService from '../services/authService';
import { POLLING_CONFIG } from '../constants/config';
import { isOnline } from '../utils/helpers';
import toast from 'react-hot-toast';

/**
 * Hook for authentication state management
 */
export const useAuth = () => {
  const [user, setUser] = useState(authService.getCurrentUser());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = async (mobile, otp) => {
    setLoading(true);
    setError(null);
    try {
      const result = await authService.loginVerify(mobile, otp);
      setUser(result.user);
      toast.success('Logged in successfully!');
      return result;
    } catch (err) {
      setError(err.message);
      toast.error(err.message || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (mobile, otp, name, role = 'farmer') => {
    setLoading(true);
    setError(null);
    try {
      const result = await authService.signupVerify(mobile, otp);
      setUser(result.user);
      toast.success('Account created successfully!');
      return result;
    } catch (err) {
      setError(err.message);
      toast.error(err.message || 'Signup failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await authService.logout();
      setUser(null);
      toast.success('Logged out successfully');
    } catch (err) {
      console.error('Logout error:', err);
      toast.error('Logout failed');
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    isAuthenticated: authService.isAuthenticated(),
    loading,
    error,
    login,
    signup,
    logout,
  };
};

/**
 * Hook for fetching dashboard data with real-time updates
 */
export const useDashboardData = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOffline, setIsOffline] = useState(!isOnline());

  const fetchData = useCallback(async () => {
    try {
      const dashboardData = await apiService.getDashboardStats();
      setData(dashboardData);
      setIsOffline(dashboardData.isOffline || false);
      setError(null);
      
      if (dashboardData.isOffline && !toast.isActive('offline-warning')) {
        toast.error('You\'re offline. Showing cached data.', {
          id: 'offline-warning',
          duration: 3000,
        });
      }
    } catch (err) {
      setError(err.message);
      console.error('Error in useDashboardData:', err);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Set up polling for real-time updates
    let interval;
    if (POLLING_CONFIG.ENABLE_POLLING) {
      interval = setInterval(fetchData, POLLING_CONFIG.METER_DATA_INTERVAL);
    }

    // Listen for online/offline events
    const handleOnline = () => {
      setIsOffline(false);
      fetchData();
      toast.success('Back online!', { duration: 2000 });
    };

    const handleOffline = () => {
      setIsOffline(true);
      toast.error('You\'re offline. Showing cached data.', { duration: 3000 });
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      if (interval) clearInterval(interval);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [fetchData]);

  return { data, loading, error, isOffline, refetch: fetchData };
};

/**
 * Hook for fetching specific meter data
 */
export const useMeterData = (meterId) => {
  const [data, setData] = useState(null);
  const [liveStatus, setLiveStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!meterId) return;
    
    try {
      const [meterData, status] = await Promise.all([
        apiService.getMeter(meterId),
        apiService.getMeterLiveStatus(meterId),
      ]);
      setData(meterData);
      setLiveStatus(status);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error in useMeterData:', err);
    } finally {
      setLoading(false);
    }
  }, [meterId]);

  useEffect(() => {
    fetchData();

    // Poll for live updates
    const interval = setInterval(fetchData, POLLING_CONFIG.METER_DATA_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchData]);

  return { data, liveStatus, loading, error, refetch: fetchData };
};


/**
 * Hook for fetching alerts with acknowledge/resolve actions
 */
export const useAlerts = (params = {}) => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAlerts = useCallback(async () => {
    try {
      const alertsData = await apiService.getAlerts(params);
      setAlerts(alertsData);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error in useAlerts:', err);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => {
    fetchAlerts();

    // Poll for new alerts
    const interval = setInterval(fetchAlerts, POLLING_CONFIG.ALERTS_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchAlerts]);

  const acknowledgeAlert = async (alertId) => {
    try {
      await apiService.acknowledgeAlert(alertId);
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId ? { ...alert, acknowledged: true, acknowledged_at: new Date().toISOString() } : alert
      ));
      toast.success('Alert acknowledged', { duration: 2000 });
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
      toast.error('Failed to acknowledge alert', { duration: 2000 });
      throw error;
    }
  };

  const resolveAlert = async (alertId) => {
    try {
      await apiService.resolveAlert(alertId);
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId ? { ...alert, resolved: true, resolved_at: new Date().toISOString() } : alert
      ));
      toast.success('Alert resolved', { duration: 2000 });
    } catch (error) {
      console.error('Failed to resolve alert:', error);
      toast.error('Failed to resolve alert', { duration: 2000 });
      throw error;
    }
  };

  return { alerts, loading, error, refetch: fetchAlerts, acknowledgeAlert, resolveAlert };
};

/**
 * Hook for fetching analytics data
 */
export const useAnalytics = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getConsumptionTrends = async (params) => {
    setLoading(true);
    try {
      const data = await apiService.getConsumptionTrends(params);
      return data;
    } catch (err) {
      setError(err.message);
      toast.error('Failed to load consumption trends');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getEfficiencyAnalysis = async (params) => {
    setLoading(true);
    try {
      const data = await apiService.getEfficiencyAnalysis(params);
      return data;
    } catch (err) {
      setError(err.message);
      toast.error('Failed to load efficiency analysis');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getCostProjection = async (params) => {
    setLoading(true);
    try {
      const data = await apiService.getCostProjection(params);
      return data;
    } catch (err) {
      setError(err.message);
      toast.error('Failed to load cost projection');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getCarbonFootprint = async (params) => {
    setLoading(true);
    try {
      const data = await apiService.getCarbonFootprint(params);
      return data;
    } catch (err) {
      setError(err.message);
      toast.error('Failed to load carbon footprint');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const predictConsumption = async (meterData) => {
    setLoading(true);
    try {
      const data = await apiService.predictConsumption(meterData);
      return data;
    } catch (err) {
      setError(err.message);
      toast.error('Failed to predict consumption');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    getConsumptionTrends,
    getEfficiencyAnalysis,
    getCostProjection,
    getCarbonFootprint,
    predictConsumption,
  };
};

/**
 * Hook for simulating WhatsApp alerts
 */
export const useSimulateAlert = () => {
  const [sending, setSending] = useState(false);

  const simulateAlert = async (alertData) => {
    setSending(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const result = {
        to: '+91 98765 43210',
        message: alertData.message || 'Alert: Voltage Spike detected on Phase 1.',
        timestamp: new Date().toISOString(),
        status: 'sent',
        channel: 'whatsapp',
      };
      
      toast.success(
        `WhatsApp alert sent successfully!\n\nTo: ${result.to}\nMessage: ${result.message}`,
        { duration: 5000 }
      );
      
      return result;
    } catch (err) {
      toast.error('Failed to send WhatsApp alert', { duration: 3000 });
      throw err;
    } finally {
      setSending(false);
    }
  };

  return { simulateAlert, sending };
};

/**
 * Hook for managing real-time power updates
 */
export const useLivePower = (initialPower = 1.8) => {
  const [power, setPower] = useState(initialPower);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate fluctuating power usage
      setPower(prev => {
        const variation = (Math.random() - 0.5) * 0.4;
        const newPower = prev + variation;
        return Math.max(1.0, Math.min(3.5, newPower));
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return power;
};

/**
 * Hook for detecting network status
 */
export const useNetworkStatus = () => {
  const [online, setOnline] = useState(isOnline());

  useEffect(() => {
    const handleOnline = () => setOnline(true);
    const handleOffline = () => setOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return online;
};

/**
 * Hook for lazy loading components
 */
export const useIntersectionObserver = (ref, options = {}) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const observerRef = useRef(null);

  useEffect(() => {
    if (!ref.current) return;

    observerRef.current = new IntersectionObserver(([entry]) => {
      setIsIntersecting(entry.isIntersecting);
    }, options);

    observerRef.current.observe(ref.current);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [ref, options]);

  return isIntersecting;
};
