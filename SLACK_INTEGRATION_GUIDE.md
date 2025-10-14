# 💬 Slack Integration Guide - SSL Monitor Pro

## 🎯 Overview

SSL Monitor Pro now supports Slack integration with OAuth 2.0 authentication, allowing development teams to receive SSL certificate alerts directly in their Slack channels.

## 🚀 Features

- **OAuth 2.0 Integration**: Secure authentication with Slack workspaces
- **Channel Notifications**: Send alerts to any public or private channel
- **Rich Message Formatting**: Beautiful SSL alerts with blocks and context
- **Team Collaboration**: Perfect for development teams and DevOps
- **Test Functionality**: Verify Slack setup before going live

## 🔧 Setup Instructions

### **Step 1: Create Slack App**

1. **Go to Slack API**:
   - Visit [api.slack.com/apps](https://api.slack.com/apps)
   - Click "Create New App"
   - Choose "From scratch"
   - Enter app name: "SSL Monitor Pro"
   - Select your workspace

2. **Configure OAuth & Permissions**:
   - Go to "OAuth & Permissions" in sidebar
   - Add these Bot Token Scopes:
     - `chat:write` - Send messages to channels
     - `channels:read` - List public channels
     - `groups:read` - List private channels
     - `im:read` - List direct messages
     - `mpim:read` - List group direct messages

3. **Set Redirect URLs**:
   - In "OAuth & Permissions", add Redirect URL:
   - `https://your-domain.com/api/v1/slack/oauth/callback`
   - Replace `your-domain.com` with your actual domain

### **Step 2: Install App to Workspace**

1. **Install App**:
   - In "OAuth & Permissions", click "Install to Workspace"
   - Review permissions and click "Allow"
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`)

2. **Get App Credentials**:
   - Copy "Client ID" from "Basic Information"
   - Copy "Client Secret" from "Basic Information"
   - Copy "Bot User OAuth Token" from "OAuth & Permissions"

### **Step 3: Configure Environment Variables**

```bash
# Slack OAuth Configuration
SLACK_CLIENT_ID=your_client_id_here
SLACK_CLIENT_SECRET=your_client_secret_here
SLACK_REDIRECT_URI=https://your-domain.com/api/v1/slack/oauth/callback
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
```

### **Step 4: Test Integration**

1. **Get OAuth URL**:
   ```http
   GET /api/v1/slack/oauth-url
   Authorization: Bearer <token>
   ```

2. **Authorize Integration**:
   - Click the OAuth URL
   - Authorize the app in Slack
   - You'll be redirected back with authorization code

3. **Test Message**:
   ```http
   POST /api/v1/slack/test
   Content-Type: application/json
   Authorization: Bearer <token>
   
   {
     "channel": "#general",
     "message": "Test message from SSL Monitor Pro"
   }
   ```

## 📱 API Endpoints

### **Get OAuth URL**
```http
GET /api/v1/slack/oauth-url
Authorization: Bearer <token>
```

**Response:**
```json
{
  "oauth_url": "https://slack.com/oauth/v2/authorize?...",
  "state": "secure_state_token",
  "instructions": "Click the OAuth URL to authorize Slack integration"
}
```

### **Handle OAuth Callback**
```http
POST /api/v1/slack/oauth/callback
Content-Type: application/json
Authorization: Bearer <token>

{
  "code": "authorization_code_from_slack",
  "state": "state_token_for_verification"
}
```

### **Create Slack Notification**
```http
POST /api/v1/slack/notifications
Content-Type: application/json
Authorization: Bearer <token>

{
  "channel": "#dev-alerts",
  "enabled": true,
  "triggers": ["expires_in_30d", "expires_in_7d", "expires_in_1d", "expired"],
  "team_id": "T1234567890"
}
```

### **Get Slack Notifications**
```http
GET /api/v1/slack/notifications
Authorization: Bearer <token>
```

### **Update Slack Notification**
```http
PUT /api/v1/slack/notifications/{notification_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "channel": "#production-alerts",
  "enabled": false
}
```

### **Delete Slack Notification**
```http
DELETE /api/v1/slack/notifications/{notification_id}
Authorization: Bearer <token>
```

### **Test Slack Message**
```http
POST /api/v1/slack/test
Content-Type: application/json
Authorization: Bearer <token>

{
  "channel": "#general",
  "message": "Custom test message"
}
```

### **Get Available Channels**
```http
GET /api/v1/slack/channels?token=slack_access_token
Authorization: Bearer <token>
```

### **Get Setup Status**
```http
GET /api/v1/slack/setup-status
Authorization: Bearer <token>
```

## 💬 Message Templates

### **SSL Certificate Expiration Alert**
```
🔒 *SSL Alert*: example.com expires in 7 days. Time to renew!

Domain: example.com | SSL Monitor Pro
```

### **SSL Certificate Expired**
```
🚨 *URGENT*: SSL certificate for example.com has EXPIRED! Immediate action required.

Domain: example.com | SSL Monitor Pro
```

### **SSL Certificate Renewed**
```
✅ *SSL Update*: Certificate for example.com has been renewed successfully.

Domain: example.com | SSL Monitor Pro
```

### **Renewal Failed**
```
❌ *SSL Error*: Failed to renew certificate for example.com. Manual intervention needed.

Domain: example.com | SSL Monitor Pro
```

## 🎯 Channel Recommendations

### **Development Teams**
- `#dev-alerts` - Development environment alerts
- `#staging` - Staging environment monitoring
- `#infrastructure` - Infrastructure and DevOps alerts

### **Production Teams**
- `#production-alerts` - Critical production alerts only
- `#oncall` - For on-call engineers
- `#security` - Security-related SSL issues

### **General Teams**
- `#general` - All team members
- `#tech-updates` - Technical updates and notifications
- `#monitoring` - All monitoring alerts

## 🔒 Security Best Practices

### **Token Management**
- Store Slack tokens securely in environment variables
- Never commit tokens to version control
- Rotate tokens regularly
- Use different tokens for different environments

### **Channel Permissions**
- Use private channels for sensitive information
- Limit bot access to necessary channels only
- Review channel permissions regularly
- Consider using dedicated alert channels

### **OAuth Security**
- Always validate state parameter in OAuth callback
- Use HTTPS for all OAuth redirects
- Implement proper error handling
- Log OAuth events for audit

## 🛠️ Troubleshooting

### **Common Issues**

#### "Slack OAuth not configured"
- **Solution**: Set SLACK_CLIENT_ID, SLACK_CLIENT_SECRET, and SLACK_REDIRECT_URI
- **Check**: Environment variables are correctly set

#### "Invalid redirect URI"
- **Solution**: Ensure redirect URI in Slack app matches environment variable
- **Check**: URL is exactly the same (including https/http)

#### "Insufficient permissions"
- **Solution**: Add required bot token scopes in Slack app settings
- **Check**: `chat:write`, `channels:read`, `groups:read` scopes are added

#### "Channel not found"
- **Solution**: Ensure bot is member of the channel
- **Check**: Invite bot to private channels manually

#### "Message failed to send"
- **Solution**: Check bot token validity and channel permissions
- **Check**: Bot has permission to post in the channel

### **Debug Steps**
1. **Test OAuth Flow**: Use `/api/v1/slack/oauth-url` endpoint
2. **Check Setup Status**: Use `/api/v1/slack/setup-status` endpoint
3. **Test Message**: Use `/api/v1/slack/test` endpoint
4. **Verify Permissions**: Check Slack app permissions in workspace

## 📊 Best Practices

### **Channel Organization**
- Create dedicated channels for different alert types
- Use consistent naming conventions
- Set appropriate channel topics and descriptions
- Pin important messages for reference

### **Message Formatting**
- Use rich message blocks for better formatting
- Include relevant context and links
- Use appropriate emojis for different alert types
- Keep messages concise but informative

### **Team Workflow**
- Set up channel notifications for team members
- Use threads for follow-up discussions
- Integrate with existing incident response procedures
- Regular testing of alert flows

## 🚀 Advanced Features

### **Custom Message Blocks**
Slack integration supports rich message formatting with blocks:

```json
{
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "🔒 *SSL Alert*: example.com expires in 7 days"
      }
    },
    {
      "type": "context",
      "elements": [
        {
          "type": "mrkdwn",
          "text": "Domain: example.com | SSL Monitor Pro"
        }
      ]
    }
  ]
}
```

### **Interactive Buttons** (Future Feature)
- Quick action buttons for common responses
- Integration with SSL certificate renewal workflows
- Acknowledgment buttons for alert management

### **Threaded Conversations** (Future Feature)
- Follow-up messages in threads
- Contextual information and discussions
- Integration with team collaboration tools

## 📈 Monitoring & Analytics

### **Metrics to Track**
- Message delivery success rate
- Channel engagement with alerts
- Response times to SSL alerts
- Team notification preferences

### **Dashboard Integration**
- Slack notification status in user dashboard
- Channel usage analytics
- Alert response metrics
- Team collaboration insights

## 🔄 Integration with Other Services

### **Combined Notifications**
- Use Slack for team alerts
- SMS for critical production issues
- Email for detailed reports
- WhatsApp for personal notifications

### **Workflow Integration**
- Connect with incident management tools
- Integrate with monitoring dashboards
- Link with SSL certificate management
- Connect with CI/CD pipelines

---

## 📞 Support

For Slack integration support:
- **Documentation**: [Slack API Documentation](https://api.slack.com/)
- **SSL Monitor Pro Support**: support@sslmonitor.pro
- **Slack Support**: [Slack API Support](https://api.slack.com/support)

**Ready to get your team notified about SSL issues via Slack? Set up the integration and never miss a certificate expiration again!** 🚀
