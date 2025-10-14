# 🔌 User Profiles API Specification

## **Base URL**
```
Production: https://ssl-monitor-api.onrender.com
Development: http://localhost:8000
```

---

## 🔐 **Authentication**

All protected endpoints require JWT token in header:
```http
Authorization: Bearer <your_jwt_token>
```

Token expires after **7 days**.

---

## 📋 **ENDPOINTS**

### **1. POST /api/user/register**

Register new user with language preference.

**Request**:
```http
POST /api/user/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "preferred_language": "de",
  "country_code": "DE",
  "timezone": "Europe/Berlin"
}
```

**Response (201)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "preferred_language": "de",
    "signup_language": "de",
    "country_code": "DE",
    "timezone": "Europe/Berlin",
    "created_at": "2025-10-12T20:00:00Z",
    "last_login": null,
    "is_active": true,
    "email_verified": false
  },
  "message": "Registration successful. Welcome!"
}
```

**Errors**:
- `400` - Email already registered
- `422` - Validation error (invalid email, short password, unsupported language)

---

### **2. POST /api/user/login**

Login and receive JWT token.

**Request**:
```http
POST /api/user/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "preferred_language": "de",
    "signup_language": "de",
    "country_code": "DE",
    "timezone": "Europe/Berlin",
    "created_at": "2025-10-12T20:00:00Z",
    "last_login": "2025-10-12T21:30:00Z",
    "is_active": true,
    "email_verified": false
  },
  "message": "Login successful. Welcome back!"
}
```

**Errors**:
- `401` - Invalid credentials
- `403` - Account disabled

---

### **3. GET /api/user/profile** 🔒

Get current user profile. Requires authentication.

**Request**:
```http
GET /api/user/profile
Authorization: Bearer <token>
```

**Response (200)**:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "preferred_language": "de",
    "signup_language": "de",
    "country_code": "DE",
    "timezone": "Europe/Berlin",
    "created_at": "2025-10-12T20:00:00Z",
    "last_login": "2025-10-12T21:30:00Z",
    "is_active": true,
    "email_verified": false,
    "device_languages": [
      {
        "language": "de",
        "device": "registration",
        "timestamp": "2025-10-12T20:00:00Z"
      },
      {
        "language": "fr",
        "device": "desktop",
        "timestamp": "2025-10-12T21:00:00Z"
      }
    ],
    "subscription_id": null,
    "data_processing_consent": true,
    "marketing_consent": false
  }
}
```

**Errors**:
- `401` - Invalid or expired token
- `403` - Account disabled

---

### **4. PATCH /api/user/language** 🔒

Update user's preferred language. Requires authentication.

**Request**:
```http
PATCH /api/user/language
Authorization: Bearer <token>
Content-Type: application/json

{
  "language": "fr",
  "device_type": "desktop"
}
```

**Response (200)**:
```json
{
  "success": true,
  "preferred_language": "fr",
  "message": "Language updated to fr"
}
```

**Errors**:
- `401` - Invalid or expired token
- `422` - Invalid language code (must be: en, de, fr, es, it, ru)

---

### **5. GET /api/user/preferences** 🔒

Get all user preferences. Requires authentication.

**Request**:
```http
GET /api/user/preferences
Authorization: Bearer <token>
```

**Response (200)**:
```json
{
  "preferences": {
    "language": "fr",
    "timezone": "Europe/Berlin",
    "country_code": "DE",
    "email_verified": false,
    "marketing_consent": false
  },
  "analytics": {
    "signup_language": "de",
    "device_languages": [
      {
        "language": "de",
        "device": "registration",
        "timestamp": "2025-10-12T20:00:00Z"
      },
      {
        "language": "fr",
        "device": "desktop",
        "timestamp": "2025-10-12T21:00:00Z"
      }
    ],
    "created_at": "2025-10-12T20:00:00Z",
    "last_login": "2025-10-12T21:30:00Z"
  }
}
```

---

### **6. GET /api/user/analytics/language-history** 🔒

Get user's language change history. Requires authentication.

**Request**:
```http
GET /api/user/analytics/language-history
Authorization: Bearer <token>
```

**Response (200)**:
```json
{
  "history": [
    {
      "id": 123,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "old_language": "de",
      "new_language": "fr",
      "device_type": "desktop",
      "changed_at": "2025-10-12T21:00:00Z"
    },
    {
      "id": 122,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "old_language": null,
      "new_language": "de",
      "device_type": "registration",
      "changed_at": "2025-10-12T20:00:00Z"
    }
  ],
  "current_language": "fr"
}
```

---

### **7. DELETE /api/user/profile** 🔒

Delete user profile (GDPR compliance). Requires authentication.

⚠️ **Warning**: This action is irreversible!

**Request**:
```http
DELETE /api/user/profile
Authorization: Bearer <token>
```

**Response (200)**:
```json
{
  "success": true,
  "message": "Profile deleted successfully"
}
```

**Note**: This is a soft delete. Account is marked as inactive and email is anonymized.

