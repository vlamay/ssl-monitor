/**
 * Dashboard Screen
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigation } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { LineChart, BarChart } from 'react-native-chart-kit';

import { RootState, AppDispatch } from '../../store';
import { fetchDomains, refreshDomainStatus } from '../../store/slices/domainSlice';
import { useTheme } from '../../hooks/useTheme';
import { DomainService } from '../../services/DomainService';
import { formatDate, formatTimeAgo } from '../../utils/dateUtils';

const { width } = Dimensions.get('window');

const DashboardScreen: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    totalDomains: 0,
    activeDomains: 0,
    expiringSoon: 0,
    expired: 0,
    healthy: 0,
  });

  const dispatch = useDispatch<AppDispatch>();
  const navigation = useNavigation();
  const theme = useTheme();

  const { domains, isLoading } = useSelector((state: RootState) => state.domains);
  const { user } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      await dispatch(fetchDomains()).unwrap();
      const statistics = await DomainService.getStatistics();
      setStats(statistics);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const refreshDomain = async (domainId: number) => {
    try {
      await dispatch(refreshDomainStatus(domainId)).unwrap();
    } catch (error) {
      console.error('Error refreshing domain:', error);
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

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    scrollView: {
      flex: 1,
    },
    header: {
      padding: theme.spacing.lg,
      backgroundColor: theme.colors.surface,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    welcomeText: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    subtitle: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.textSecondary,
    },
    statsContainer: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      padding: theme.spacing.lg,
      justifyContent: 'space-between',
    },
    statCard: {
      width: (width - theme.spacing.lg * 3) / 2,
      backgroundColor: theme.colors.surface,
      borderRadius: 12,
      padding: theme.spacing.lg,
      marginBottom: theme.spacing.md,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    statValue: {
      fontSize: theme.fonts.sizes.xxl,
      fontWeight: 'bold',
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    statLabel: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
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
    domainCard: {
      backgroundColor: theme.colors.surface,
      borderRadius: 12,
      padding: theme.spacing.lg,
      marginBottom: theme.spacing.md,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    domainHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: theme.spacing.sm,
    },
    domainName: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: theme.colors.text,
      flex: 1,
    },
    statusBadge: {
      paddingHorizontal: theme.spacing.sm,
      paddingVertical: theme.spacing.xs,
      borderRadius: 6,
    },
    statusText: {
      fontSize: theme.fonts.sizes.xs,
      fontWeight: '600',
      color: '#FFFFFF',
    },
    domainInfo: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    expiresText: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
    },
    refreshButton: {
      padding: theme.spacing.xs,
    },
    addButton: {
      position: 'absolute',
      bottom: theme.spacing.xl,
      right: theme.spacing.lg,
      width: 56,
      height: 56,
      borderRadius: 28,
      backgroundColor: theme.colors.primary,
      justifyContent: 'center',
      alignItems: 'center',
      elevation: 4,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.25,
      shadowRadius: 4,
    },
    emptyState: {
      alignItems: 'center',
      padding: theme.spacing.xxl,
    },
    emptyIcon: {
      marginBottom: theme.spacing.lg,
    },
    emptyText: {
      fontSize: theme.fonts.sizes.lg,
      color: theme.colors.textSecondary,
      textAlign: 'center',
      marginBottom: theme.spacing.md,
    },
    emptySubtext: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.textSecondary,
      textAlign: 'center',
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
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: theme.colors.primary,
    },
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
          <Text style={styles.welcomeText}>
            Welcome back, {user?.name || user?.email}!
          </Text>
          <Text style={styles.subtitle}>
            Monitor your SSL certificates
          </Text>
        </View>

        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{stats.totalDomains}</Text>
            <Text style={styles.statLabel}>Total Domains</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={[styles.statValue, { color: theme.colors.success }]}>
              {stats.healthy}
            </Text>
            <Text style={styles.statLabel}>Healthy</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={[styles.statValue, { color: theme.colors.warning }]}>
              {stats.expiringSoon}
            </Text>
            <Text style={styles.statLabel}>Expiring Soon</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={[styles.statValue, { color: theme.colors.error }]}>
              {stats.expired}
            </Text>
            <Text style={styles.statLabel}>Expired</Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Domains</Text>
          
          {domains.length === 0 ? (
            <View style={styles.emptyState}>
              <Icon
                name="domain"
                size={64}
                color={theme.colors.textSecondary}
                style={styles.emptyIcon}
              />
              <Text style={styles.emptyText}>No domains yet</Text>
              <Text style={styles.emptySubtext}>
                Add your first domain to start monitoring SSL certificates
              </Text>
            </View>
          ) : (
            domains.slice(0, 5).map((domain) => (
              <TouchableOpacity
                key={domain.id}
                style={styles.domainCard}
                onPress={() => navigation.navigate('DomainDetail', { domainId: domain.id } as never)}
              >
                <View style={styles.domainHeader}>
                  <Text style={styles.domainName}>{domain.name}</Text>
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
                </View>
                <View style={styles.domainInfo}>
                  <Text style={styles.expiresText}>
                    {domain.ssl_status?.expires_in
                      ? `${domain.ssl_status.expires_in} days left`
                      : 'Not checked'}
                  </Text>
                  <TouchableOpacity
                    style={styles.refreshButton}
                    onPress={() => refreshDomain(domain.id)}
                  >
                    <Icon
                      name="refresh"
                      size={20}
                      color={theme.colors.primary}
                    />
                  </TouchableOpacity>
                </View>
              </TouchableOpacity>
            ))
          )}
        </View>
      </ScrollView>

      <TouchableOpacity
        style={styles.addButton}
        onPress={() => navigation.navigate('AddDomain' as never)}
      >
        <Icon name="add" size={24} color="#FFFFFF" />
      </TouchableOpacity>
    </View>
  );
};

export default DashboardScreen;
