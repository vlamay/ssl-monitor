/**
 * Profile Screen - User profile management
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Image,
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { RootState, AppDispatch } from '../../store';
import { updateProfile } from '../../store/slices/authSlice';
import { useTheme } from '../../hooks/useTheme';

const ProfileScreen: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [company, setCompany] = useState('');
  const [phone, setPhone] = useState('');

  const dispatch = useDispatch<AppDispatch>();
  const theme = useTheme();

  const { user, isLoading } = useSelector((state: RootState) => state.auth);

  React.useEffect(() => {
    if (user) {
      setName(user.name || '');
      setEmail(user.email || '');
      setCompany(user.company || '');
      setPhone(user.phone || '');
    }
  }, [user]);

  const handleSave = async () => {
    try {
      const profileData = {
        name,
        email,
        company,
        phone,
      };

      await dispatch(updateProfile(profileData)).unwrap();
      setIsEditing(false);
      
      Alert.alert('Success', 'Profile updated successfully!');
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to update profile');
    }
  };

  const handleCancel = () => {
    if (user) {
      setName(user.name || '');
      setEmail(user.email || '');
      setCompany(user.company || '');
      setPhone(user.phone || '');
    }
    setIsEditing(false);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const renderProfileHeader = () => (
    <View style={styles.profileHeader}>
      <View style={styles.avatarContainer}>
        {user?.avatar ? (
          <Image source={{ uri: user.avatar }} style={styles.avatar} />
        ) : (
          <View style={styles.avatarPlaceholder}>
            <Icon name="person" size={40} color={theme.colors.primary} />
          </View>
        )}
        <TouchableOpacity style={styles.editAvatarButton}>
          <Icon name="camera-alt" size={16} color="#FFFFFF" />
        </TouchableOpacity>
      </View>
      
      <Text style={styles.userName}>{user?.name || 'User'}</Text>
      <Text style={styles.userEmail}>{user?.email}</Text>
      
      {!isEditing && (
        <TouchableOpacity style={styles.editButton} onPress={handleEdit}>
          <Icon name="edit" size={16} color={theme.colors.primary} />
          <Text style={styles.editButtonText}>Edit Profile</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  const renderInputField = (
    label: string,
    value: string,
    onChangeText: (text: string) => void,
    placeholder?: string,
    keyboardType?: any,
    editable: boolean = true
  ) => (
    <View style={styles.inputGroup}>
      <Text style={styles.inputLabel}>{label}</Text>
      <TextInput
        style={[
          styles.textInput,
          !editable && styles.textInputDisabled,
        ]}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={theme.colors.textSecondary}
        keyboardType={keyboardType}
        editable={editable}
      />
    </View>
  );

  const renderStatsSection = () => (
    <View style={styles.statsSection}>
      <Text style={styles.sectionTitle}>Account Statistics</Text>
      
      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Icon name="domain" size={24} color={theme.colors.primary} />
          <Text style={styles.statValue}>12</Text>
          <Text style={styles.statLabel}>Monitored Domains</Text>
        </View>
        
        <View style={styles.statCard}>
          <Icon name="notifications" size={24} color={theme.colors.warning} />
          <Text style={styles.statValue}>3</Text>
          <Text style={styles.statLabel}>Active Alerts</Text>
        </View>
        
        <View style={styles.statCard}>
          <Icon name="schedule" size={24} color={theme.colors.success} />
          <Text style={styles.statValue}>7</Text>
          <Text style={styles.statLabel}>Days Monitoring</Text>
        </View>
        
        <View style={styles.statCard}>
          <Icon name="security" size={24} color={theme.colors.info} />
          <Text style={styles.statValue}>95%</Text>
          <Text style={styles.statLabel}>SSL Health</Text>
        </View>
      </View>
    </View>
  );

  const renderAccountSection = () => (
    <View style={styles.accountSection}>
      <Text style={styles.sectionTitle}>Account Information</Text>
      
      <View style={styles.sectionContent}>
        {renderInputField(
          'Full Name',
          name,
          setName,
          'Enter your full name',
          'default',
          isEditing
        )}
        
        {renderInputField(
          'Email',
          email,
          setEmail,
          'Enter your email',
          'email-address',
          isEditing
        )}
        
        {renderInputField(
          'Company',
          company,
          setCompany,
          'Enter your company name',
          'default',
          isEditing
        )}
        
        {renderInputField(
          'Phone',
          phone,
          setPhone,
          'Enter your phone number',
          'phone-pad',
          isEditing
        )}
        
        {renderInputField(
          'Account Type',
          'Premium',
          () => {},
          '',
          'default',
          false
        )}
        
        {renderInputField(
          'Member Since',
          'October 2024',
          () => {},
          '',
          'default',
          false
        )}
      </View>
    </View>
  );

  const renderActionButtons = () => {
    if (!isEditing) return null;

    return (
      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.cancelButton} onPress={handleCancel}>
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.saveButton} onPress={handleSave} disabled={isLoading}>
          <Text style={styles.saveButtonText}>
            {isLoading ? 'Saving...' : 'Save Changes'}
          </Text>
        </TouchableOpacity>
      </View>
    );
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    scrollView: {
      flex: 1,
    },
    profileHeader: {
      alignItems: 'center',
      paddingVertical: theme.spacing.xl,
      paddingHorizontal: theme.spacing.lg,
      backgroundColor: theme.colors.surface,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    avatarContainer: {
      position: 'relative',
      marginBottom: theme.spacing.lg,
    },
    avatar: {
      width: 100,
      height: 100,
      borderRadius: 50,
    },
    avatarPlaceholder: {
      width: 100,
      height: 100,
      borderRadius: 50,
      backgroundColor: theme.colors.background,
      justifyContent: 'center',
      alignItems: 'center',
      borderWidth: 2,
      borderColor: theme.colors.border,
    },
    editAvatarButton: {
      position: 'absolute',
      bottom: 0,
      right: 0,
      backgroundColor: theme.colors.primary,
      borderRadius: 15,
      width: 30,
      height: 30,
      justifyContent: 'center',
      alignItems: 'center',
      borderWidth: 2,
      borderColor: theme.colors.surface,
    },
    userName: {
      fontSize: theme.fonts.sizes.xl,
      fontWeight: 'bold',
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    userEmail: {
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.textSecondary,
      marginBottom: theme.spacing.lg,
    },
    editButton: {
      flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: theme.spacing.lg,
      paddingVertical: theme.spacing.sm,
      backgroundColor: theme.colors.background,
      borderRadius: 20,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    editButtonText: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.primary,
      marginLeft: theme.spacing.xs,
      fontWeight: '500',
    },
    statsSection: {
      paddingVertical: theme.spacing.lg,
      paddingHorizontal: theme.spacing.lg,
    },
    sectionTitle: {
      fontSize: theme.fonts.sizes.lg,
      fontWeight: '600',
      color: theme.colors.text,
      marginBottom: theme.spacing.lg,
    },
    statsGrid: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      justifyContent: 'space-between',
    },
    statCard: {
      width: '48%',
      backgroundColor: theme.colors.surface,
      borderRadius: 12,
      padding: theme.spacing.lg,
      alignItems: 'center',
      marginBottom: theme.spacing.md,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    statValue: {
      fontSize: theme.fonts.sizes.xl,
      fontWeight: 'bold',
      color: theme.colors.text,
      marginTop: theme.spacing.sm,
      marginBottom: theme.spacing.xs,
    },
    statLabel: {
      fontSize: theme.fonts.sizes.sm,
      color: theme.colors.textSecondary,
      textAlign: 'center',
    },
    accountSection: {
      paddingVertical: theme.spacing.lg,
    },
    sectionContent: {
      paddingHorizontal: theme.spacing.lg,
    },
    inputGroup: {
      marginBottom: theme.spacing.lg,
    },
    inputLabel: {
      fontSize: theme.fonts.sizes.md,
      fontWeight: '500',
      color: theme.colors.text,
      marginBottom: theme.spacing.sm,
    },
    textInput: {
      borderWidth: 1,
      borderColor: theme.colors.border,
      borderRadius: 8,
      paddingHorizontal: theme.spacing.md,
      paddingVertical: theme.spacing.md,
      fontSize: theme.fonts.sizes.md,
      color: theme.colors.text,
      backgroundColor: theme.colors.surface,
    },
    textInputDisabled: {
      backgroundColor: theme.colors.background,
      color: theme.colors.textSecondary,
    },
    actionButtons: {
      flexDirection: 'row',
      paddingHorizontal: theme.spacing.lg,
      paddingVertical: theme.spacing.lg,
      gap: theme.spacing.md,
    },
    cancelButton: {
      flex: 1,
      paddingVertical: theme.spacing.md,
      borderRadius: 8,
      borderWidth: 1,
      borderColor: theme.colors.border,
      alignItems: 'center',
      backgroundColor: theme.colors.surface,
    },
    cancelButtonText: {
      fontSize: theme.fonts.sizes.md,
      fontWeight: '500',
      color: theme.colors.text,
    },
    saveButton: {
      flex: 1,
      paddingVertical: theme.spacing.md,
      borderRadius: 8,
      backgroundColor: theme.colors.primary,
      alignItems: 'center',
    },
    saveButtonText: {
      fontSize: theme.fonts.sizes.md,
      fontWeight: '600',
      color: '#FFFFFF',
    },
  });

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {renderProfileHeader()}
        {renderStatsSection()}
        {renderAccountSection()}
      </ScrollView>
      {renderActionButtons()}
    </View>
  );
};

export default ProfileScreen;