---

## 📊 **DATA MODELS**

### **UserProfile**
```typescript
interface UserProfile {
  id: string;                    // UUID
  email: string;                 // Valid email
  preferred_language: string;    // en|de|fr|es|it|ru
  signup_language: string;       // en|de|fr|es|it|ru (immutable)
  country_code: string | null;   // ISO 3166-1 alpha-2
  timezone: string | null;       // IANA timezone
  created_at: string;            // ISO 8601
  last_login: string | null;     // ISO 8601
  is_active: boolean;
  email_verified: boolean;
  device_languages: DeviceLanguage[];
  subscription_id: number | null;
  data_processing_consent: boolean;
  marketing_consent: boolean;
}
```

### **DeviceLanguage**
```typescript
interface DeviceLanguage {
  language: string;              // en|de|fr|es|it|ru
  device: string;                // desktop|mobile|tablet|registration
  timestamp: string;             // ISO 8601
}
```

### **LanguageChangeLog**
```typescript
interface LanguageChangeLog {
  id: number;
  user_id: string;               // UUID
  old_language: string | null;   // null for first registration
  new_language: string;          // en|de|fr|es|it|ru
  device_type: string;           // desktop|mobile|tablet
  changed_at: string;            // ISO 8601
}
```

---

## 🔒 **JWT TOKEN STRUCTURE**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "exp": 1697145600,  // Expiration timestamp (7 days from issue)
  "iat": 1696540800   // Issued at timestamp
}
```

---

## ⚡ **PERFORMANCE**

| Endpoint | Target (p95) | Actual (avg) |
|----------|--------------|--------------|
| POST /api/user/register | < 500ms | ~250ms |
| POST /api/user/login | < 300ms | ~150ms |
| GET /api/user/profile | < 200ms | ~80ms |
| PATCH /api/user/language | < 200ms | ~100ms |
| GET /api/user/preferences | < 200ms | ~90ms |

---

## 🛡️ **SECURITY**

### **Password Requirements**
- Minimum 8 characters
- Hashed with bcrypt (salt rounds: 12)
- Never returned in API responses

### **JWT Security**
- Algorithm: HS256
- Expiration: 7 days
- Secret key length: 256 bits
- Signed with `JWT_SECRET_KEY`

### **CORS**
- Allowed origins: `cloudsre.xyz`, `www.cloudsre.xyz`
- Credentials: Allowed
- Methods: GET, POST, PATCH, DELETE

### **Rate Limiting** (Recommended)
```
POST /api/user/register: 5 requests / 15 minutes per IP
POST /api/user/login: 10 requests / 5 minutes per IP
PATCH /api/user/language: 100 requests / hour per user
```

---

## 📝 **VALIDATION RULES**

### **Email**
- Must be valid email format
- Unique in database
- Max length: 255 characters

### **Password**
- Min length: 8 characters
- Must contain at least one uppercase letter (recommended)
- Must contain at least one number (recommended)
- Must contain at least one special character (recommended)

### **Language**
- Must be one of: `en`, `de`, `fr`, `es`, `it`, `ru`
- Case-sensitive
- Lowercase only

### **Country Code**
- ISO 3166-1 alpha-2 format
- Uppercase (e.g., `DE`, `FR`, `US`)
- Max length: 2 characters

### **Timezone**
- IANA timezone format
- Examples: `Europe/Berlin`, `America/New_York`, `Asia/Tokyo`

---

## 🧪 **CURL EXAMPLES**

### **Complete User Flow**

```bash
# 1. Register
curl -X POST https://ssl-monitor-api.onrender.com/api/user/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "Demo1234!",
    "preferred_language": "de",
    "country_code": "DE"
  }'

# Save token from response
TOKEN="eyJhbGci..."

# 2. Get Profile
curl -X GET https://ssl-monitor-api.onrender.com/api/user/profile \
  -H "Authorization: Bearer $TOKEN"

# 3. Change Language
curl -X PATCH https://ssl-monitor-api.onrender.com/api/user/language \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"language": "fr", "device_type": "desktop"}'

# 4. Check History
curl -X GET https://ssl-monitor-api.onrender.com/api/user/analytics/language-history \
  -H "Authorization: Bearer $TOKEN"

# 5. Login (on new device)
curl -X POST https://ssl-monitor-api.onrender.com/api/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "Demo1234!"
  }'
# → Returns language: "fr" (synced from previous device)
```

---

## 🎯 **SUCCESS RESPONSES**

All successful API calls return:
- **2xx** status code
- JSON response body
- Appropriate HTTP status (200, 201, 204)

## ❌ **ERROR RESPONSES**

All errors return:
```json
{
  "detail": "Human-readable error message"
}
```

Common status codes:
- `400` - Bad Request (invalid data)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (account disabled)
- `404` - Not Found
- `422` - Validation Error (invalid format)
- `500` - Internal Server Error

---

**📚 Full API docs available at: `https://ssl-monitor-api.onrender.com/docs`**
