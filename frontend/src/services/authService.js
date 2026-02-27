// Authentication Service for Mobile OTP-based Authentication
import { API_CONFIG } from '../constants/config';
import storageService from './storage';

class AuthService {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
  }

  /**
   * Get authentication headers
   */
  getHeaders() {
    const token = storageService.getToken();
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  /**
   * Make authenticated API request
   */
  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...options.headers,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('Auth request error:', error);
      throw error;
    }
  }

  /**
   * Request signup OTP
   * POST /api/v1/auth/signup/request/
   * 
   * Backend expects: mobile_number, first_name, last_name, village, role
   */
  async signupRequest(mobile, firstName, lastName, village, role = 'farmer') {
    try {
      // Format mobile number with country code if not present
      const formattedMobile = mobile.startsWith('+') ? mobile : `+91${mobile}`;
      
      const response = await this.request('/auth/signup/request/', {
        method: 'POST',
        body: JSON.stringify({
          mobile_number: formattedMobile,
          first_name: firstName,
          last_name: lastName,
          village: village,
          role: role,
        }),
      });

      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to send OTP');
    }
  }

  /**
   * Verify signup OTP and create account
   * POST /api/v1/auth/signup/verify/
   * 
   * Backend expects: mobile_number, otp
   */
  async signupVerify(mobile, otp) {
    try {
      // Format mobile number with country code if not present
      const formattedMobile = mobile.startsWith('+') ? mobile : `+91${mobile}`;
      
      const response = await this.request('/auth/signup/verify/', {
        method: 'POST',
        body: JSON.stringify({
          mobile_number: formattedMobile,
          otp: otp,
        }),
      });

      // Store tokens - backend returns tokens.access and tokens.refresh
      if (response.tokens?.access) {
        storageService.setToken(response.tokens.access);
      }
      if (response.tokens?.refresh) {
        storageService.setRefreshToken(response.tokens.refresh);
      }
      // Also support flat response structure
      if (response.access) {
        storageService.setToken(response.access);
      }
      if (response.refresh) {
        storageService.setRefreshToken(response.refresh);
      }
      if (response.user) {
        // Transform user object to include name field for frontend
        const user = {
          ...response.user,
          name: `${response.user.first_name} ${response.user.last_name}`.trim(),
          mobile: response.user.mobile_number,
        };
        storageService.setUser(user);
      }

      return {
        ...response,
        user: response.user ? {
          ...response.user,
          name: `${response.user.first_name} ${response.user.last_name}`.trim(),
        } : null,
      };
    } catch (error) {
      throw new Error(error.message || 'Invalid OTP');
    }
  }

  /**
   * Request login OTP
   * POST /api/v1/auth/login/request/
   * 
   * Backend expects: mobile_number
   * Backend returns: user_id (needed for verify step)
   */
  async loginRequest(mobile) {
    try {
      // Format mobile number with country code if not present
      const formattedMobile = mobile.startsWith('+') ? mobile : `+91${mobile}`;
      
      const response = await this.request('/auth/login/request/', {
        method: 'POST',
        body: JSON.stringify({
          mobile_number: formattedMobile,
        }),
      });

      // Store user_id for the verify step
      if (response.user_id) {
        storageService.set('pending_login_user_id', response.user_id);
      }

      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to send OTP');
    }
  }

  /**
   * Verify login OTP
   * POST /api/v1/auth/login/verify/
   * 
   * Backend expects: user_id, otp (NOT mobile!)
   */
  async loginVerify(mobile, otp) {
    try {
      // Get the user_id stored from loginRequest
      const userId = storageService.get('pending_login_user_id');
      
      if (!userId) {
        throw new Error('Login session expired. Please request OTP again.');
      }
      
      const response = await this.request('/auth/login/verify/', {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          otp: otp,
        }),
      });

      // Clear pending login user_id
      storageService.remove('pending_login_user_id');

      // Store tokens - backend returns tokens.access and tokens.refresh
      if (response.tokens?.access) {
        storageService.setToken(response.tokens.access);
      }
      if (response.tokens?.refresh) {
        storageService.setRefreshToken(response.tokens.refresh);
      }
      // Also support flat response structure
      if (response.access) {
        storageService.setToken(response.access);
      }
      if (response.refresh) {
        storageService.setRefreshToken(response.refresh);
      }
      if (response.user) {
        // Transform user object to include name field for frontend
        const user = {
          ...response.user,
          name: `${response.user.first_name} ${response.user.last_name}`.trim(),
          mobile: response.user.mobile_number,
        };
        storageService.setUser(user);
      }

      return {
        ...response,
        user: response.user ? {
          ...response.user,
          name: `${response.user.first_name} ${response.user.last_name}`.trim(),
        } : null,
      };
    } catch (error) {
      throw new Error(error.message || 'Invalid OTP');
    }
  }

  /**
   * Resend OTP
   * POST /api/v1/auth/otp/resend/
   * 
   * Backend expects: mobile_number
   */
  async resendOTP(mobile) {
    try {
      // Format mobile number with country code if not present
      const formattedMobile = mobile.startsWith('+') ? mobile : `+91${mobile}`;
      
      const response = await this.request('/auth/otp/resend/', {
        method: 'POST',
        body: JSON.stringify({
          mobile_number: formattedMobile,
        }),
      });

      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to resend OTP');
    }
  }

  /**
   * Logout
   * POST /api/v1/auth/logout/
   */
  async logout() {
    try {
      await this.request('/auth/logout/', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage
      storageService.clearAuth();
    }
  }

  /**
   * Check authentication status
   * GET /api/v1/auth/status/
   */
  async checkAuthStatus() {
    try {
      const response = await this.request('/auth/status/');
      return response;
    } catch (error) {
      return { authenticated: false };
    }
  }

  /**
   * Refresh access token
   * POST /api/v1/auth/token/refresh/
   */
  async refreshToken() {
    try {
      const refreshToken = storageService.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh: refreshToken,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      // Store new access token
      if (data.access) {
        storageService.setToken(data.access);
      }

      return data;
    } catch (error) {
      // If refresh fails, clear auth
      storageService.clearAuth();
      throw error;
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!storageService.getToken();
  }

  /**
   * Get current user
   */
  getCurrentUser() {
    return storageService.getUser();
  }
}

export default new AuthService();
