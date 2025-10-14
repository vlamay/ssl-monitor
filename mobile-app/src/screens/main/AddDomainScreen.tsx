/**
 * Add Domain Screen
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useDispatch } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Toast from 'react-native-toast-message';

import { AppDispatch } from '../../store';
import { addDomain } from '../../store/slices/domainSlice';
import { useTheme } from '../../hooks/useTheme';

const AddDomainScreen: React.FC = () => {
  const [domainName, setDomainName] = useState('');
  const [alertThreshold, setAlertThreshold] = useState('30');
  const [isLoading, setIsLoading] = useState(false);

  const navigation = useNavigation();
  const dispatch = useDispatch<AppDispatch>();
  const theme = useTheme();

  const validateDomain = (domain: string): boolean => {
    // Basic domain validation regex
    const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?(\.[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?)*$/;
    return domainRegex.test(domain);
  };

  const handleAddDomain = async () => {
    // Validation
    if (!domainName.trim()) {
      Alert.alert('Error', 'Please enter a domain name');
      return;
    }

    if (!validateDomain(domainName.trim())) {
      Alert.alert('Error', 'Please enter a valid domain name');
      return;
    }

    const threshold = parseInt(alertThreshold);
    if (isNaN(threshold) || threshold < 1 || threshold > 365) {
      Alert.alert('Error', 'Alert threshold must be between 1 and 365 days');
      return;
    }

    setIsLoading(true);

    try {
      const domainData = {
        name: domainName.trim(),
        alert_threshold_days: threshold,
      };

      await dispatch(addDomain(domainData)).unwrap();

      Toast.show({
        type: 'success',
        text1: 'Domain Added',
        text2: `${domainName} has been added successfully`,
      });

      // Navigate back to domains list
      navigation.goBack();
    } catch (error: any) {
      Toast.show({
        type: 'error',
        text1: 'Add Domain Failed',
        text2: error.message || 'Could not add domain',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    if (domainName.trim() || alertThreshold !== '30') {
      Alert.alert(
        'Discard Changes',
        'Are you sure you want to discard your changes?',
        [
          { text: 'Keep Editing', style: 'cancel' },
          { text: 'Discard', style: 'destructive', onPress: () => navigation.goBack() },
        ]
      );
    } else {
      navigation.goBack();
    }
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    header: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingHorizontal: theme.spacing.lg,
      paddingVertical: theme.spacing.md,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
      backgroundColor: theme.colors.surface,
    },
    headerTitle: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: theme.colors.text,
    },
    cancelButton: {
      paddingVertical: theme.spacing.sm,
      paddingHorizontal: theme.spacing.md,
    },
    cancelButtonText: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.primary,
    },
    content: {
      flex: 1,
      padding: theme.spacing.lg,
    },
    form: {
      flex: 1,
    },
    section: {
      marginBottom: theme.spacing.xl,
    },
    sectionTitle: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: theme.colors.text,
      marginBottom: theme.spacing.md,
    },
    sectionDescription: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
      marginBottom: theme.spacing.lg,
      lineHeight: 20,
    },
    inputGroup: {
      marginBottom: theme.spacing.lg,
    },
    label: {
      fontSize: theme.fonts.sizes.md,
      fontWeight: '500',
      color: theme.colors.text,
      marginBottom: theme.spacing.sm,
    },
    required: {
      color: theme.colors.error,
    },
    input: {
      borderWidth: 1,
      borderColor: theme.colors.border,
      borderRadius: 8,
      paddingHorizontal: theme.spacing.md,
      paddingVertical: theme.spacing.md,
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.text,
      backgroundColor: theme.colors.surface,
    },
    inputFocused: {
      borderColor: theme.colors.primary,
      borderWidth: 2,
    },
    inputError: {
      borderColor: theme.colors.error,
    },
    inputHint: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
      marginTop: theme.spacing.xs,
    },
    errorText: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.error,
      marginTop: theme.spacing.xs,
    },
    exampleDomains: {
      marginTop: theme.spacing.md,
    },
    exampleTitle: {
      fontSize: theme.fonts.sizes.sm,
      fontWeight: '500',
      color: theme.colors.textSecondary,
      marginBottom: theme.spacing.sm,
    },
    exampleItem: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingVertical: theme.spacing.xs,
    },
    exampleIcon: {
      marginRight: theme.spacing.sm,
    },
    exampleText: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
    },
    thresholdContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      marginTop: theme.spacing.md,
    },
    thresholdButton: {
      paddingHorizontal: theme.spacing.md,
      paddingVertical: theme.spacing.sm,
      borderRadius: 6,
      borderWidth: 1,
      borderColor: theme.colors.border,
      backgroundColor: theme.colors.surface,
      marginHorizontal: theme.spacing.xs,
    },
    thresholdButtonActive: {
      backgroundColor: theme.colors.primary,
      borderColor: theme.colors.primary,
    },
    thresholdButtonText: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.text,
    },
    thresholdButtonTextActive: {
      color: '#FFFFFF',
    },
    addButton: {
      backgroundColor: theme.colors.primary,
      borderRadius: 8,
      paddingVertical: theme.spacing.lg,
      alignItems: 'center',
      marginTop: theme.spacing.xl,
    },
    addButtonDisabled: {
      backgroundColor: theme.colors.textSecondary,
    },
    addButtonText: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: '#FFFFFF',
    },
    addButtonLoading: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    loadingText: {
      marginLeft: theme.spacing.sm,
    },
  });

  const commonDomains = ['example.com', 'google.com', 'github.com', 'stackoverflow.com'];
  const thresholdOptions = [7, 14, 30, 60, 90];

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.header}>
        <TouchableOpacity style={styles.cancelButton} onPress={handleCancel}>
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Add Domain</Text>
        <View style={{ width: 60 }} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.form}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Domain Information</Text>
            <Text style={styles.sectionDescription}>
              Enter the domain name you want to monitor. We'll check the SSL certificate status and notify you when it's about to expire.
            </Text>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>
                Domain Name <Text style={styles.required}>*</Text>
              </Text>
              <TextInput
                style={styles.input}
                value={domainName}
                onChangeText={setDomainName}
                placeholder="example.com"
                placeholderTextColor={theme.colors.textSecondary}
                autoCapitalize="none"
                autoCorrect={false}
                keyboardType="url"
                returnKeyType="next"
              />
              <Text style={styles.inputHint}>
                Enter domain name without https:// or www.
              </Text>

              <View style={styles.exampleDomains}>
                <Text style={styles.exampleTitle}>Examples:</Text>
                {commonDomains.map((domain) => (
                  <TouchableOpacity
                    key={domain}
                    style={styles.exampleItem}
                    onPress={() => setDomainName(domain)}
                  >
                    <Icon
                      name="domain"
                      size={16}
                      color={theme.colors.textSecondary}
                      style={styles.exampleIcon}
                    />
                    <Text style={styles.exampleText}>{domain}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Alert Settings</Text>
            <Text style={styles.sectionDescription}>
              Choose when you want to receive notifications before the SSL certificate expires.
            </Text>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>
                Alert Threshold (Days) <Text style={styles.required}>*</Text>
              </Text>
              <TextInput
                style={styles.input}
                value={alertThreshold}
                onChangeText={setAlertThreshold}
                placeholder="30"
                placeholderTextColor={theme.colors.textSecondary}
                keyboardType="numeric"
                returnKeyType="done"
              />
              <Text style={styles.inputHint}>
                Number of days before expiry to send alerts (1-365)
              </Text>

              <View style={styles.thresholdContainer}>
                <Text style={[styles.label, { marginBottom: 0, marginRight: theme.spacing.md }]}>
                  Quick Select:
                </Text>
                {thresholdOptions.map((days) => (
                  <TouchableOpacity
                    key={days}
                    style={[
                      styles.thresholdButton,
                      alertThreshold === days.toString() && styles.thresholdButtonActive,
                    ]}
                    onPress={() => setAlertThreshold(days.toString())}
                  >
                    <Text
                      style={[
                        styles.thresholdButtonText,
                        alertThreshold === days.toString() && styles.thresholdButtonTextActive,
                      ]}
                    >
                      {days}d
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          </View>
        </View>
      </ScrollView>

      <View style={{ padding: theme.spacing.lg }}>
        <TouchableOpacity
          style={[
            styles.addButton,
            (isLoading || !domainName.trim()) && styles.addButtonDisabled,
          ]}
          onPress={handleAddDomain}
          disabled={isLoading || !domainName.trim()}
        >
          <View style={styles.addButtonLoading}>
            <Icon name="add" size={20} color="#FFFFFF" />
            <Text style={[styles.addButtonText, styles.loadingText]}>
              {isLoading ? 'Adding Domain...' : 'Add Domain'}
            </Text>
          </View>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

export default AddDomainScreen;
