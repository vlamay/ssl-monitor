/**
 * Push Notification Service
 */

import PushNotification from 'react-native-push-notification';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface NotificationData {
  id: string;
  title: string;
  message: string;
  type: 'ssl_expired' | 'ssl_expiring' | 'ssl_renewed' | 'domain_added' | 'system';
  domainId?: string;
  domainName?: string;
  expiresIn?: number;
  timestamp: string;
  read: boolean;
}

class NotificationService {
  private isInitialized = false;

  constructor() {
    this.initializeNotifications();
  }

  private initializeNotifications() {
    if (this.isInitialized) return;

    try {
      // Configure push notifications
      PushNotification.configure({
        onRegister: (token) => {
          console.log('Push notification token:', token);
          this.saveToken(token.token);
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

      // Create notification channels for Android
      if (Platform.OS === 'android') {
        this.createNotificationChannels();
      }

      this.isInitialized = true;
      console.log('Notification service initialized');
    } catch (error) {
      console.error('Failed to initialize notification service:', error);
    }
  }

  private createNotificationChannels() {
    const channels = [
      {
        channelId: 'ssl-alerts',
        channelName: 'SSL Certificate Alerts',
        channelDescription: 'Notifications for SSL certificate expiry and issues',
        importance: 4,
        vibrate: true,
      },
      {
        channelId: 'domain-updates',
        channelName: 'Domain Updates',
        channelDescription: 'Notifications for domain management updates',
        importance: 3,
        vibrate: false,
      },
      {
        channelId: 'system',
        channelName: 'System Notifications',
        channelDescription: 'General system and app notifications',
        importance: 2,
        vibrate: false,
      },
    ];

    channels.forEach(channel => {
      PushNotification.createChannel(
        channel,
        (created) => console.log(`Notification channel created: ${channel.channelId}`, created)
      );
    });
  }

  private async saveToken(token: string) {
    try {
      await AsyncStorage.setItem('push_notification_token', token);
      // TODO: Send token to backend server
      console.log('Push notification token saved:', token);
    } catch (error) {
      console.error('Failed to save push notification token:', error);
    }
  }

  private async getToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('push_notification_token');
    } catch (error) {
      console.error('Failed to get push notification token:', error);
      return null;
    }
  }

  private handleNotificationTap(notification: any) {
    try {
      const { data } = notification;
      
      if (data?.domainId) {
        // Navigate to domain detail
        // NavigationService.navigate('DomainDetail', { domainId: data.domainId });
        console.log('Navigate to domain:', data.domainId);
      } else if (data?.screen) {
        // Navigate to specific screen
        // NavigationService.navigate(data.screen);
        console.log('Navigate to screen:', data.screen);
      }
    } catch (error) {
      console.error('Failed to handle notification tap:', error);
    }
  }

  // Public methods
  async showLocalNotification(
    title: string,
    message: string,
    data?: any,
    channelId: string = 'ssl-alerts'
  ) {
    try {
      PushNotification.localNotification({
        channelId,
        title,
        message,
        data,
        playSound: true,
        soundName: 'default',
        vibrate: true,
        vibration: 300,
        priority: 'high',
        importance: 'high',
        autoCancel: true,
        ongoing: false,
        actions: ['View', 'Dismiss'],
      });

      // Store notification in local storage
      await this.storeNotification({
        id: Date.now().toString(),
        title,
        message,
        type: data?.type || 'system',
        domainId: data?.domainId,
        domainName: data?.domainName,
        expiresIn: data?.expiresIn,
        timestamp: new Date().toISOString(),
        read: false,
      });
    } catch (error) {
      console.error('Failed to show local notification:', error);
    }
  }

  async scheduleNotification(
    title: string,
    message: string,
    date: Date,
    data?: any,
    channelId: string = 'ssl-alerts'
  ) {
    try {
      PushNotification.localNotificationSchedule({
        channelId,
        title,
        message,
        date,
        data,
        playSound: true,
        soundName: 'default',
        vibrate: true,
        vibration: 300,
        priority: 'high',
        importance: 'high',
        autoCancel: true,
        ongoing: false,
      });

      console.log(`Notification scheduled for ${date.toISOString()}`);
    } catch (error) {
      console.error('Failed to schedule notification:', error);
    }
  }

  async cancelNotification(id: string) {
    try {
      PushNotification.cancelLocalNotifications({ id });
      console.log(`Notification cancelled: ${id}`);
    } catch (error) {
      console.error('Failed to cancel notification:', error);
    }
  }

  async cancelAllNotifications() {
    try {
      PushNotification.cancelAllLocalNotifications();
      console.log('All notifications cancelled');
    } catch (error) {
      console.error('Failed to cancel all notifications:', error);
    }
  }

  async clearNotificationBadge() {
    try {
      PushNotification.setApplicationIconBadgeNumber(0);
    } catch (error) {
      console.error('Failed to clear notification badge:', error);
    }
  }

  async setNotificationBadge(count: number) {
    try {
      PushNotification.setApplicationIconBadgeNumber(count);
    } catch (error) {
      console.error('Failed to set notification badge:', error);
    }
  }

  // SSL-specific notification methods
  async notifySSLExpiring(domainName: string, expiresIn: number, domainId: string) {
    const title = 'SSL Certificate Expiring Soon';
    const message = `${domainName} SSL certificate expires in ${expiresIn} days`;
    
    const data = {
      type: 'ssl_expiring',
      domainId,
      domainName,
      expiresIn,
    };

    await this.showLocalNotification(title, message, data, 'ssl-alerts');
  }

  async notifySSLExpired(domainName: string, domainId: string) {
    const title = 'SSL Certificate Expired';
    const message = `${domainName} SSL certificate has expired`;
    
    const data = {
      type: 'ssl_expired',
      domainId,
      domainName,
      expiresIn: 0,
    };

    await this.showLocalNotification(title, message, data, 'ssl-alerts');
  }

  async notifySSLRenewed(domainName: string, domainId: string) {
    const title = 'SSL Certificate Renewed';
    const message = `${domainName} SSL certificate has been renewed`;
    
    const data = {
      type: 'ssl_renewed',
      domainId,
      domainName,
    };

    await this.showLocalNotification(title, message, data, 'domain-updates');
  }

  async notifyDomainAdded(domainName: string, domainId: string) {
    const title = 'Domain Added';
    const message = `${domainName} has been added to monitoring`;
    
    const data = {
      type: 'domain_added',
      domainId,
      domainName,
    };

    await this.showLocalNotification(title, message, data, 'domain-updates');
  }

  // Storage methods
  private async storeNotification(notification: NotificationData) {
    try {
      const existingNotifications = await this.getStoredNotifications();
      existingNotifications.unshift(notification); // Add to beginning
      
      // Keep only last 100 notifications
      const limitedNotifications = existingNotifications.slice(0, 100);
      
      await AsyncStorage.setItem(
        'notifications',
        JSON.stringify(limitedNotifications)
      );
    } catch (error) {
      console.error('Failed to store notification:', error);
    }
  }

  async getStoredNotifications(): Promise<NotificationData[]> {
    try {
      const notifications = await AsyncStorage.getItem('notifications');
      return notifications ? JSON.parse(notifications) : [];
    } catch (error) {
      console.error('Failed to get stored notifications:', error);
      return [];
    }
  }

  async markNotificationAsRead(id: string) {
    try {
      const notifications = await this.getStoredNotifications();
      const updatedNotifications = notifications.map(notification =>
        notification.id === id ? { ...notification, read: true } : notification
      );
      
      await AsyncStorage.setItem(
        'notifications',
        JSON.stringify(updatedNotifications)
      );
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  }

  async markAllNotificationsAsRead() {
    try {
      const notifications = await this.getStoredNotifications();
      const updatedNotifications = notifications.map(notification =>
        ({ ...notification, read: true })
      );
      
      await AsyncStorage.setItem(
        'notifications',
        JSON.stringify(updatedNotifications)
      );
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  }

  async deleteNotification(id: string) {
    try {
      const notifications = await this.getStoredNotifications();
      const updatedNotifications = notifications.filter(notification => notification.id !== id);
      
      await AsyncStorage.setItem(
        'notifications',
        JSON.stringify(updatedNotifications)
      );
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  }

  async clearAllNotifications() {
    try {
      await AsyncStorage.removeItem('notifications');
    } catch (error) {
      console.error('Failed to clear all notifications:', error);
    }
  }

  async getUnreadCount(): Promise<number> {
    try {
      const notifications = await this.getStoredNotifications();
      return notifications.filter(notification => !notification.read).length;
    } catch (error) {
      console.error('Failed to get unread count:', error);
      return 0;
    }
  }

  // Background job methods
  async scheduleSSLCheckNotifications(domains: any[]) {
    try {
      // Cancel existing scheduled notifications
      await this.cancelAllNotifications();

      // Schedule new notifications for domains expiring soon
      domains.forEach(domain => {
        if (domain.ssl_status?.expires_in <= 30 && domain.ssl_status?.expires_in > 0) {
          const notificationDate = new Date();
          notificationDate.setDate(notificationDate.getDate() + (domain.ssl_status.expires_in - 7));
          
          if (notificationDate > new Date()) {
            this.scheduleNotification(
              'SSL Certificate Expiring Soon',
              `${domain.name} SSL certificate expires in 7 days`,
              notificationDate,
              {
                type: 'ssl_expiring',
                domainId: domain.id,
                domainName: domain.name,
                expiresIn: domain.ssl_status.expires_in,
              }
            );
          }
        }
      });
    } catch (error) {
      console.error('Failed to schedule SSL check notifications:', error);
    }
  }
}

export const notificationService = new NotificationService();
