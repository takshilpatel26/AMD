// API Service - Complete Integration with Django REST Framework Backend
import { API_CONFIG } from '../constants/config';
import storageService from './storage';
import authService from './authService';

class ApiService {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
  }

  getHeaders() {
    const token = storageService.getToken();
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  async request(endpoint, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          ...this.getHeaders(),
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (response.status === 401) {
        try {
          await authService.refreshToken();
          return await this.request(endpoint, options);
        } catch (error) {
          authService.logout();
          throw new Error('Session expired. Please login again.');
        }
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      
      throw error;
    }
  }

  async requestWithRetry(endpoint, options = {}, retries = API_CONFIG.RETRY_ATTEMPTS) {
    try {
      return await this.request(endpoint, options);
    } catch (error) {
      if (retries > 0 && !error.message.includes('Session expired')) {
        await new Promise(resolve => setTimeout(resolve, API_CONFIG.RETRY_DELAY));
        return this.requestWithRetry(endpoint, options, retries - 1);
      }
      throw error;
    }
  }

  async getDashboardStats() {
    try {
      const data = await this.requestWithRetry('/dashboard/stats/');
      storageService.cacheMeterData(data);
      storageService.updateLastSyncTime();
      return data;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      const cached = storageService.getCachedMeterData();
      if (cached) {
        return { ...cached.data, isOffline: true };
      }
      throw error;
    }
  }

  async getMeters() {
    const response = await this.requestWithRetry('/meters/');
    // Handle DRF paginated response or direct array
    return Array.isArray(response) ? response : (response.results || []);
  }

  async getMeter(meterId) {
    return await this.requestWithRetry(`/meters/${meterId}/`);
  }

  async getMeterLiveStatus(meterId) {
    return await this.requestWithRetry(`/meters/${meterId}/live_status/`);
  }

  async getMeterStats() {
    return await this.requestWithRetry('/meters/stats/');
  }

  async getMeterReadings(meterId, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = `/meters/${meterId}/readings/${queryString ? `?${queryString}` : ''}`;
    return await this.requestWithRetry(endpoint);
  }

  async getReadings(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = `/readings/${queryString ? `?${queryString}` : ''}`;
    const response = await this.requestWithRetry(endpoint);
    // Handle DRF paginated response or direct array
    return Array.isArray(response) ? response : (response.results || []);
  }

  async getAnomalies(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/readings/anomalies/${queryString ? `?${queryString}` : ''}`;
      return await this.requestWithRetry(endpoint);
    } catch (error) {
      console.error('Error fetching anomalies:', error);
      return [];
    }
  }

  async getAlerts(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/alerts/${queryString ? `?${queryString}` : ''}`;
      const response = await this.requestWithRetry(endpoint);
      
      // Handle DRF paginated response or direct array
      const alerts = Array.isArray(response) ? response : (response.results || []);
      storageService.cacheAlerts(alerts);
      return alerts;
    } catch (error) {
      console.error('Error fetching alerts:', error);
      const cached = storageService.getCachedAlerts();
      return cached ? cached.data : [];
    }
  }

  async acknowledgeAlert(alertId) {
    return await this.requestWithRetry(`/alerts/${alertId}/acknowledge/`, {
      method: 'POST',
    });
  }

  async resolveAlert(alertId) {
    return await this.requestWithRetry(`/alerts/${alertId}/resolve/`, {
      method: 'POST',
    });
  }

  async bulkAcknowledgeAlerts(alertIds) {
    // Backend expects: alert_ids (array of IDs)
    return await this.requestWithRetry('/alerts/bulk_acknowledge/', {
      method: 'POST',
      body: JSON.stringify({
        alert_ids: alertIds,
      }),
    });
  }

  async getAlertStats() {
    return await this.requestWithRetry('/alerts/stats/');
  }

  async getConsumptionTrends(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/analytics/consumption/${queryString ? `?${queryString}` : ''}`;
      return await this.requestWithRetry(endpoint);
    } catch (error) {
      console.error('Error:', error);
      return null;
    }
  }

  async getEfficiencyAnalysis(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/analytics/efficiency/${queryString ? `?${queryString}` : ''}`;
      return await this.requestWithRetry(endpoint);
    } catch (error) {
      console.error('Error:', error);
      return null;
    }
  }

  async getCostProjection(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/analytics/trends/${queryString ? `?${queryString}` : ''}`;
      return await this.requestWithRetry(endpoint);
    } catch (error) {
      console.error('Error:', error);
      return null;
    }
  }

  async getCarbonFootprint(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/analytics/carbon_footprint/${queryString ? `?${queryString}` : ''}`;
      return await this.requestWithRetry(endpoint);
    } catch (error) {
      console.error('Error:', error);
      return null;
    }
  }

  async detectAnomaly(readingData) {
    // Backend expects: voltage, current, power, energy, power_factor, frequency, meter_id
    return await this.requestWithRetry('/analytics/ml/detect_anomaly/', {
      method: 'POST',
      body: JSON.stringify({
        voltage: readingData.voltage || 230,
        current: readingData.current || 0,
        power: readingData.power || 0,
        energy: readingData.energy || 0,
        power_factor: readingData.power_factor || 0.95,
        frequency: readingData.frequency || 50.0,
        meter_id: readingData.meter_id,
      }),
    });
  }

  async predictConsumption(meterData) {
    // Backend expects: current_day, consumed_so_far, avg_pump_usage, avg_voltage
    return await this.requestWithRetry('/analytics/predict_consumption/', {
      method: 'POST',
      body: JSON.stringify({
        current_day: meterData.current_day || new Date().getDate(),
        consumed_so_far: meterData.consumed_so_far || 0,
        avg_pump_usage: meterData.avg_pump_usage || 0,
        avg_voltage: meterData.avg_voltage || 230,
      }),
    });
  }

  async forecastHourly(meterData) {
    // Backend expects: meter_id, historical_readings (array)
    return await this.requestWithRetry('/analytics/forecast_hourly/', {
      method: 'POST',
      body: JSON.stringify({
        meter_id: meterData.meter_id,
        historical_readings: meterData.historical_readings || [],
      }),
    });
  }

  async weeklyForecast(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/analytics/weekly_forecast/${queryString ? `?${queryString}` : ''}`;
      return await this.requestWithRetry(endpoint);
    } catch (error) {
      console.error('Error:', error);
      return null;
    }
  }

  async patternAnalysis(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/analytics/pattern_analysis/${queryString ? `?${queryString}` : ''}`;
      return await this.requestWithRetry(endpoint);
    } catch (error) {
      console.error('Error:', error);
      return null;
    }
  }

  async getBillingSummary(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/billing/summary/${queryString ? `?${queryString}` : ''}`;
      return await this.requestWithRetry(endpoint);
    } catch (error) {
      console.error('Error:', error);
      return null;
    }
  }

  async getInvoices(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/billing/invoices/${queryString ? `?${queryString}` : ''}`;
      const response = await this.requestWithRetry(endpoint);
      // Handle DRF paginated response: { invoices: [...] } or direct array
      return response.invoices || (Array.isArray(response) ? response : (response.results || []));
    } catch (error) {
      console.error('Error:', error);
      return [];
    }
  }

  async getBills(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/billing/bills/${queryString ? `?${queryString}` : ''}`;
      const response = await this.requestWithRetry(endpoint);
      // Handle DRF paginated response: { bills: [...] } or direct array
      return response.bills || (Array.isArray(response) ? response : (response.results || []));
    } catch (error) {
      console.error('Error:', error);
      return [];
    }
  }

  async generateBill(meterId) {
    // Backend expects: meter_id in body
    return await this.requestWithRetry('/billing/generate_bill/', {
      method: 'POST',
      body: JSON.stringify({
        meter_id: meterId,
      }),
    });
  }

  async getBillDetail(billId) {
    return await this.requestWithRetry(`/billing/bills/${billId}/`);
  }

  async getInvoiceDetail(invoiceId) {
    return await this.requestWithRetry(`/billing/invoices/${invoiceId}/`);
  }

  async getNotifications(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = `/notifications/${queryString ? `?${queryString}` : ''}`;
      const response = await this.requestWithRetry(endpoint);
      // Handle DRF paginated response or direct array
      return Array.isArray(response) ? response : (response.results || []);
    } catch (error) {
      console.error('Error:', error);
      return [];
    }
  }

  async getUnreadNotificationCount() {
    try {
      return await this.requestWithRetry('/notifications/unread_count/');
    } catch (error) {
      console.error('Error:', error);
      return { unread_count: 0 };
    }
  }

  async markNotificationRead(notificationId) {
    return await this.requestWithRetry(`/notifications/${notificationId}/mark_read/`, {
      method: 'POST',
    });
  }

  async markAllNotificationsRead() {
    return await this.requestWithRetry('/notifications/mark_all_read/', {
      method: 'POST',
    });
  }

  async sendAlertNotification(alertId, channel = 'whatsapp') {
    // Backend expects: alert_id, channel
    return await this.requestWithRetry('/notifications/send_alert_notification/', {
      method: 'POST',
      body: JSON.stringify({
        alert_id: alertId,
        channel: channel,
      }),
    });
  }

  async sendTestWhatsApp(data) {
    // Backend expects: phone, message
    return await this.requestWithRetry('/notifications/send_test_whatsapp/', {
      method: 'POST',
      body: JSON.stringify({
        phone: data.phone,
        message: data.message || 'Test message from Gram Meter! 🌾',
      }),
    });
  }

  async sendTestSMS(data) {
    // Backend expects: phone, message
    return await this.requestWithRetry('/notifications/send_test_sms/', {
      method: 'POST',
      body: JSON.stringify({
        phone: data.phone,
        message: data.message || 'Test SMS from Gram Meter!',
      }),
    });
  }

  async getCurrentUser() {
    return await this.requestWithRetry('/users/me/');
  }

  async updateProfile(userData) {
    return await this.requestWithRetry('/users/update_profile/', {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }
}

export default new ApiService();
