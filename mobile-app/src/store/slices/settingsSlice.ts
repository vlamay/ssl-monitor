/**
 * Settings Redux Slice
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface NotificationSettings {
  push: boolean;
  email: boolean;
  telegram: boolean;
  slack: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
}

export interface AppSettings {
  language: string;
  timezone: string;
  theme: 'light' | 'dark' | 'auto';
  auto_refresh: boolean;
  refresh_interval: number; // in seconds
  notifications: NotificationSettings;
  biometric_auth: boolean;
  analytics_enabled: boolean;
}

interface SettingsState {
  settings: AppSettings;
  isInitialized: boolean;
}

const initialState: SettingsState = {
  settings: {
    language: 'en',
    timezone: 'UTC',
    theme: 'light',
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
  },
  isInitialized: false,
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    initializeSettings: (state, action: PayloadAction<AppSettings>) => {
      state.settings = action.payload;
      state.isInitialized = true;
    },
    updateSettings: (state, action: PayloadAction<Partial<AppSettings>>) => {
      state.settings = { ...state.settings, ...action.payload };
    },
    updateNotificationSettings: (state, action: PayloadAction<Partial<NotificationSettings>>) => {
      state.settings.notifications = { ...state.settings.notifications, ...action.payload };
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.settings.theme = action.payload;
    },
    setLanguage: (state, action: PayloadAction<string>) => {
      state.settings.language = action.payload;
    },
    setTimezone: (state, action: PayloadAction<string>) => {
      state.settings.timezone = action.payload;
    },
    toggleBiometricAuth: (state) => {
      state.settings.biometric_auth = !state.settings.biometric_auth;
    },
    toggleAnalytics: (state) => {
      state.settings.analytics_enabled = !state.settings.analytics_enabled;
    },
    resetSettings: (state) => {
      state.settings = initialState.settings;
    },
  },
});

export const {
  initializeSettings,
  updateSettings,
  updateNotificationSettings,
  setTheme,
  setLanguage,
  setTimezone,
  toggleBiometricAuth,
  toggleAnalytics,
  resetSettings,
} = settingsSlice.actions;

export default settingsSlice.reducer;
