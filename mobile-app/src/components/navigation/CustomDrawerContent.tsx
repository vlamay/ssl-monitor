/**
 * Custom Drawer Content Component
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { DrawerContentScrollView, DrawerContentComponentProps } from '@react-navigation/drawer';
import { useDispatch, useSelector } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { RootState, AppDispatch } from '../../store';
import { logoutUser } from '../../store/slices/authSlice';
import { useTheme } from '../../hooks/useTheme';

const CustomDrawerContent: React.FC<DrawerContentComponentProps> = (props) => {
  const { navigation } = props;
  const dispatch = useDispatch<AppDispatch>();
  const theme = useTheme();
  
  const { user } = useSelector((state: RootState) => state.auth);
  const { unreadCount } = useSelector((state: RootState) => state.notifications);

  const handleLogout = async () => {
    try {
      await dispatch(logoutUser()).unwrap();
      navigation.reset({
        index: 0,
        routes: [{ name: 'Login' as never }],
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.surface,
    },
    header: {
      padding: theme.spacing.lg,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
      backgroundColor: theme.colors.primary,
    },
    userInfo: {
      alignItems: 'center',
    },
    avatar: {
      width: 60,
      height: 60,
      borderRadius: 30,
      backgroundColor: '#FFFFFF',
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: theme.spacing.md,
    },
    userName: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: '#FFFFFF',
      marginBottom: theme.spacing.xs,
    },
    userEmail: {
      fontSize: theme.fonts.sizes.sm,
      color: 'rgba(255, 255, 255, 0.8)',
    },
    menuContainer: {
      flex: 1,
      paddingTop: theme.spacing.lg,
    },
    menuItem: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: theme.spacing.lg,
      paddingVertical: theme.spacing.md,
    },
    menuIcon: {
      marginRight: theme.spacing.md,
      width: 24,
    },
    menuText: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.text,
      flex: 1,
    },
    badge: {
      backgroundColor: theme.colors.error,
      borderRadius: 10,
      minWidth: 20,
      height: 20,
      justifyContent: 'center',
      alignItems: 'center',
      paddingHorizontal: 6,
    },
    badgeText: {
      color: '#FFFFFF',
      fontSize: 12,
      fontWeight: '600',
    },
    logoutContainer: {
      padding: theme.spacing.lg,
      borderTopWidth: 1,
      borderTopColor: theme.colors.border,
    },
    logoutButton: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: theme.spacing.md,
    },
    logoutIcon: {
      marginRight: theme.spacing.md,
    },
    logoutText: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.error,
      fontWeight: '600',
    },
  });

  const menuItems = [
    {
      name: 'Dashboard',
      icon: 'dashboard',
      onPress: () => navigation.navigate('Tabs' as never),
    },
    {
      name: 'Domains',
      icon: 'domain',
      onPress: () => navigation.navigate('Tabs' as never),
    },
    {
      name: 'Analytics',
      icon: 'analytics',
      onPress: () => navigation.navigate('Tabs' as never),
    },
    {
      name: 'Notifications',
      icon: 'notifications',
      badge: unreadCount > 0 ? unreadCount : undefined,
      onPress: () => navigation.navigate('Tabs' as never),
    },
    {
      name: 'Profile',
      icon: 'person',
      onPress: () => navigation.navigate('Profile' as never),
    },
    {
      name: 'Settings',
      icon: 'settings',
      onPress: () => navigation.navigate('Settings' as never),
    },
  ];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.userInfo}>
          <View style={styles.avatar}>
            <Icon name="person" size={30} color={theme.colors.primary} />
          </View>
          <Text style={styles.userName}>{user?.name || 'User'}</Text>
          <Text style={styles.userEmail}>{user?.email}</Text>
        </View>
      </View>

      <View style={styles.menuContainer}>
        {menuItems.map((item) => (
          <TouchableOpacity
            key={item.name}
            style={styles.menuItem}
            onPress={item.onPress}
          >
            <Icon
              name={item.icon as any}
              size={24}
              color={theme.colors.textSecondary}
              style={styles.menuIcon}
            />
            <Text style={styles.menuText}>{item.name}</Text>
            {item.badge && (
              <View style={styles.badge}>
                <Text style={styles.badgeText}>
                  {item.badge > 99 ? '99+' : item.badge}
                </Text>
              </View>
            )}
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.logoutContainer}>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Icon
            name="logout"
            size={24}
            color={theme.colors.error}
            style={styles.logoutIcon}
          />
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default CustomDrawerContent;
