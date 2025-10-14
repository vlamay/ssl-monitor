/**
 * Notification Slice
 */

import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import { notificationService, NotificationData } from '../../services/NotificationService';

interface Notification {
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

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
}

const initialState: NotificationState = {
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null,
};

// Async thunks
export const fetchNotifications = createAsyncThunk(
  'notifications/fetchNotifications',
  async () => {
    return await notificationService.getStoredNotifications();
  }
);

export const markAsRead = createAsyncThunk(
  'notifications/markAsRead',
  async (notificationId: string) => {
    await notificationService.markNotificationAsRead(notificationId);
    return notificationId;
  }
);

export const markAllAsRead = createAsyncThunk(
  'notifications/markAllAsRead',
  async () => {
    await notificationService.markAllNotificationsAsRead();
  }
);

export const deleteNotification = createAsyncThunk(
  'notifications/deleteNotification',
  async (notificationId: string) => {
    await notificationService.deleteNotification(notificationId);
    return notificationId;
  }
);

export const sendSSLExpiringNotification = createAsyncThunk(
  'notifications/sendSSLExpiringNotification',
  async ({ domainName, expiresIn, domainId }: { domainName: string; expiresIn: number; domainId: string }) => {
    await notificationService.notifySSLExpiring(domainName, expiresIn, domainId);
  }
);

export const sendSSLExpiredNotification = createAsyncThunk(
  'notifications/sendSSLExpiredNotification',
  async ({ domainName, domainId }: { domainName: string; domainId: string }) => {
    await notificationService.notifySSLExpired(domainName, domainId);
  }
);

export const sendSSLRenewedNotification = createAsyncThunk(
  'notifications/sendSSLRenewedNotification',
  async ({ domainName, domainId }: { domainName: string; domainId: string }) => {
    await notificationService.notifySSLRenewed(domainName, domainId);
  }
);

export const sendDomainAddedNotification = createAsyncThunk(
  'notifications/sendDomainAddedNotification',
  async ({ domainName, domainId }: { domainName: string; domainId: string }) => {
    await notificationService.notifyDomainAdded(domainName, domainId);
  }
);

const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id' | 'timestamp' | 'read'>>) => {
      const newNotification: Notification = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        read: false,
        ...action.payload,
      };
      state.notifications.unshift(newNotification);
      state.unreadCount += 1;
    },
    clearNotifications: (state) => {
      state.notifications = [];
      state.unreadCount = 0;
    },
    updateUnreadCount: (state) => {
      state.unreadCount = state.notifications.filter(n => !n.read).length;
    },
  },
  extraReducers: (builder) => {
    // Fetch notifications
    builder
      .addCase(fetchNotifications.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchNotifications.fulfilled, (state, action) => {
        state.loading = false;
        state.notifications = action.payload;
        state.unreadCount = action.payload.filter(n => !n.read).length;
      })
      .addCase(fetchNotifications.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch notifications';
      });

    // Mark as read
    builder
      .addCase(markAsRead.fulfilled, (state, action) => {
        const notification = state.notifications.find(n => n.id === action.payload);
        if (notification && !notification.read) {
          notification.read = true;
          state.unreadCount -= 1;
        }
      });

    // Mark all as read
    builder
      .addCase(markAllAsRead.fulfilled, (state) => {
        state.notifications.forEach(n => (n.read = true));
        state.unreadCount = 0;
      });

    // Delete notification
    builder
      .addCase(deleteNotification.fulfilled, (state, action) => {
        const notification = state.notifications.find(n => n.id === action.payload);
        if (notification && !notification.read) {
          state.unreadCount -= 1;
        }
        state.notifications = state.notifications.filter(n => n.id !== action.payload);
      });
  },
});

export const { addNotification, clearNotifications, updateUnreadCount } = notificationSlice.actions;
export default notificationSlice.reducer;