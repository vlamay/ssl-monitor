/**
 * Tab Bar Icon Component
 */

import React from 'react';
import Icon from 'react-native-vector-icons/MaterialIcons';

interface TabBarIconProps {
  route: string;
  focused: boolean;
  color: string;
  size: number;
}

const TabBarIcon: React.FC<TabBarIconProps> = ({ route, focused, color, size }) => {
  const getIconName = (routeName: string): string => {
    switch (routeName) {
      case 'Dashboard':
        return 'dashboard';
      case 'Domains':
        return 'domain';
      case 'Analytics':
        return 'analytics';
      case 'Notifications':
        return 'notifications';
      default:
        return 'help';
    }
  };

  return (
    <Icon
      name={getIconName(route)}
      size={size}
      color={color}
    />
  );
};

export default TabBarIcon;
