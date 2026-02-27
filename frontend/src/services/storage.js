// Local Storage service for offline-first functionality
import { CACHE_CONFIG } from '../constants/config';

class StorageService {
  /**
   * Get item from localStorage
   */
  get(key) {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return null;
    }
  }

  /**
   * Set item in localStorage
   */
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('Error writing to localStorage:', error);
      return false;
    }
  }

  /**
   * Remove item from localStorage
   */
  remove(key) {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('Error removing from localStorage:', error);
      return false;
    }
  }

  /**
   * Clear all items from localStorage
   */
  clear() {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.error('Error clearing localStorage:', error);
      return false;
    }
  }

  /**
   * Get cached meter data
   */
  getCachedMeterData() {
    return this.get(CACHE_CONFIG.METER_DATA_KEY);
  }

  /**
   * Cache meter data with timestamp
   */
  cacheMeterData(data) {
    const cacheEntry = {
      data,
      timestamp: Date.now(),
    };
    return this.set(CACHE_CONFIG.METER_DATA_KEY, cacheEntry);
  }

  /**
   * Get cached alerts
   */
  getCachedAlerts() {
    return this.get(CACHE_CONFIG.ALERTS_KEY);
  }

  /**
   * Cache alerts with timestamp
   */
  cacheAlerts(alerts) {
    const cacheEntry = {
      data: alerts,
      timestamp: Date.now(),
    };
    return this.set(CACHE_CONFIG.ALERTS_KEY, cacheEntry);
  }

  /**
   * Get last sync timestamp
   */
  getLastSyncTime() {
    return this.get(CACHE_CONFIG.LAST_SYNC_KEY);
  }

  /**
   * Update last sync timestamp
   */
  updateLastSyncTime() {
    return this.set(CACHE_CONFIG.LAST_SYNC_KEY, Date.now());
  }

  /**
   * Get user's language preference
   */
  getLanguage() {
    return this.get(CACHE_CONFIG.LANGUAGE_KEY) || 'en';
  }

  /**
   * Set user's language preference
   */
  setLanguage(lang) {
    return this.set(CACHE_CONFIG.LANGUAGE_KEY, lang);
  }

  /**
   * Check if cache is fresh
   */
  isCacheFresh(cacheKey, maxAge = CACHE_CONFIG.MAX_AGE) {
    const cache = this.get(cacheKey);
    if (!cache || !cache.timestamp) return false;
    
    const now = Date.now();
    return now - cache.timestamp < maxAge;
  }

  /**
   * Authentication Token Management
   */

  /**
   * Get access token
   */
  getToken() {
    return this.get('auth_token');
  }

  /**
   * Set access token
   */
  setToken(token) {
    return this.set('auth_token', token);
  }

  /**
   * Get refresh token
   */
  getRefreshToken() {
    return this.get('refresh_token');
  }

  /**
   * Set refresh token
   */
  setRefreshToken(token) {
    return this.set('refresh_token', token);
  }

  /**
   * Get user data
   */
  getUser() {
    return this.get('user_data');
  }

  /**
   * Set user data
   */
  setUser(user) {
    return this.set('user_data', user);
  }

  /**
   * Clear authentication data
   */
  clearAuth() {
    this.remove('auth_token');
    this.remove('refresh_token');
    this.remove('user_data');
  }
}

export default new StorageService();
