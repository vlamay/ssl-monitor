/**
 * Notifications Screen - Push notifications and alerts
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { RootState, AppDispatch } from '../../store';
import { fetchNotifications, markAsRead, markAllAsRead, deleteNotification } from '../../store/slices/notificationSlice';
import { useTheme } from '../../hooks/useTheme';
import { formatTimeAgo } from '../../utils/dateUtils';

const NotificationsScreen: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);

  const dispatch = useDispatch<AppDispatch>();
  const theme = useTheme();

  const { notifications, unreadCount, isLoading } = useSelector((state: RootState) => state.notifications);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      await dispatch(fetchNotifications()).unwrap();
    } catch (error) {
      console.error('Error loading notifications:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadNotifications();
    setRefreshing(false);
  };

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await dispatch(markAsRead(notificationId)).unwrap();
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await dispatch(markAllAsRead()).unwrap();
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  const handleDeleteNotification = (notificationId: string) => {
    Alert.alert(
      'Delete Notification',
      'Are you sure you want to delete this notification?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await dispatch(deleteNotification(notificationId)).unwrap();
            } catch (error) {
              console.error('Error deleting notification:', error);
            }
          },
        },
      ]
    );
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'ssl_expired':
        return 'error';
      case 'ssl_expiring':
        return 'warning';
      case 'ssl_renewed':
        return 'check-circle';
      case 'domain_added':
        return 'add-circle';
      case 'domain_removed':
        return 'remove-circle';
      case 'system':
        return 'info';
      default:
        return 'notifications';
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'ssl_expired':
        return theme.colors.error;
      case 'ssl_expiring':
        return theme.colors.warning;
      case 'ssl_renewed':
        return theme.colors.success;
      case 'domain_added':
        return theme.colors.info;
      case 'domain_removed':
        return theme.colors.textSecondary;
      case 'system':
        return theme.colors.primary;
      default:
        return theme.colors.textSecondary;
    }
  };

  const renderNotificationItem = ({ item }: { item: any }) => {
    const iconName = getNotificationIcon(item.type);
    const iconColor = getNotificationColor(item.type);

    return (
      <TouchableOpacity
        style={[
          styles.notificationCard,
          !item.read && styles.unreadNotification,
        ]}
        onPress={() => handleMarkAsRead(item.id)}
        activeOpacity={0.7}
      >
        <View style={styles.notificationContent}>
          <View style={styles.notificationIcon}>
            <Icon name={iconName} size={24} color={iconColor} />
          </View>
          
          <View style={styles.notificationText}>
            <Text style={[
              styles.notificationTitle,
              !item.read && styles.unreadText,
            ]}>
              {item.title}
            </Text>
            <Text style={styles.notificationMessage}>
              {item.message}
            </Text>
            <Text style={styles.notificationTime}>
              {formatTimeAgo(item.timestamp)}
            </Text>
          </View>

          <View style={styles.notificationActions}>
            {!item.read && (
              <View style={styles.unreadIndicator} />
            )}
            <TouchableOpacity
              style={styles.deleteButton}
              onPress={() => handleDeleteNotification(item.id)}
            >
              <Icon name="close" size={20} color={theme.colors.textSecondary} />
            </TouchableOpacity>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Icon name="notifications-none" size={64} color={theme.colors.textSecondary} />
      <Text style={styles.emptyTitle}>No Notifications</Text>
      <Text style={styles.emptyDescription}>
        You're all caught up! New SSL alerts and updates will appear here.
      </Text>
    </View>
  );

  const renderHeader = () => (
    <View style={styles.header}>
      <View style={styles.headerInfo}>
        <Text style={styles.headerTitle}>Notifications</Text>
        {unreadCount > 0 && (
          <Text style={styles.unreadCount}>{unreadCount} unread</Text>
        )}
      </View>
      
      {unreadCount > 0 && (
        <TouchableOpacity
          style={styles.markAllButton}
          onPress={handleMarkAllAsRead}
        >
          <Icon name="done-all" size={20} color={theme.colors.primary} />
          <Text style={styles.markAllText}>Mark all read</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    header: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingHorizontal: theme.spacing.lg,
      paddingVertical: theme.spacing.md,
      backgroundColor: theme.colors.surface,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    headerInfo: {
      flex: 1,
    },
    headerTitle: {
      fontSize: theme.fonts.sizes.xl,
      fontWeight: 'bold',
      color: theme.colors.text,
    },
    unreadCount: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
      marginTop: theme.spacing.xs,
    },
    markAllButton: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: theme.spacing.sm,
      paddingHorizontal: theme.spacing.md,
      backgroundColor: theme.colors.background,
      borderRadius: 6,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    markAllText: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.primary,
      marginLeft: theme.spacing.xs,
      fontWeight: '500',
    },
    content: {
      flex: 1,
    },
    notificationsList: {
      flex: 1,
      paddingHorizontal: theme.spacing.lg,
    },
    notificationCard: {
      backgroundColor: theme.colors.surface,
      borderRadius: 12,
      marginVertical: theme.spacing.xs,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    unreadNotification: {
      borderLeftWidth: 4,
      borderLeftColor: theme.colors.primary,
    },
    notificationContent: {
      flexDirection: 'row',
      padding: theme.spacing.lg,
    },
    notificationIcon: {
      marginRight: theme.spacing.md,
      marginTop: theme.spacing.xs,
    },
    notificationText: {
      flex: 1,
    },
    notificationTitle: {
      fontSize: theme.fonts.sizes.md,
      fontWeight: '500',
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    unreadText: {
      fontWeight: '600',
    },
    notificationMessage: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
      lineHeight: 18,
      marginBottom: theme.spacing.sm,
    },
    notificationTime: {
      fontSize: theme.fonts.sizes.xs,
      color: theme.colors.textSecondary,
    },
    notificationActions: {
      alignItems: 'center',
      justifyContent: 'space-between',
      marginLeft: theme.spacing.sm,
    },
    unreadIndicator: {
      width: 8,
      height: 8,
      borderRadius: 4,
      backgroundColor: theme.colors.primary,
      marginBottom: theme.spacing.sm,
    },
    deleteButton: {
      padding: theme.spacing.xs,
    },
    emptyState: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      paddingHorizontal: theme.spacing.xl,
    },
    emptyTitle: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: theme.colors.text,
      marginTop: theme.spacing.lg,
      marginBottom: theme.spacing.sm,
    },
    emptyDescription: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.textSecondary,
      textAlign: 'center',
      lineHeight: 20,
    },
    filterContainer: {
      flexDirection: 'row',
      paddingHorizontal: theme.spacing.lg,
      paddingVertical: theme.spacing.md,
      backgroundColor: theme.colors.surface,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    filterChip: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: theme.spacing.md,
      paddingVertical: theme.spacing.sm,
      borderRadius: 20,
      backgroundColor: theme.colors.background,
      borderWidth: 1,
      borderColor: theme.colors.border,
      marginRight: theme.spacing.sm,
    },
    filterChipActive: {
      backgroundColor: theme.colors.primary,
      borderColor: theme.colors.primary,
    },
    filterChipText: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
      marginLeft: theme.spacing.xs,
    },
    filterChipTextActive: {
      color: '#FFFFFF',
    },
  });

  return (
    <View style={styles.container}>
      {renderHeader()}
      
      <View style={styles.content}>
        <FlatList
          style={styles.notificationsList}
          data={notifications}
          keyExtractor={(item) => item.id}
          renderItem={renderNotificationItem}
          ListEmptyComponent={renderEmptyState}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
          }
          showsVerticalScrollIndicator={false}
        />
      </View>
    </View>
  );
};

export default NotificationsScreen;
