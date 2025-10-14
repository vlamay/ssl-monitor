/**
 * Settings Screen - App configuration and preferences
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  Linking,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { RootState, AppDispatch } from '../../store';
import { updateSettings, logoutUser } from '../../store/slices/authSlice';
import { toggleTheme } from '../../store/slices/themeSlice';
import { useTheme } from '../../hooks/useTheme';

const SettingsScreen: React.FC = () => {
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);

  const dispatch = useDispatch<AppDispatch>();
  const theme = useTheme();

  const { user } = useSelector((state: RootState) => state.auth);
  const { mode } = useSelector((state: RootState) => state.theme);

  const handleToggleTheme = () => {
    dispatch(toggleTheme());
  };

  const handleToggleBiometric = (value: boolean) => {
    setBiometricEnabled(value);
    // TODO: Implement biometric authentication toggle
  };

  const handleToggleNotifications = (value: boolean) => {
    setNotificationsEnabled(value);
    // TODO: Implement notifications toggle
  };

  const handleToggleAutoRefresh = (value: boolean) => {
    setAutoRefreshEnabled(value);
    // TODO: Implement auto refresh toggle
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            try {
              await dispatch(logoutUser()).unwrap();
            } catch (error) {
              console.error('Logout error:', error);
            }
          },
        },
      ]
    );
  };

  const handleOpenLink = (url: string) => {
    Linking.openURL(url).catch((err) => {
      console.error('Failed to open link:', err);
    });
  };

  const renderSettingItem = (
    title: string,
    subtitle?: string,
    icon?: string,
    onPress?: () => void,
    rightComponent?: React.ReactNode
  ) => (
    <TouchableOpacity
      style={styles.settingItem}
      onPress={onPress}
      disabled={!onPress}
    >
      <View style={styles.settingLeft}>
        {icon && (
          <Icon name={icon} size={24} color={theme.colors.textSecondary} style={styles.settingIcon} />
        )}
        <View style={styles.settingText}>
          <Text style={styles.settingTitle}>{title}</Text>
          {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
        </View>
      </View>
      {rightComponent || (onPress && <Icon name="chevron-right" size={24} color={theme.colors.textSecondary} />)}
    </TouchableOpacity>
  );

  const renderSection = (title: string, children: React.ReactNode) => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <View style={styles.sectionContent}>
        {children}
      </View>
    </View>
  );

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    content: {
      flex: 1,
    },
    section: {
      marginBottom: theme.spacing.xl,
    },
    sectionTitle: {
      fontSize: theme.fonts.sizes.md,
      fontWeight: '600',
      color: theme.colors.text,
      marginBottom: theme.spacing.sm,
      paddingHorizontal: theme.spacing.lg,
    },
    sectionContent: {
      backgroundColor: theme.colors.surface,
      borderTopWidth: 1,
      borderBottomWidth: 1,
      borderColor: theme.colors.border,
    },
    settingItem: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingHorizontal: theme.spacing.lg,
      paddingVertical: theme.spacing.md,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    settingLeft: {
      flexDirection: 'row',
      alignItems: 'center',
      flex: 1,
    },
    settingIcon: {
      marginRight: theme.spacing.md,
      width: 24,
    },
    settingText: {
      flex: 1,
    },
    settingTitle: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    settingSubtitle: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
    },
    userInfo: {
      backgroundColor: theme.colors.surface,
      padding: theme.spacing.lg,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    userName: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    userEmail: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.textSecondary,
    },
    versionInfo: {
      alignItems: 'center',
      paddingVertical: theme.spacing.xl,
      paddingHorizontal: theme.spacing.lg,
    },
    versionText: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
      marginBottom: theme.spacing.sm,
    },
    appName: {
      fontSize: theme.fonts.sizes.md,
      fontWeight: '600',
      color: theme.colors.text,
    },
    logoutButton: {
      backgroundColor: theme.colors.error,
      marginHorizontal: theme.spacing.lg,
      marginVertical: theme.spacing.lg,
      paddingVertical: theme.spacing.md,
      borderRadius: 8,
      alignItems: 'center',
    },
    logoutButtonText: {
      fontSize: theme.fonts.sizes.md,
      fontWeight: '600',
      color: '#FFFFFF',
    },
  });

  return (
    <View style={styles.container}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.userInfo}>
          <Text style={styles.userName}>{user?.name || 'User'}</Text>
          <Text style={styles.userEmail}>{user?.email}</Text>
        </View>

        {renderSection('Appearance', (
          <>
            {renderSettingItem(
              'Dark Mode',
              'Switch between light and dark themes',
              'dark-mode',
              handleToggleTheme,
              <Switch
                value={mode === 'dark'}
                onValueChange={handleToggleTheme}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
                thumbColor={mode === 'dark' ? '#FFFFFF' : '#FFFFFF'}
              />
            )}
          </>
        ))}

        {renderSection('Notifications', (
          <>
            {renderSettingItem(
              'Push Notifications',
              'Receive alerts for SSL certificate issues',
              'notifications',
              undefined,
              <Switch
                value={notificationsEnabled}
                onValueChange={handleToggleNotifications}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
                thumbColor={notificationsEnabled ? '#FFFFFF' : '#FFFFFF'}
              />
            )}
            {renderSettingItem(
              'Email Notifications',
              'Get notified via email',
              'email',
              undefined,
              <Switch
                value={notificationsEnabled}
                onValueChange={handleToggleNotifications}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
                thumbColor={notificationsEnabled ? '#FFFFFF' : '#FFFFFF'}
              />
            )}
          </>
        ))}

        {renderSection('Security', (
          <>
            {renderSettingItem(
              'Biometric Authentication',
              'Use fingerprint or face ID to unlock',
              'fingerprint',
              undefined,
              <Switch
                value={biometricEnabled}
                onValueChange={handleToggleBiometric}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
                thumbColor={biometricEnabled ? '#FFFFFF' : '#FFFFFF'}
              />
            )}
            {renderSettingItem(
              'Change Password',
              'Update your account password',
              'lock',
              () => {
                // TODO: Navigate to change password screen
                Alert.alert('Coming Soon', 'Password change feature will be available soon.');
              }
            )}
          </>
        ))}

        {renderSection('Monitoring', (
          <>
            {renderSettingItem(
              'Auto Refresh',
              'Automatically refresh domain status',
              'refresh',
              undefined,
              <Switch
                value={autoRefreshEnabled}
                onValueChange={handleToggleAutoRefresh}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
                thumbColor={autoRefreshEnabled ? '#FFFFFF' : '#FFFFFF'}
              />
            )}
            {renderSettingItem(
              'Default Alert Threshold',
              'Set default days before expiry alerts',
              'schedule',
              () => {
                // TODO: Navigate to alert threshold settings
                Alert.alert('Coming Soon', 'Alert threshold settings will be available soon.');
              }
            )}
          </>
        ))}

        {renderSection('Support', (
          <>
            {renderSettingItem(
              'Help & FAQ',
              'Get help and find answers',
              'help',
              () => handleOpenLink('https://ssl-monitor-pro.com/help')
            )}
            {renderSettingItem(
              'Contact Support',
              'Get in touch with our team',
              'support',
              () => handleOpenLink('mailto:support@ssl-monitor-pro.com')
            )}
            {renderSettingItem(
              'Privacy Policy',
              'Read our privacy policy',
              'privacy-tip',
              () => handleOpenLink('https://ssl-monitor-pro.com/privacy')
            )}
            {renderSettingItem(
              'Terms of Service',
              'Read our terms of service',
              'description',
              () => handleOpenLink('https://ssl-monitor-pro.com/terms')
            )}
          </>
        ))}

        {renderSection('About', (
          <>
            {renderSettingItem(
              'App Version',
              '1.0.0',
              'info'
            )}
            {renderSettingItem(
              'Rate App',
              'Rate us on the App Store',
              'star',
              () => {
                // TODO: Open app store rating
                Alert.alert('Thank you!', 'Rating feature will be available when published.');
              }
            )}
            {renderSettingItem(
              'Share App',
              'Tell your friends about SSL Monitor Pro',
              'share',
              () => {
                // TODO: Implement share functionality
                Alert.alert('Coming Soon', 'Share feature will be available soon.');
              }
            )}
          </>
        ))}

        <View style={styles.versionInfo}>
          <Text style={styles.versionText}>SSL Monitor Pro</Text>
          <Text style={styles.appName}>Professional SSL Certificate Monitoring</Text>
        </View>
      </ScrollView>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutButtonText}>Logout</Text>
      </TouchableOpacity>
    </View>
  );
};

export default SettingsScreen;
