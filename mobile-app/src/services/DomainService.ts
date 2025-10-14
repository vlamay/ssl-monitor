/**
 * Domain Management Service
 */

import axios from 'axios';
import * as Keychain from 'react-native-keychain';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000' 
  : 'https://ssl-monitor-api.onrender.com';

export interface Domain {
  id: number;
  name: string;
  is_active: boolean;
  alert_threshold_days: number;
  created_at: string;
  updated_at: string;
  ssl_status?: SSLStatus;
}

export interface SSLStatus {
  is_valid: boolean;
  expires_in: number;
  issuer?: string;
  subject?: string;
  not_valid_after?: string;
  checked_at?: string;
}

export interface DomainStatistics {
  total_domains: number;
  active_domains: number;
  domains_with_errors: number;
  domains_expiring_soon: number;
  domains_expired: number;
}

class DomainService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 15000,
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
  }

  async getDomains(): Promise<Domain[]> {
    try {
      const response = await this.api.get('/domains');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch domains');
    }
  }

  async getDomain(id: number): Promise<Domain> {
    try {
      const response = await this.api.get(`/domains/${id}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch domain');
    }
  }

  async addDomain(domainData: { 
    name: string; 
    alert_threshold_days?: number;
  }): Promise<Domain> {
    try {
      const response = await this.api.post('/domains', {
        name: domainData.name,
        alert_threshold_days: domainData.alert_threshold_days || 30,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to add domain');
    }
  }

  async updateDomain(id: number, domainData: Partial<Domain>): Promise<Domain> {
    try {
      const response = await this.api.patch(`/domains/${id}`, domainData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to update domain');
    }
  }

  async deleteDomain(id: number): Promise<void> {
    try {
      await this.api.delete(`/domains/${id}`);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to delete domain');
    }
  }

  async checkSSLStatus(id: number): Promise<SSLStatus> {
    try {
      const response = await this.api.post(`/domains/${id}/check-ssl`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to check SSL status');
    }
  }

  async refreshDomainStatus(id: number): Promise<SSLStatus> {
    try {
      const response = await this.api.post(`/domains/${id}/refresh`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to refresh domain status');
    }
  }

  async getStatistics(): Promise<DomainStatistics> {
    try {
      const response = await this.api.get('/statistics');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch statistics');
    }
  }

  async getAnalytics(period: string = '7d') {
    try {
      const response = await this.api.get(`/analytics/dashboard?period=${period}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch analytics');
    }
  }

  async getSSLTrends(period: string = '30d') {
    try {
      const response = await this.api.get(`/analytics/ssl-trends?period=${period}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch SSL trends');
    }
  }

  async exportDomains(format: 'csv' | 'json' = 'json') {
    try {
      const response = await this.api.get(`/domains/export?format=${format}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to export domains');
    }
  }

  async bulkCheckSSL(domainIds: number[]): Promise<SSLStatus[]> {
    try {
      const response = await this.api.post('/domains/bulk-check-ssl', {
        domain_ids: domainIds,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to bulk check SSL');
    }
  }

  async validateDomain(domain: string): Promise<{ valid: boolean; message?: string }> {
    try {
      const response = await this.api.post('/domains/validate', { domain });
      return response.data;
    } catch (error: any) {
      return {
        valid: false,
        message: error.response?.data?.detail || 'Invalid domain format',
      };
    }
  }

  async getDomainHistory(id: number, limit: number = 30) {
    try {
      const response = await this.api.get(`/domains/${id}/history?limit=${limit}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch domain history');
    }
  }

  async setDomainPreferences(id: number, preferences: {
    alert_threshold_days?: number;
    notification_enabled?: boolean;
    priority?: 'low' | 'normal' | 'high' | 'critical';
  }) {
    try {
      const response = await this.api.patch(`/domains/${id}/preferences`, preferences);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to update domain preferences');
    }
  }
}

export const DomainService = new DomainService();
