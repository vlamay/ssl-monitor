/**
 * App Service - Application initialization and setup
 */

import { store } from '../store';
import { AuthService } from './AuthService';
import { setCredentials, clearCredentials } from '../store/slices/authSlice';
import { initializeSettings } from '../store/slices/settingsSlice';
import { setSystemTheme } from '../store/slices/themeSlice';
import PushNotification from 'react-native-push-notification';
import DeviceInfo from 'react-native-device-info';
import NetInfo from '@react-native-netinfo/netinfo';

class AppService {
  private isInitialized = false;

  async initialize() {
    if (this.isInitialized) return;

    try {
      // Initialize device info
      await this.initializeDeviceInfo();
      
      // Initialize authentication
      await this.initializeAuthentication();
      
      // Initialize settings
      await this.initializeSettings();
      
      // Initialize theme
      await this.initializeTheme();
      
      // Initialize push notifications
      this.initializePushNotifications();
      
      // Initialize network monitoring
      this.initializeNetworkMonitoring();

      this.isInitialized = true;
      console.log('App service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize app service:', error);
    }
  }

  private async initializeDeviceInfo() {
    try {
      const deviceInfo = {
        deviceId: await DeviceInfo.getUniqueId(),
        deviceName: await DeviceInfo.getDeviceName(),
        systemName: await DeviceInfo.getSystemName(),
        systemVersion: await DeviceInfo.getSystemVersion(),
        appVersion: await DeviceInfo.getVersion(),
        buildNumber: await DeviceInfo.getBuildNumber(),
        bundleId: await DeviceInfo.getBundleId(),
      };
      
      console.log('Device Info:', deviceInfo);
    } catch (error) {
      console.error('Failed to get device info:', error);
    }
  }

  private async initializeAuthentication() {
    try {
      const isAuthenticated = await AuthService.isAuthenticated();
      
      if (isAuthenticated) {
        const user = await AuthService.getCurrentUser();
        const token = await AuthService.getStoredToken();
        
        if (user && token) {
          store.dispatch(setCredentials({ user, token }));
        }
      } else {
        store.dispatch(clearCredentials());
      }
    } catch (error) {
      console.error('Failed to initialize authentication:', error);
      store.dispatch(clearCredentials());
    }
  }

  private async initializeSettings() {
    try {
      // Load default settings or from storage
      const defaultSettings = {
        language: 'en',
        timezone: 'UTC',
        theme: 'light' as const,
        auto_refresh: true,
        refresh_interval: 30,
        notifications: {
          push: true,
          email: true,
          telegram: false,
          slack: false,
          quiet_hours_enabled: true,
          quiet_hours_start: '22:00',
          quiet_hours_end: '08:00',
        },
        biometric_auth: false,
        analytics_enabled: true,
      };

      store.dispatch(initializeSettings(defaultSettings));
    } catch (error) {
      console.error('Failed to initialize settings:', error);
    }
  }

  private async initializeTheme() {
    try {
      // Detect system theme preference
      const isDarkMode = await DeviceInfo.isEmulator()
        ? false // Default to light for emulator
        : false; // TODO: Implement system theme detection

      store.dispatch(setSystemTheme(isDarkMode ? 'dark' : 'light'));
    } catch (error) {
      console.error('Failed to initialize theme:', error);
      store.dispatch(setSystemTheme('light'));
    }
  }

  private initializePushNotifications() {
    try {
      PushNotification.configure({
        onRegister: (token) => {
          console.log('Push notification token:', token);
          // TODO: Send token to server
        },
        onNotification: (notification) => {
          console.log('Push notification received:', notification);
          
          if (notification.userInteraction) {
            // Handle notification tap
            this.handleNotificationTap(notification);
          }
        },
        onAction: (notification) => {
          console.log('Push notification action:', notification);
        },
        onRegistrationError: (error) => {
          console.error('Push notification registration error:', error);
        },
        permissions: {
          alert: true,
          badge: true,
          sound: true,
        },
        popInitialNotification: true,
        requestPermissions: true,
      });

      // Create notification channel for Android
      PushNotification.createChannel(
        {
          channelId: 'ssl-monitor-pro',
          channelName: 'SSL Monitor Pro',
          channelDescription: 'SSL certificate monitoring notifications',
          playSound: true,
          soundName: 'default',
          importance: 4,
          vibrate: true,
        },
        (created) => console.log('Notification channel created:', created)
      );
    } catch (error) {
      console.error('Failed to initialize push notifications:', error);
    }
  }

  private initializeNetworkMonitoring() {
    try {
      NetInfo.addEventListener(state => {
        console.log('Network state changed:', state);
        
        // Store network state in Redux if needed
        // store.dispatch(setNetworkState(state));
      });
    } catch (error) {
      console.error('Failed to initialize network monitoring:', error);
    }
  }

  private handleNotificationTap(notification: any) {
    try {
      // Handle notification tap based on type
      const { data } = notification;
      
      if (data?.domainId) {
        // Navigate to domain detail
        // NavigationService.navigate('DomainDetail', { domainId: data.domainId });
      } else if (data?.screen) {
        // Navigate to specific screen
        // NavigationService.navigate(data.screen);
      }
    } catch (error) {
      console.error('Failed to handle notification tap:', error);
    }
  }

  // Public methods
  async showLocalNotification(title: string, message: string, data?: any) {
    try {
      PushNotification.localNotification({
        channelId: 'ssl-monitor-pro',
        title,
        message,
        data,
        playSound: true,
        soundName: 'default',
        vibrate: true,
        vibration: 300,
      });
    } catch (error) {
      console.error('Failed to show local notification:', error);
    }
  }

  async scheduleNotification(title: string, message: string, date: Date, data?: any) {
    try {
      PushNotification.localNotificationSchedule({
        channelId: 'ssl-monitor-pro',
        title,
        message,
        date,
        data,
        playSound: true,
        soundName: 'default',
        vibrate: true,
        vibration: 300,
      });
    } catch (error) {
      console.error('Failed to schedule notification:', error);
    }
  }

  async cancelAllNotifications() {
    try {
      PushNotification.cancelAllLocalNotifications();
    } catch (error) {
      console.error('Failed to cancel notifications:', error);
    }
  }

  async getAppVersion(): Promise<string> {
    try {
      return await DeviceInfo.getVersion();
    } catch (error) {
      console.error('Failed to get app version:', error);
      return '1.0.0';
    }
  }

  async getDeviceInfo() {
    try {
      return {
        deviceId: await DeviceInfo.getUniqueId(),
        deviceName: await DeviceInfo.getDeviceName(),
        systemName: await DeviceInfo.getSystemName(),
        systemVersion: await DeviceInfo.getSystemVersion(),
        appVersion: await DeviceInfo.getVersion(),
        buildNumber: await DeviceInfo.getBuildNumber(),
        bundleId: await DeviceInfo.getBundleId(),
        isEmulator: await DeviceInfo.isEmulator(),
      };
    } catch (error) {
      console.error('Failed to get device info:', error);
      return null;
    }
  }
}

export const initializeApp = async () => {
  const appService = new AppService();
  await appService.initialize();
};

export const AppService = new AppService();
