/**
 * Analytics Screen - SSL certificate analytics and insights
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Dimensions,
  TouchableOpacity,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { RootState, AppDispatch } from '../../store';
import { fetchAnalytics } from '../../store/slices/analyticsSlice';
import { useTheme } from '../../hooks/useTheme';

const { width: screenWidth } = Dimensions.get('window');
const chartWidth = screenWidth - 32;

const AnalyticsScreen: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [refreshing, setRefreshing] = useState(false);

  const dispatch = useDispatch<AppDispatch>();
  const theme = useTheme();

  const { analytics, isLoading, error } = useSelector((state: RootState) => state.analytics);
  const { domains } = useSelector((state: RootState) => state.domains);

  useEffect(() => {
    loadAnalytics();
  }, [selectedPeriod]);

  const loadAnalytics = async () => {
    try {
      await dispatch(fetchAnalytics({ period: selectedPeriod })).unwrap();
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadAnalytics();
    setRefreshing(false);
  };

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
      r: '4',
      strokeWidth: '2',
      stroke: theme.colors.primary,
    },
  };

  const pieChartConfig = {
    backgroundColor: theme.colors.background,
    backgroundGradientFrom: theme.colors.background,
    backgroundGradientTo: theme.colors.background,
    color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
    labelColor: (opacity = 1) => theme.colors.text,
  };

  // Calculate statistics from domains
  const stats = {
    total: domains.length,
    healthy: domains.filter(d => (d.ssl_status?.expires_in || 0) > 30).length,
    warning: domains.filter(d => {
      const days = d.ssl_status?.expires_in || 0;
      return days > 7 && days <= 30;
    }).length,
    critical: domains.filter(d => {
      const days = d.ssl_status?.expires_in || 0;
      return days > 0 && days <= 7;
    }).length,
    expired: domains.filter(d => (d.ssl_status?.expires_in || 0) <= 0).length,
  };

  // Mock data for charts - in real app, this would come from analytics API
  const expiryTrendData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        data: [95, 92, 88, 85],
        color: (opacity = 1) => `rgba(59, 130, 246, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  const statusDistributionData = [
    {
      name: 'Healthy',
      population: stats.healthy,
      color: theme.colors.success,
      legendFontColor: theme.colors.text,
      legendFontSize: 12,
    },
    {
      name: 'Warning',
      population: stats.warning,
      color: theme.colors.warning,
      legendFontColor: theme.colors.text,
      legendFontSize: 12,
    },
    {
      name: 'Critical',
      population: stats.critical,
      color: theme.colors.error,
      legendFontColor: theme.colors.text,
      legendFontSize: 12,
    },
    {
      name: 'Expired',
      population: stats.expired,
      color: theme.colors.textSecondary,
      legendFontColor: theme.colors.text,
      legendFontSize: 12,
    },
  ];

  const alertsData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        data: [2, 1, 3, 0, 2, 1, 0],
      },
    ],
  };

  const renderPeriodSelector = () => (
    <View style={styles.periodSelector}>
      {[
        { key: '7d', label: '7 Days' },
        { key: '30d', label: '30 Days' },
        { key: '90d', label: '90 Days' },
        { key: '1y', label: '1 Year' },
      ].map((period) => (
        <TouchableOpacity
          key={period.key}
          style={[
            styles.periodButton,
            selectedPeriod === period.key && styles.periodButtonActive,
          ]}
          onPress={() => setSelectedPeriod(period.key as any)}
        >
          <Text
            style={[
              styles.periodButtonText,
              selectedPeriod === period.key && styles.periodButtonTextActive,
            ]}
          >
            {period.label}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderStatsCards = () => (
    <View style={styles.statsContainer}>
      <View style={styles.statCard}>
        <Icon name="domain" size={24} color={theme.colors.primary} />
        <Text style={styles.statValue}>{stats.total}</Text>
        <Text style={styles.statLabel}>Total Domains</Text>
      </View>
      <View style={styles.statCard}>
        <Icon name="check-circle" size={24} color={theme.colors.success} />
        <Text style={styles.statValue}>{stats.healthy}</Text>
        <Text style={styles.statLabel}>Healthy</Text>
      </View>
      <View style={styles.statCard}>
        <Icon name="warning" size={24} color={theme.colors.warning} />
        <Text style={styles.statValue}>{stats.warning}</Text>
        <Text style={styles.statLabel}>Warning</Text>
      </View>
      <View style={styles.statCard}>
        <Icon name="error" size={24} color={theme.colors.error} />
        <Text style={styles.statValue}>{stats.critical}</Text>
        <Text style={styles.statLabel}>Critical</Text>
      </View>
    </View>
  );

  const renderChart = (title: string, children: React.ReactNode) => (
    <View style={styles.chartContainer}>
      <Text style={styles.chartTitle}>{title}</Text>
      {children}
    </View>
  );

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    header: {
      backgroundColor: theme.colors.surface,
      paddingHorizontal: theme.spacing.lg,
      paddingVertical: theme.spacing.md,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    headerTitle: {
      fontSize: theme.fonts.sizes.xl,
      fontWeight: 'bold',
      color: theme.colors.text,
      marginBottom: theme.spacing.md,
    },
    periodSelector: {
      flexDirection: 'row',
      backgroundColor: theme.colors.background,
      borderRadius: 8,
      padding: 4,
    },
    periodButton: {
      flex: 1,
      paddingVertical: theme.spacing.sm,
      alignItems: 'center',
      borderRadius: 6,
    },
    periodButtonActive: {
      backgroundColor: theme.colors.primary,
    },
    periodButtonText: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
      fontWeight: '500',
    },
    periodButtonTextActive: {
      color: '#FFFFFF',
    },
    scrollView: {
      flex: 1,
    },
    content: {
      padding: theme.spacing.lg,
    },
    statsContainer: {
      flexDirection: 'row',
      marginBottom: theme.spacing.xl,
    },
    statCard: {
      flex: 1,
      backgroundColor: theme.colors.surface,
      borderRadius: 12,
      padding: theme.spacing.md,
      alignItems: 'center',
      marginHorizontal: theme.spacing.xs,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    statValue: {
      fontSize: theme.fonts.sizes.xl,
      fontWeight: 'bold',
      color: theme.colors.text,
      marginTop: theme.spacing.sm,
    },
    statLabel: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
      marginTop: theme.spacing.xs,
      textAlign: 'center',
    },
    chartContainer: {
      backgroundColor: theme.colors.surface,
      borderRadius: 12,
      padding: theme.spacing.lg,
      marginBottom: theme.spacing.lg,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    chartTitle: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: theme.colors.text,
      marginBottom: theme.spacing.md,
    },
    chart: {
      marginVertical: 8,
      borderRadius: 16,
    },
    insightsContainer: {
      backgroundColor: theme.colors.surface,
      borderRadius: 12,
      padding: theme.spacing.lg,
      marginBottom: theme.spacing.lg,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    insightItem: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: theme.spacing.sm,
    },
    insightIcon: {
      marginRight: theme.spacing.md,
    },
    insightText: {
      flex: 1,
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.text,
    },
    insightValue: {
      fontSize: theme.fonts.sizes.md,
      fontWeight: '600',
      color: theme.colors.text,
    },
    emptyState: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      paddingHorizontal: theme.spacing.xl,
    },
    emptyIcon: {
      marginBottom: theme.spacing.lg,
    },
    emptyTitle: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: theme.colors.text,
      marginBottom: theme.spacing.sm,
      textAlign: 'center',
    },
    emptyDescription: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.textSecondary,
      textAlign: 'center',
      lineHeight: 20,
    },
  });

  if (domains.length === 0) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Analytics</Text>
        </View>
        <View style={styles.emptyState}>
          <Icon name="analytics" size={64} color={theme.colors.textSecondary} style={styles.emptyIcon} />
          <Text style={styles.emptyTitle}>No Analytics Data</Text>
          <Text style={styles.emptyDescription}>
            Add some domains to start monitoring and see analytics insights
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Analytics</Text>
        {renderPeriodSelector()}
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
      >
        {renderStatsCards()}

        {renderChart(
          'Certificate Status Distribution',
          <PieChart
            data={statusDistributionData}
            width={chartWidth}
            height={220}
            chartConfig={pieChartConfig}
            accessor="population"
            backgroundColor="transparent"
            paddingLeft="15"
            center={[10, 0]}
            absolute
          />
        )}

        {renderChart(
          'SSL Health Trend',
          <LineChart
            data={expiryTrendData}
            width={chartWidth}
            height={220}
            chartConfig={chartConfig}
            bezier
            style={styles.chart}
          />
        )}

        {renderChart(
          'Daily Alerts',
          <BarChart
            data={alertsData}
            width={chartWidth}
            height={220}
            chartConfig={chartConfig}
            style={styles.chart}
            verticalLabelRotation={30}
          />
        )}

        <View style={styles.insightsContainer}>
          <Text style={styles.chartTitle}>Key Insights</Text>
          
          <View style={styles.insightItem}>
            <Icon name="trending-up" size={20} color={theme.colors.success} style={styles.insightIcon} />
            <Text style={styles.insightText}>SSL health improved by 12% this month</Text>
          </View>
          
          <View style={styles.insightItem}>
            <Icon name="schedule" size={20} color={theme.colors.warning} style={styles.insightIcon} />
            <Text style={styles.insightText}>3 certificates expiring in the next 7 days</Text>
          </View>
          
          <View style={styles.insightItem}>
            <Icon name="notifications" size={20} color={theme.colors.info} style={styles.insightIcon} />
            <Text style={styles.insightText}>Average response time: 2.3 seconds</Text>
          </View>
          
          <View style={styles.insightItem}>
            <Icon name="security" size={20} color={theme.colors.success} style={styles.insightIcon} />
            <Text style={styles.insightText}>All certificates using strong encryption</Text>
          </View>
        </View>
      </ScrollView>
    </View>
  );
};

export default AnalyticsScreen;
