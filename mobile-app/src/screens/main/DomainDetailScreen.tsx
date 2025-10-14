/**
 * Domain Detail Screen
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Share,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { useDispatch, useSelector } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { LineChart } from 'react-native-chart-kit';
import Toast from 'react-native-toast-message';

import { RootState, AppDispatch } from '../../store';
import { getDomain, refreshDomainStatus, deleteDomain } from '../../store/slices/domainSlice';
import { useTheme } from '../../hooks/useTheme';
import { formatDate, formatTimeAgo, formatDaysLeft } from '../../utils/dateUtils';
import { Domain } from '../../services/DomainService';

interface RouteParams {
  domainId: number;
}

const DomainDetailScreen: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);
  const [domainHistory, setDomainHistory] = useState<any[]>([]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const route = useRoute();
  const navigation = useNavigation();
  const dispatch = useDispatch<AppDispatch>();
  const theme = useTheme();

  const { domainId } = route.params as RouteParams;
  const { domains, isLoading } = useSelector((state: RootState) => state.domains);
  const domain = domains.find(d => d.id === domainId);

  useEffect(() => {
    if (domainId) {
      loadDomainData();
    }
  }, [domainId]);

  const loadDomainData = async () => {
    try {
      // Load domain details and history
      // This would be implemented in the actual app
      setDomainHistory([]);
    } catch (error) {
      console.error('Error loading domain data:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await dispatch(refreshDomainStatus(domainId)).unwrap();
      await loadDomainData();
    } catch (error) {
      Toast.show({
        type: 'error',
        text1: 'Refresh Failed',
        text2: 'Could not refresh domain status',
      });
    } finally {
      setRefreshing(false);
    }
  };

  const handleDeleteDomain = async () => {
    Alert.alert(
      'Delete Domain',
      `Are you sure you want to delete ${domain?.name}? This action cannot be undone.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await dispatch(deleteDomain(domainId)).unwrap();
              Toast.show({
                type: 'success',
                text1: 'Domain Deleted',
                text2: `${domain?.name} has been removed`,
              });
              navigation.goBack();
            } catch (error) {
              Toast.show({
                type: 'error',
                text1: 'Delete Failed',
                text2: 'Could not delete domain',
              });
            }
          },
        },
      ]
    );
  };

  const handleShare = async () => {
    if (!domain) return;

    const message = `SSL Certificate Status for ${domain.name}:\n` +
      `Status: ${domain.ssl_status?.is_valid ? 'Valid' : 'Invalid'}\n` +
      `Expires: ${formatDaysLeft(domain.ssl_status?.expires_in || 0)}\n` +
      `Last Checked: ${formatTimeAgo(domain.ssl_status?.checked_at || domain.updated_at)}`;

    try {
      await Share.share({
        message,
        title: `SSL Status - ${domain.name}`,
      });
    } catch (error) {
      console.error('Error sharing:', error);
    }
  };

  const getStatusColor = (expiresIn: number) => {
    if (expiresIn <= 0) return theme.colors.error;
    if (expiresIn <= 7) return theme.colors.warning;
    if (expiresIn <= 30) return theme.colors.info;
    return theme.colors.success;
  };

  const getStatusText = (expiresIn: number) => {
    if (expiresIn <= 0) return 'Expired';
    if (expiresIn <= 7) return 'Critical';
    if (expiresIn <= 30) return 'Warning';
    return 'Healthy';
  };

  if (!domain) {
    return (
      <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
        <Text style={[styles.errorText, { color: theme.colors.text }]}>
          Domain not found
        </Text>
      </View>
    );
  }

  const styles = StyleSheet.create({
    container: {
      flex: 1,
    },
    scrollView: {
      flex: 1,
    },
    header: {
      backgroundColor: theme.colors.surface,
      padding: theme.spacing.lg,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    domainName: {
      fontSize: theme.fonts.sizes.xxl,
      fontWeight: 'bold',
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    domainUrl: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.textSecondary,
      marginBottom: theme.spacing.md,
    },
    statusContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      marginBottom: theme.spacing.lg,
    },
    statusBadge: {
      paddingHorizontal: theme.spacing.md,
      paddingVertical: theme.spacing.xs,
      borderRadius: 20,
      marginRight: theme.spacing.md,
    },
    statusText: {
      fontSize: theme.fonts.sizes.sm,
      fontWeight: '600',
      color: '#FFFFFF',
    },
    lastChecked: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
    },
    actionButtons: {
      flexDirection: 'row',
      justifyContent: 'space-between',
    },
    actionButton: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: theme.spacing.md,
      paddingVertical: theme.spacing.sm,
      borderRadius: 8,
      backgroundColor: theme.colors.background,
      borderWidth: 1,
      borderColor: theme.colors.border,
      flex: 1,
      marginHorizontal: theme.spacing.xs,
    },
    actionButtonText: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.text,
      marginLeft: theme.spacing.xs,
    },
    section: {
      padding: theme.spacing.lg,
    },
    sectionTitle: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: theme.colors.text,
      marginBottom: theme.spacing.md,
    },
    infoCard: {
      backgroundColor: theme.colors.surface,
      borderRadius: 12,
      padding: theme.spacing.lg,
      marginBottom: theme.spacing.md,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    infoRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: theme.spacing.sm,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    infoRowLast: {
      borderBottomWidth: 0,
    },
    infoLabel: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.textSecondary,
      flex: 1,
    },
    infoValue: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.text,
      fontWeight: '500',
      flex: 1,
      textAlign: 'right',
    },
    chartContainer: {
      backgroundColor: theme.colors.surface,
      borderRadius: 12,
      padding: theme.spacing.lg,
      marginBottom: theme.spacing.md,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    chartTitle: {
      fontSize: theme.fonts.sizes.md,
      fontWeight: '600',
      color: theme.colors.text,
      marginBottom: theme.spacing.md,
      textAlign: 'center',
    },
    deleteButton: {
      backgroundColor: theme.colors.error,
      borderRadius: 8,
      paddingVertical: theme.spacing.md,
      paddingHorizontal: theme.spacing.lg,
      alignItems: 'center',
      margin: theme.spacing.lg,
    },
    deleteButtonText: {
      color: '#FFFFFF',
      fontSize: theme.fonts.sizes.md,
      fontWeight: '600',
    },
    errorText: {
      textAlign: 'center',
      marginTop: theme.spacing.xxl,
      fontSize: theme.fonts.sizes.lg,
    },
  });

  const chartConfig = {
    backgroundColor: theme.colors.background,
    backgroundGradientFrom: theme.colors.background,
    backgroundGradientTo: theme.colors.background,
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
    labelColor: (opacity = 1) => theme.colors.text,
    style: {
      borderRadius: 16,
    },
  };

  // Mock chart data - in real app, this would come from domain history
  const chartData = {
    labels: ['7d ago', '6d ago', '5d ago', '4d ago', '3d ago', '2d ago', '1d ago'],
    datasets: [
      {
        data: [90, 89, 88, 87, 86, 85, domain.ssl_status?.expires_in || 84],
        color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <View style={styles.header}>
          <Text style={styles.domainName}>{domain.name}</Text>
          <Text style={styles.domainUrl}>https://{domain.name}</Text>
          
          <View style={styles.statusContainer}>
            <View
              style={[
                styles.statusBadge,
                { backgroundColor: getStatusColor(domain.ssl_status?.expires_in || 0) },
              ]}
            >
              <Text style={styles.statusText}>
                {getStatusText(domain.ssl_status?.expires_in || 0)}
              </Text>
            </View>
            <Text style={styles.lastChecked}>
              Last checked: {formatTimeAgo(domain.ssl_status?.checked_at || domain.updated_at)}
            </Text>
          </View>

          <View style={styles.actionButtons}>
            <TouchableOpacity style={styles.actionButton} onPress={onRefresh}>
              <Icon name="refresh" size={20} color={theme.colors.primary} />
              <Text style={styles.actionButtonText}>Refresh</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.actionButton} onPress={handleShare}>
              <Icon name="share" size={20} color={theme.colors.primary} />
              <Text style={styles.actionButtonText}>Share</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>SSL Certificate Information</Text>
          
          <View style={styles.infoCard}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Status</Text>
              <Text style={[styles.infoValue, { color: getStatusColor(domain.ssl_status?.expires_in || 0) }]}>
                {domain.ssl_status?.is_valid ? 'Valid' : 'Invalid'}
              </Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Days Until Expiry</Text>
              <Text style={[styles.infoValue, { color: getStatusColor(domain.ssl_status?.expires_in || 0) }]}>
                {domain.ssl_status?.expires_in || 'Unknown'}
              </Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Issuer</Text>
              <Text style={styles.infoValue}>
                {domain.ssl_status?.issuer || 'Unknown'}
              </Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Subject</Text>
              <Text style={styles.infoValue}>
                {domain.ssl_status?.subject || 'Unknown'}
              </Text>
            </View>
            <View style={[styles.infoRow, styles.infoRowLast]}>
              <Text style={styles.infoLabel}>Expires On</Text>
              <Text style={styles.infoValue}>
                {domain.ssl_status?.not_valid_after 
                  ? formatDate(domain.ssl_status.not_valid_after)
                  : 'Unknown'
                }
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Certificate History</Text>
          
          <View style={styles.chartContainer}>
            <Text style={styles.chartTitle}>Days Until Expiry (Last 7 Days)</Text>
            <LineChart
              data={chartData}
              width={300}
              height={200}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Domain Settings</Text>
          
          <View style={styles.infoCard}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Alert Threshold</Text>
              <Text style={styles.infoValue}>
                {domain.alert_threshold_days} days
              </Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Status</Text>
              <Text style={styles.infoValue}>
                {domain.is_active ? 'Active' : 'Inactive'}
              </Text>
            </View>
            <View style={[styles.infoRow, styles.infoRowLast]}>
              <Text style={styles.infoLabel}>Added On</Text>
              <Text style={styles.infoValue}>
                {formatDate(domain.created_at)}
              </Text>
            </View>
          </View>
        </View>

        <TouchableOpacity style={styles.deleteButton} onPress={handleDeleteDomain}>
          <Text style={styles.deleteButtonText}>Delete Domain</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
};

export default DomainDetailScreen;
