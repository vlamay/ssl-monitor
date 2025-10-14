/**
 * Theme Redux Slice
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  error: string;
  warning: string;
  success: string;
  info: string;
}

export interface Theme {
  mode: 'light' | 'dark';
  colors: ThemeColors;
  fonts: {
    regular: string;
    medium: string;
    bold: string;
    sizes: {
      xs: number;
      sm: number;
      md: number;
      lg: number;
      xl: number;
      xxl: number;
    };
  };
  spacing: {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
    xxl: number;
  };
}

const lightTheme: Theme = {
  mode: 'light',
  colors: {
    primary: '#3B82F6',
    secondary: '#10B981',
    background: '#FFFFFF',
    surface: '#F8FAFC',
    text: '#1F2937',
    textSecondary: '#6B7280',
    border: '#E5E7EB',
    error: '#EF4444',
    warning: '#F59E0B',
    success: '#10B981',
    info: '#3B82F6',
  },
  fonts: {
    regular: 'System',
    medium: 'System',
    bold: 'System',
    sizes: {
      xs: 12,
      sm: 14,
      md: 16,
      lg: 18,
      xl: 20,
      xxl: 24,
    },
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
};

const darkTheme: Theme = {
  mode: 'dark',
  colors: {
    primary: '#60A5FA',
    secondary: '#34D399',
    background: '#111827',
    surface: '#1F2937',
    text: '#F9FAFB',
    textSecondary: '#9CA3AF',
    border: '#374151',
    error: '#F87171',
    warning: '#FBBF24',
    success: '#34D399',
    info: '#60A5FA',
  },
  fonts: {
    regular: 'System',
    medium: 'System',
    bold: 'System',
    sizes: {
      xs: 12,
      sm: 14,
      md: 16,
      lg: 18,
      xl: 20,
      xxl: 24,
    },
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
};

interface ThemeState {
  currentTheme: Theme;
  systemTheme: 'light' | 'dark';
  userPreference: 'light' | 'dark' | 'auto';
}

const initialState: ThemeState = {
  currentTheme: lightTheme,
  systemTheme: 'light',
  userPreference: 'light',
};

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    setUserPreference: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.userPreference = action.payload;
      state.currentTheme = action.payload === 'auto' 
        ? (state.systemTheme === 'dark' ? darkTheme : lightTheme)
        : (action.payload === 'dark' ? darkTheme : lightTheme);
    },
    setSystemTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.systemTheme = action.payload;
      if (state.userPreference === 'auto') {
        state.currentTheme = action.payload === 'dark' ? darkTheme : lightTheme;
      }
    },
    toggleTheme: (state) => {
      const newPreference = state.currentTheme.mode === 'light' ? 'dark' : 'light';
      state.userPreference = newPreference;
      state.currentTheme = newPreference === 'dark' ? darkTheme : lightTheme;
    },
  },
});

export const { setUserPreference, setSystemTheme, toggleTheme } = themeSlice.actions;
export default themeSlice.reducer;
