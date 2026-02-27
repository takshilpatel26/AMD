// Distribution API Service - For Company Admin Dashboard
import { API_CONFIG } from '../constants/config';
import storageService from './storage';
import authService from './authService';

class DistributionApiService {
  constructor() {
    this.baseURL = `${API_CONFIG.BASE_URL}/distribution`;
  }

  getHeaders() {
    const token = storageService.getToken();
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...options.headers,
        },
      });

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
      throw error;
    }
  }

  // ============ Dashboard ============
  async getDashboard(companyId = null) {
    const params = companyId ? `?company=${companyId}` : '';
    return await this.request(`/dashboard/${params}`);
  }

  // ============ Companies ============
  async getCompanies() {
    return await this.request('/companies/');
  }

  async getCompany(companyId) {
    return await this.request(`/companies/${companyId}/`);
  }

  async getCompanyStats(companyId) {
    return await this.request(`/companies/${companyId}/dashboard_stats/`);
  }

  // ============ Districts ============
  async getDistricts(companyId = null) {
    const params = companyId ? `?company=${companyId}` : '';
    return await this.request(`/districts/${params}`);
  }

  async getDistrict(districtId) {
    return await this.request(`/districts/${districtId}/`);
  }

  async getDistrictVillages(districtId) {
    return await this.request(`/districts/${districtId}/villages/`);
  }

  async getDistrictAlerts(districtId) {
    return await this.request(`/districts/${districtId}/alerts/`);
  }

  async getDistrictStats(districtId) {
    return await this.request(`/districts/${districtId}/stats/`);
  }

  // ============ Villages ============
  async getVillages(districtId = null) {
    const params = districtId ? `?district=${districtId}` : '';
    return await this.request(`/villages/${params}`);
  }

  async getVillage(villageId) {
    return await this.request(`/villages/${villageId}/`);
  }

  async getVillageTransformers(villageId) {
    return await this.request(`/villages/${villageId}/transformers/`);
  }

  async getVillageAlerts(villageId) {
    return await this.request(`/villages/${villageId}/alerts/`);
  }

  async getVillageStats(villageId) {
    return await this.request(`/villages/${villageId}/stats/`);
  }

  // ============ Transformers ============
  async getTransformers(villageId = null) {
    const params = villageId ? `?village=${villageId}` : '';
    return await this.request(`/transformers/${params}`);
  }

  async getTransformer(transformerId) {
    return await this.request(`/transformers/${transformerId}/`);
  }

  async getTransformerHouses(transformerId) {
    return await this.request(`/transformers/${transformerId}/houses/`);
  }

  async getTransformerReadings(transformerId, hours = 24) {
    return await this.request(`/transformers/${transformerId}/readings/?hours=${hours}`);
  }

  async getTransformerAlerts(transformerId) {
    return await this.request(`/transformers/${transformerId}/alerts/`);
  }

  async getTransformerStats(transformerId) {
    return await this.request(`/transformers/${transformerId}/stats/`);
  }

  // ============ Houses ============
  async getHouses(transformerId = null) {
    const params = transformerId ? `?transformer=${transformerId}` : '';
    return await this.request(`/houses/${params}`);
  }

  async getHouse(houseId) {
    return await this.request(`/houses/${houseId}/`);
  }

  async getHouseReadings(houseId, hours = 24) {
    return await this.request(`/houses/${houseId}/readings/?hours=${hours}`);
  }

  async getHouseAlerts(houseId) {
    return await this.request(`/houses/${houseId}/alerts/`);
  }

  // ============ Readings ============
  async getReadings(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await this.request(`/readings/${queryString ? `?${queryString}` : ''}`);
  }

  async getAnomalousReadings() {
    return await this.request('/readings/?anomalies_only=true');
  }

  // ============ Alerts ============
  async getAlerts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await this.request(`/alerts/${queryString ? `?${queryString}` : ''}`);
  }

  async getAlert(alertId) {
    return await this.request(`/alerts/${alertId}/`);
  }

  async acknowledgeAlert(alertId) {
    return await this.request(`/alerts/${alertId}/acknowledge/`, {
      method: 'POST',
    });
  }

  async resolveAlert(alertId, notes = '') {
    return await this.request(`/alerts/${alertId}/resolve/`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  async getAlertStats(districtId = null) {
    const params = districtId ? `?district=${districtId}` : '';
    return await this.request(`/alerts/stats/${params}`);
  }

  // ============ Simulator ============
  async runSimulator(params = {}) {
    return await this.request('/simulator/run/', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }
}

export const distributionApi = new DistributionApiService();
export default distributionApi;
