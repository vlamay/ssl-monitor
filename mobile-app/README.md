# SSL Monitor Pro - Mobile App

React Native mobile application for SSL certificate monitoring and management.

## 📱 Features

### Core Features
- **SSL Certificate Monitoring** - Monitor SSL certificates in real-time
- **Domain Management** - Add, edit, and delete monitored domains
- **Push Notifications** - Get alerts for expiring certificates
- **Offline Support** - View cached data when offline
- **Biometric Authentication** - Secure login with fingerprint/face ID

### User Experience
- **Dark/Light Theme** - Automatic theme switching
- **Multi-language Support** - 7 languages supported
- **Real-time Updates** - Live SSL status updates
- **Analytics Dashboard** - Charts and insights
- **User Preferences** - Customizable settings

## 🛠️ Tech Stack

### Core Technologies
- **React Native 0.72.6** - Cross-platform mobile development
- **TypeScript** - Type-safe development
- **Redux Toolkit** - State management
- **React Navigation 6** - Navigation and routing

### UI/UX Libraries
- **React Native Paper** - Material Design components
- **React Native Elements** - UI component library
- **React Native Vector Icons** - Icon library
- **React Native Reanimated** - Animations

### Data & API
- **React Query** - Data fetching and caching
- **Axios** - HTTP client
- **Redux Persist** - State persistence

### Security & Storage
- **React Native Keychain** - Secure token storage
- **React Native Biometrics** - Biometric authentication
- **AsyncStorage** - Local data storage

### Notifications & Network
- **React Native Push Notification** - Push notifications
- **React Native NetInfo** - Network status monitoring

## 📁 Project Structure

```
mobile-app/
├── src/
│   ├── components/          # Reusable components
│   │   └── navigation/      # Navigation components
│   ├── screens/            # Screen components
│   │   ├── auth/           # Authentication screens
│   │   └── main/           # Main app screens
│   ├── services/           # API and app services
│   ├── store/              # Redux store and slices
│   │   └── slices/         # Redux state slices
│   ├── navigation/         # Navigation configuration
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   └── App.tsx             # Main app component
├── android/                # Android-specific code
├── ios/                    # iOS-specific code
├── package.json            # Dependencies and scripts
└── README.md               # This file
```

## 🚀 Getting Started

### Prerequisites
- Node.js 16+
- React Native CLI
- Android Studio (for Android)
- Xcode (for iOS)

### Installation

1. **Install dependencies**
   ```bash
   cd mobile-app
   npm install
   ```

2. **iOS Setup**
   ```bash
   cd ios
   pod install
   cd ..
   ```

3. **Run the app**
   ```bash
   # Android
   npm run android
   
   # iOS
   npm run ios
   
   # Start Metro bundler
   npm start
   ```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the mobile-app directory:

```env
# API Configuration
API_BASE_URL=https://ssl-monitor-api.onrender.com
API_TIMEOUT=10000

# Push Notifications
FCM_SERVER_KEY=your_fcm_server_key

# Analytics (optional)
ANALYTICS_ENABLED=true
```

### API Configuration
Update the API base URL in services:
- `AuthService.ts`
- `DomainService.ts`

## 📱 Screens

### Authentication
- **LoginScreen** - User login with email/password
- **RegisterScreen** - User registration

### Main App
- **DashboardScreen** - Overview of SSL certificates
- **DomainsScreen** - List of monitored domains
- **DomainDetailScreen** - Detailed domain information
- **AnalyticsScreen** - Charts and insights
- **NotificationsScreen** - Push notifications
- **SettingsScreen** - App configuration
- **ProfileScreen** - User profile management

## 🔐 Security Features

### Authentication
- Secure token storage using Keychain
- Automatic token refresh
- Biometric authentication support
- Session management

### Data Protection
- Encrypted local storage
- Secure API communication
- Certificate pinning (optional)

## 📊 State Management

### Redux Store Structure
```typescript
{
  auth: {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
  };
  domains: {
    domains: Domain[];
    selectedDomain: Domain | null;
    isLoading: boolean;
  };
  notifications: {
    notifications: Notification[];
    unreadCount: number;
  };
  settings: {
    language: string;
    theme: 'light' | 'dark' | 'auto';
    notifications: NotificationSettings;
  };
}
```

## 🔔 Push Notifications

### Notification Types
- **SSL Warning** - Certificate expiring soon
- **SSL Critical** - Certificate expiring in 7 days
- **SSL Expired** - Certificate has expired
- **System Updates** - App and system notifications

### Configuration
```typescript
// Notification channels
const notificationChannels = {
  ssl_alerts: 'SSL Certificate Alerts',
  system: 'System Notifications',
};
```

## 🎨 Theming

### Theme System
- Light and dark themes
- Automatic system theme detection
- Custom color schemes
- Consistent spacing and typography

### Usage
```typescript
import { useTheme } from '../hooks/useTheme';

const MyComponent = () => {
  const theme = useTheme();
  
  return (
    <View style={{ backgroundColor: theme.colors.background }}>
      <Text style={{ color: theme.colors.text }}>Hello</Text>
    </View>
  );
};
```

## 📈 Analytics

### Tracked Events
- App launches
- Feature usage
- Error occurrences
- Performance metrics

### Privacy
- User consent required
- Data anonymization
- GDPR compliant

## 🧪 Testing

### Test Structure
```
__tests__/
├── components/     # Component tests
├── screens/        # Screen tests
├── services/       # Service tests
└── utils/          # Utility tests
```

### Running Tests
```bash
npm test
npm run test:coverage
```

## 📦 Building

### Android
```bash
npm run build:android
```

### iOS
```bash
npm run build:ios
```

### Release Builds
```bash
# Android APK
cd android
./gradlew assembleRelease

# iOS Archive
cd ios
xcodebuild -workspace SSLMonitorPro.xcworkspace -scheme SSLMonitorPro -configuration Release archive
```

## 🚀 Deployment

### App Stores
- **Google Play Store** - Android distribution
- **Apple App Store** - iOS distribution

### Over-the-Air Updates
- CodePush integration (optional)
- Automatic updates

## 🔧 Development

### Code Style
- ESLint configuration
- Prettier formatting
- TypeScript strict mode

### Git Workflow
- Feature branches
- Pull requests
- Code review required

## 📚 API Integration

### Backend API
- RESTful API endpoints
- JWT authentication
- Real-time WebSocket updates
- Offline data synchronization

### Endpoints Used
- `/auth/login` - User authentication
- `/domains` - Domain management
- `/analytics` - Analytics data
- `/notifications` - Push notification management

## 🐛 Troubleshooting

### Common Issues

1. **Metro bundler issues**
   ```bash
   npx react-native start --reset-cache
   ```

2. **iOS build issues**
   ```bash
   cd ios
   pod install
   ```

3. **Android build issues**
   ```bash
   cd android
   ./gradlew clean
   ```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
npm start
```

## 📞 Support

### Documentation
- [React Native Docs](https://reactnative.dev/)
- [React Navigation Docs](https://reactnavigation.org/)
- [Redux Toolkit Docs](https://redux-toolkit.js.org/)

### Issues
- Report bugs via GitLab Issues
- Feature requests welcome
- Pull requests accepted

## 📄 License

MIT License - see LICENSE file for details.

---

**SSL Monitor Pro Mobile App** - Professional SSL certificate monitoring on your mobile device.
