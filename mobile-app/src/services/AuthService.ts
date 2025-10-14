/**
 * Authentication Service
 */

import axios from 'axios';
import * as Keychain from 'react-native-keychain';
import { User } from '../store/slices/authSlice';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000' 
  : 'https://ssl-monitor-api.onrender.com';

class AuthService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
  });

  constructor() {
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      async (config) => {
        const credentials = await Keychain.getInternetCredentials('ssl_monitor_token');
        if (credentials && credentials.password) {
          config.headers.Authorization = `Bearer ${credentials.password}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          try {
            const newToken = await this.refreshToken();
            if (newToken) {
              // Retry original request with new token
              error.config.headers.Authorization = `Bearer ${newToken}`;
              return this.api.request(error.config);
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            await this.logout();
          }
        }
        return Promise.reject(error);
      }
    );
  }

  async login(credentials: { email: string; password: string }) {
    try {
      const response = await this.api.post('/auth/login', credentials);
      const { user, token } = response.data;

      // Store token securely
      await Keychain.setInternetCredentials(
        'ssl_monitor_token',
        user.email,
        token
      );

      // Store user data
      await Keychain.setInternetCredentials(
        'ssl_monitor_user',
        user.email,
        JSON.stringify(user)
      );

      return { user, token };
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  async register(userData: { email: string; password: string; name?: string }) {
    try {
      const response = await this.api.post('/auth/register', userData);
      const { user, token } = response.data;

      // Store token securely
      await Keychain.setInternetCredentials(
        'ssl_monitor_token',
        user.email,
        token
      );

      // Store user data
      await Keychain.setInternetCredentials(
        'ssl_monitor_user',
        user.email,
        JSON.stringify(user)
      );

      return { user, token };
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  async logout() {
    try {
      // Clear stored credentials
      await Keychain.resetInternetCredentials('ssl_monitor_token');
      await Keychain.resetInternetCredentials('ssl_monitor_user');
      
      // Call logout endpoint if needed
      await this.api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  async refreshToken() {
    try {
      const response = await this.api.post('/auth/refresh');
      const { token } = response.data;

      // Update stored token
      const credentials = await Keychain.getInternetCredentials('ssl_monitor_token');
      if (credentials) {
        await Keychain.setInternetCredentials(
          'ssl_monitor_token',
          credentials.username,
          token
        );
      }

      return token;
    } catch (error) {
      throw new Error('Token refresh failed');
    }
  }

  async updateProfile(userData: Partial<User>) {
    try {
      const response = await this.api.patch('/auth/profile', userData);
      const user = response.data;

      // Update stored user data
      await Keychain.setInternetCredentials(
        'ssl_monitor_user',
        user.email,
        JSON.stringify(user)
      );

      return user;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Profile update failed');
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const credentials = await Keychain.getInternetCredentials('ssl_monitor_user');
      if (credentials && credentials.password) {
        return JSON.parse(credentials.password);
      }
      return null;
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  }

  async getStoredToken(): Promise<string | null> {
    try {
      const credentials = await Keychain.getInternetCredentials('ssl_monitor_token');
      return credentials?.password || null;
    } catch (error) {
      console.error('Error getting stored token:', error);
      return null;
    }
  }

  async isAuthenticated(): Promise<boolean> {
    try {
      const token = await this.getStoredToken();
      const user = await this.getCurrentUser();
      return !!(token && user);
    } catch (error) {
      return false;
    }
  }

  async changePassword(currentPassword: string, newPassword: string) {
    try {
      await this.api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Password change failed');
    }
  }

  async forgotPassword(email: string) {
    try {
      await this.api.post('/auth/forgot-password', { email });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Password reset failed');
    }
  }

  async resetPassword(token: string, newPassword: string) {
    try {
      await this.api.post('/auth/reset-password', {
        token,
        new_password: newPassword,
      });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Password reset failed');
    }
  }
}

export const AuthService = new AuthService();
