/**
 * Offline Service - Handle offline data storage and synchronization
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-netinfo/netinfo';
import { Domain } from './DomainService';

interface OfflineData {
  domains: Domain[];
  lastSync: string;
  pendingOperations: PendingOperation[];
}

interface PendingOperation {
  id: string;
  type: 'create' | 'update' | 'delete';
  data: any;
  timestamp: string;
  retryCount: number;
}

class OfflineService {
  private isOnline = true;
  private syncInProgress = false;
  private readonly STORAGE_KEY = 'offline_data';
  private readonly MAX_RETRY_COUNT = 3;

  constructor() {
    this.initializeNetworkListener();
    this.loadOfflineData();
  }

  private initializeNetworkListener() {
    NetInfo.addEventListener(state => {
      const wasOffline = !this.isOnline;
      this.isOnline = state.isConnected ?? false;

      if (wasOffline && this.isOnline) {
        console.log('Network connection restored, syncing data...');
        this.syncPendingOperations();
      }
    });
  }

  private async loadOfflineData() {
    try {
      const data = await AsyncStorage.getItem(this.STORAGE_KEY);
      if (data) {
        const offlineData: OfflineData = JSON.parse(data);
        console.log('Offline data loaded:', offlineData);
      }
    } catch (error) {
      console.error('Failed to load offline data:', error);
    }
  }

  private async saveOfflineData(data: OfflineData) {
    try {
      await AsyncStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save offline data:', error);
    }
  }

  // Domain operations
  async saveDomains(domains: Domain[]) {
    try {
      const currentData = await this.getOfflineData();
      currentData.domains = domains;
      currentData.lastSync = new Date().toISOString();
      
      await this.saveOfflineData(currentData);
      console.log('Domains saved offline:', domains.length);
    } catch (error) {
      console.error('Failed to save domains offline:', error);
    }
  }

  async getDomains(): Promise<Domain[]> {
    try {
      const data = await this.getOfflineData();
      return data.domains || [];
    } catch (error) {
      console.error('Failed to get domains offline:', error);
      return [];
    }
  }

  async addDomainOffline(domain: Domain) {
    try {
      const data = await this.getOfflineData();
      
      // Add to local storage
      data.domains.push(domain);
      await this.saveOfflineData(data);

      // Add to pending operations if offline
      if (!this.isOnline) {
        await this.addPendingOperation({
          type: 'create',
          data: domain,
        });
      }

      console.log('Domain added offline:', domain.name);
    } catch (error) {
      console.error('Failed to add domain offline:', error);
    }
  }

  async updateDomainOffline(domainId: string, updates: Partial<Domain>) {
    try {
      const data = await this.getOfflineData();
      const domainIndex = data.domains.findIndex(d => d.id === domainId);
      
      if (domainIndex !== -1) {
        data.domains[domainIndex] = { ...data.domains[domainIndex], ...updates };
        await this.saveOfflineData(data);

        // Add to pending operations if offline
        if (!this.isOnline) {
          await this.addPendingOperation({
            type: 'update',
            data: { id: domainId, updates },
          });
        }

        console.log('Domain updated offline:', domainId);
      }
    } catch (error) {
      console.error('Failed to update domain offline:', error);
    }
  }

  async deleteDomainOffline(domainId: string) {
    try {
      const data = await this.getOfflineData();
      const domainIndex = data.domains.findIndex(d => d.id === domainId);
      
      if (domainIndex !== -1) {
        const deletedDomain = data.domains[domainIndex];
        data.domains.splice(domainIndex, 1);
        await this.saveOfflineData(data);

        // Add to pending operations if offline
        if (!this.isOnline) {
          await this.addPendingOperation({
            type: 'delete',
            data: { id: domainId, domain: deletedDomain },
          });
        }

        console.log('Domain deleted offline:', domainId);
      }
    } catch (error) {
      console.error('Failed to delete domain offline:', error);
    }
  }

  // Pending operations management
  private async addPendingOperation(operation: Omit<PendingOperation, 'id' | 'timestamp' | 'retryCount'>) {
    try {
      const data = await this.getOfflineData();
      
      const pendingOperation: PendingOperation = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        retryCount: 0,
        ...operation,
      };

      data.pendingOperations.push(pendingOperation);
      await this.saveOfflineData(data);

      console.log('Pending operation added:', pendingOperation.type);
    } catch (error) {
      console.error('Failed to add pending operation:', error);
    }
  }

  private async getPendingOperations(): Promise<PendingOperation[]> {
    try {
      const data = await this.getOfflineData();
      return data.pendingOperations || [];
    } catch (error) {
      console.error('Failed to get pending operations:', error);
      return [];
    }
  }

  private async removePendingOperation(operationId: string) {
    try {
      const data = await this.getOfflineData();
      data.pendingOperations = data.pendingOperations.filter(op => op.id !== operationId);
      await this.saveOfflineData(data);
    } catch (error) {
      console.error('Failed to remove pending operation:', error);
    }
  }

  private async updatePendingOperationRetryCount(operationId: string) {
    try {
      const data = await this.getOfflineData();
      const operation = data.pendingOperations.find(op => op.id === operationId);
      
      if (operation) {
        operation.retryCount += 1;
        await this.saveOfflineData(data);
      }
    } catch (error) {
      console.error('Failed to update pending operation retry count:', error);
    }
  }

  // Sync operations
  async syncPendingOperations() {
    if (this.syncInProgress || !this.isOnline) {
      return;
    }

    this.syncInProgress = true;
    console.log('Starting sync of pending operations...');

    try {
      const pendingOperations = await this.getPendingOperations();
      
      for (const operation of pendingOperations) {
        try {
          await this.executePendingOperation(operation);
          await this.removePendingOperation(operation.id);
          console.log('Pending operation synced:', operation.type);
        } catch (error) {
          console.error('Failed to sync pending operation:', operation.id, error);
          
          // Increment retry count
          await this.updatePendingOperationRetryCount(operation.id);
          
          // Remove if max retries reached
          const updatedOperation = (await this.getPendingOperations()).find(op => op.id === operation.id);
          if (updatedOperation && updatedOperation.retryCount >= this.MAX_RETRY_COUNT) {
            await this.removePendingOperation(operation.id);
            console.log('Pending operation removed after max retries:', operation.id);
          }
        }
      }

      console.log('Sync completed');
    } catch (error) {
      console.error('Failed to sync pending operations:', error);
    } finally {
      this.syncInProgress = false;
    }
  }

  private async executePendingOperation(operation: PendingOperation) {
    // This would integrate with your API service
    // For now, we'll just simulate the operations
    
    switch (operation.type) {
      case 'create':
        // await DomainService.addDomain(operation.data);
        console.log('Executing create operation:', operation.data);
        break;
      case 'update':
        // await DomainService.updateDomain(operation.data.id, operation.data.updates);
        console.log('Executing update operation:', operation.data);
        break;
      case 'delete':
        // await DomainService.deleteDomain(operation.data.id);
        console.log('Executing delete operation:', operation.data);
        break;
    }
  }

  // Utility methods
  private async getOfflineData(): Promise<OfflineData> {
    try {
      const data = await AsyncStorage.getItem(this.STORAGE_KEY);
      return data ? JSON.parse(data) : {
        domains: [],
        lastSync: '',
        pendingOperations: [],
      };
    } catch (error) {
      console.error('Failed to get offline data:', error);
      return {
        domains: [],
        lastSync: '',
        pendingOperations: [],
      };
    }
  }

  async isNetworkAvailable(): Promise<boolean> {
    const state = await NetInfo.fetch();
    return state.isConnected ?? false;
  }

  async getLastSyncTime(): Promise<string | null> {
    try {
      const data = await this.getOfflineData();
      return data.lastSync || null;
    } catch (error) {
      console.error('Failed to get last sync time:', error);
      return null;
    }
  }

  async getPendingOperationsCount(): Promise<number> {
    try {
      const operations = await this.getPendingOperations();
      return operations.length;
    } catch (error) {
      console.error('Failed to get pending operations count:', error);
      return 0;
    }
  }

  async clearOfflineData() {
    try {
      await AsyncStorage.removeItem(this.STORAGE_KEY);
      console.log('Offline data cleared');
    } catch (error) {
      console.error('Failed to clear offline data:', error);
    }
  }

  // Cache management
  async cacheSSLStatus(domainId: string, sslStatus: any) {
    try {
      const cacheKey = `ssl_status_${domainId}`;
      const cacheData = {
        status: sslStatus,
        timestamp: new Date().toISOString(),
        expiresAt: new Date(Date.now() + 5 * 60 * 1000).toISOString(), // 5 minutes
      };
      
      await AsyncStorage.setItem(cacheKey, JSON.stringify(cacheData));
      console.log('SSL status cached for domain:', domainId);
    } catch (error) {
      console.error('Failed to cache SSL status:', error);
    }
  }

  async getCachedSSLStatus(domainId: string): Promise<any | null> {
    try {
      const cacheKey = `ssl_status_${domainId}`;
      const cacheData = await AsyncStorage.getItem(cacheKey);
      
      if (cacheData) {
        const parsed = JSON.parse(cacheData);
        const now = new Date();
        const expiresAt = new Date(parsed.expiresAt);
        
        if (now < expiresAt) {
          return parsed.status;
        } else {
          // Cache expired, remove it
          await AsyncStorage.removeItem(cacheKey);
        }
      }
      
      return null;
    } catch (error) {
      console.error('Failed to get cached SSL status:', error);
      return null;
    }
  }

  // Background sync
  async performBackgroundSync() {
    if (!this.isOnline) {
      console.log('Skipping background sync - offline');
      return;
    }

    try {
      console.log('Performing background sync...');
      
      // Sync pending operations
      await this.syncPendingOperations();
      
      // Update last sync time
      const data = await this.getOfflineData();
      data.lastSync = new Date().toISOString();
      await this.saveOfflineData(data);
      
      console.log('Background sync completed');
    } catch (error) {
      console.error('Background sync failed:', error);
    }
  }
}

export const offlineService = new OfflineService();
