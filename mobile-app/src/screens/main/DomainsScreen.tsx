/**
 * Domains Screen - List of monitored domains
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
  TextInput,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useDispatch, useSelector } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { RootState, AppDispatch } from '../../store';
import { fetchDomains, refreshDomainStatus } from '../../store/slices/domainSlice';
import { useTheme } from '../../hooks/useTheme';
import { formatDaysLeft, formatTimeAgo } from '../../utils/dateUtils';
import { Domain } from '../../services/DomainService';

const DomainsScreen: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'healthy' | 'warning' | 'critical' | 'expired'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'expiry' | 'status'>('expiry');

  const navigation = useNavigation();
  const dispatch = useDispatch<AppDispatch>();
  const theme = useTheme();

  const { domains, isLoading, error } = useSelector((state: RootState) => state.domains);

  useEffect(() => {
    loadDomains();
  }, []);

  const loadDomains = async () => {
    try {
      await dispatch(fetchDomains()).unwrap();
    } catch (error) {
      console.error('Error loading domains:', error);
    }
  };

  const handleRefresh = async () => {
    await loadDomains();
  };

  const handleRefreshDomain = async (domainId: number) => {
    try {
      await dispatch(refreshDomainStatus(domainId)).unwrap();
    } catch (error) {
      Alert.alert('Error', 'Failed to refresh domain status');
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

  const getStatusIcon = (expiresIn: number) => {
    if (expiresIn <= 0) return 'error';
    if (expiresIn <= 7) return 'warning';
    if (expiresIn <= 30) return 'info';
    return 'check-circle';
  };

  const filteredDomains = domains
    .filter((domain) => {
      // Search filter
      if (searchQuery && !domain.name.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }

      // Status filter
      if (filterStatus !== 'all') {
        const expiresIn = domain.ssl_status?.expires_in || 0;
        const status = getStatusText(expiresIn).toLowerCase();
        if (status !== filterStatus) {
          return false;
        }
      }

      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'expiry':
          return (a.ssl_status?.expires_in || 0) - (b.ssl_status?.expires_in || 0);
        case 'status':
          const aStatus = getStatusText(a.ssl_status?.expires_in || 0);
          const bStatus = getStatusText(b.ssl_status?.expires_in || 0);
          return aStatus.localeCompare(bStatus);
        default:
          return 0;
      }
    });

  const renderDomainItem = ({ item }: { item: Domain }) => {
    const expiresIn = item.ssl_status?.expires_in || 0;
    const statusColor = getStatusColor(expiresIn);
    const statusText = getStatusText(expiresIn);
    const statusIcon = getStatusIcon(expiresIn);

    return (
      <TouchableOpacity
        style={styles.domainCard}
        onPress={() => navigation.navigate('DomainDetail' as never, { domainId: item.id } as never)}
        activeOpacity={0.7}
      >
        <View style={styles.domainHeader}>
          <View style={styles.domainInfo}>
            <Text style={styles.domainName}>{item.name}</Text>
            <View style={styles.statusContainer}>
              <Icon name={statusIcon} size={16} color={statusColor} />
              <Text style={[styles.statusText, { color: statusColor }]}>
                {statusText}
              </Text>
            </View>
          </View>
          <TouchableOpacity
            onPress={() => handleRefreshDomain(item.id)}
            style={styles.refreshButton}
          >
            <Icon name="refresh" size={20} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>

        <View style={styles.domainDetails}>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Expires in:</Text>
            <Text style={[styles.detailValue, { color: statusColor }]}>
              {formatDaysLeft(expiresIn)}
            </Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Alert threshold:</Text>
            <Text style={styles.detailValue}>{item.alert_threshold_days} days</Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Last checked:</Text>
            <Text style={styles.detailValue}>
              {formatTimeAgo(item.ssl_status?.checked_at || item.updated_at)}
            </Text>
          </View>
        </View>

        <View style={styles.domainFooter}>
          <View style={styles.domainMeta}>
            <Icon name="domain" size={14} color={theme.colors.textSecondary} />
            <Text style={styles.metaText}>
              {item.is_active ? 'Active' : 'Inactive'}
            </Text>
          </View>
          <Icon name="chevron-right" size={20} color={theme.colors.textSecondary} />
        </View>
      </TouchableOpacity>
    );
  };

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Icon name="domain-disabled" size={64} color={theme.colors.textSecondary} />
      <Text style={styles.emptyTitle}>No domains found</Text>
      <Text style={styles.emptyDescription}>
        {searchQuery || filterStatus !== 'all'
          ? 'Try adjusting your search or filters'
          : 'Add your first domain to start monitoring SSL certificates'
        }
      </Text>
      {!searchQuery && filterStatus === 'all' && (
        <TouchableOpacity
          style={styles.addFirstButton}
          onPress={() => navigation.navigate('AddDomain' as never)}
        >
          <Icon name="add" size={20} color="#FFFFFF" />
          <Text style={styles.addFirstButtonText}>Add First Domain</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  const renderFilterChips = () => (
    <View style={styles.filterContainer}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        {[
          { key: 'all', label: 'All', icon: 'list' },
          { key: 'healthy', label: 'Healthy', icon: 'check-circle' },
          { key: 'warning', label: 'Warning', icon: 'info' },
          { key: 'critical', label: 'Critical', icon: 'warning' },
          { key: 'expired', label: 'Expired', icon: 'error' },
        ].map((filter) => (
          <TouchableOpacity
            key={filter.key}
            style={[
              styles.filterChip,
              filterStatus === filter.key && styles.filterChipActive,
            ]}
            onPress={() => setFilterStatus(filter.key as any)}
          >
            <Icon
              name={filter.icon as any}
              size={16}
              color={filterStatus === filter.key ? '#FFFFFF' : theme.colors.textSecondary}
            />
            <Text
              style={[
                styles.filterChipText,
                filterStatus === filter.key && styles.filterChipTextActive,
              ]}
            >
              {filter.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
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
    headerTop: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: theme.spacing.md,
    },
    headerTitle: {
      fontSize: theme.fonts.sizes.xl,
      fontWeight: 'bold',
      color: theme.colors.text,
    },
    addButton: {
      backgroundColor: theme.colors.primary,
      borderRadius: 20,
      width: 40,
      height: 40,
      justifyContent: 'center',
      alignItems: 'center',
    },
    searchContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: theme.colors.background,
      borderRadius: 8,
      paddingHorizontal: theme.spacing.md,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    searchInput: {
      flex: 1,
      paddingVertical: theme.spacing.sm,
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.text,
    },
    searchIcon: {
      marginRight: theme.spacing.sm,
    },
    clearButton: {
      padding: theme.spacing.xs,
    },
    content: {
      flex: 1,
    },
    filterContainer: {
      paddingVertical: theme.spacing.md,
      paddingHorizontal: theme.spacing.lg,
    },
    filterChip: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: theme.spacing.md,
      paddingVertical: theme.spacing.sm,
      borderRadius: 20,
      backgroundColor: theme.colors.surface,
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
    domainsList: {
      flex: 1,
      paddingHorizontal: theme.spacing.lg,
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
      alignItems: 'flex-start',
      marginBottom: theme.spacing.md,
    },
    domainInfo: {
      flex: 1,
    },
    domainName: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    statusContainer: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    statusText: {
      fontSize: theme.fonts.sizes.sm,
      fontWeight: '500',
      marginLeft: theme.spacing.xs,
    },
    refreshButton: {
      padding: theme.spacing.xs,
    },
    domainDetails: {
      marginBottom: theme.spacing.md,
    },
    detailRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: theme.spacing.xs,
    },
    detailLabel: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
    },
    detailValue: {
      fontSize: theme.fonts.sizes.sm,
      fontWeight: '500',
      color: theme.colors.text,
    },
    domainFooter: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingTop: theme.spacing.sm,
      borderTopWidth: 1,
      borderTopColor: theme.colors.border,
    },
    domainMeta: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    metaText: {
      fontSize: theme.fonts.sizes.xs,
      color: theme.colors.textSecondary,
      marginLeft: theme.spacing.xs,
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
      marginBottom: theme.spacing.xl,
    },
    addFirstButton: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: theme.colors.primary,
      paddingHorizontal: theme.spacing.lg,
      paddingVertical: theme.spacing.md,
      borderRadius: 8,
    },
    addFirstButtonText: {
      fontSize: theme.fonts.sizes.md,
      fontWeight: '600',
      color: '#FFFFFF',
      marginLeft: theme.spacing.sm,
    },
    statsContainer: {
      flexDirection: 'row',
      paddingHorizontal: theme.spacing.lg,
      paddingVertical: theme.spacing.md,
      backgroundColor: theme.colors.surface,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    statItem: {
      flex: 1,
      alignItems: 'center',
    },
    statValue: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: 'bold',
      color: theme.colors.text,
    },
    statLabel: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
      marginTop: theme.spacing.xs,
    },
  });

  const stats = {
    total: domains.length,
    healthy: domains.filter(d => getStatusText(d.ssl_status?.expires_in || 0) === 'Healthy').length,
    warning: domains.filter(d => getStatusText(d.ssl_status?.expires_in || 0) === 'Warning').length,
    critical: domains.filter(d => getStatusText(d.ssl_status?.expires_in || 0) === 'Critical').length,
    expired: domains.filter(d => getStatusText(d.ssl_status?.expires_in || 0) === 'Expired').length,
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <Text style={styles.headerTitle}>Domains</Text>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => navigation.navigate('AddDomain' as never)}
          >
            <Icon name="add" size={24} color="#FFFFFF" />
          </TouchableOpacity>
        </View>

        <View style={styles.searchContainer}>
          <Icon name="search" size={20} color={theme.colors.textSecondary} style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search domains..."
            placeholderTextColor={theme.colors.textSecondary}
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity
              style={styles.clearButton}
              onPress={() => setSearchQuery('')}
            >
              <Icon name="clear" size={20} color={theme.colors.textSecondary} />
            </TouchableOpacity>
          )}
        </View>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{stats.total}</Text>
          <Text style={styles.statLabel}>Total</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={[styles.statValue, { color: theme.colors.success }]}>{stats.healthy}</Text>
          <Text style={styles.statLabel}>Healthy</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={[styles.statValue, { color: theme.colors.warning }]}>{stats.warning}</Text>
          <Text style={styles.statLabel}>Warning</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={[styles.statValue, { color: theme.colors.error }]}>{stats.critical}</Text>
          <Text style={styles.statLabel}>Critical</Text>
        </View>
      </View>

      <View style={styles.content}>
        {renderFilterChips()}
        
        <FlatList
          style={styles.domainsList}
          data={filteredDomains}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderDomainItem}
          ListEmptyComponent={renderEmptyState}
          refreshControl={
            <RefreshControl refreshing={isLoading} onRefresh={handleRefresh} />
          }
          showsVerticalScrollIndicator={false}
        />
      </View>
    </View>
  );
};

export default DomainsScreen;
