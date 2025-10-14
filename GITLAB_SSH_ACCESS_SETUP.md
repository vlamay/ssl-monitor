# 🔑 GITLAB SSH ACCESS SETUP

## 🎯 **REPOSITORY:** ssl-monitor-pro
## 🔗 **URL:** https://gitlab.trustforge.uk/root/ssl-monitor-pro.git

---

## 🚀 **SSH ACCESS SOLUTIONS**

### **Method 1: Deploy Token (RECOMMENDED)**

#### **Step 1: Create Deploy Token in GitLab**
1. **Login to GitLab:** https://gitlab.trustforge.uk/
2. **Go to:** Your project `ssl-monitor-pro`
3. **Navigate:** Settings → Repository
4. **Expand:** Deploy tokens
5. **Create token:**
   - **Name:** `render-deployment`
   - **Scopes:** `read_repository`
   - **Expires:** No expiration
6. **Copy:** Username and token

#### **Step 2: Use Deploy Token in Render**
**Repository URL format:**
```
https://[USERNAME]:[TOKEN]@gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

**Example:**
```
https://gitlab+deploy-token-123:glpat-xxxxxxxxxxxxxxxxxxxx@gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

---

### **Method 2: Personal Access Token**

#### **Step 1: Create Personal Access Token**
1. **Login to GitLab:** https://gitlab.trustforge.uk/
2. **Go to:** User Settings → Access Tokens
3. **Create token:**
   - **Name:** `render-deployment`
   - **Scopes:** `read_repository`
   - **Expires:** No expiration (or set date)
4. **Copy token:** Save securely

#### **Step 2: Use Token in Render**
**Repository URL format:**
```
https://oauth2:[TOKEN]@gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

**Example:**
```
https://oauth2:glpat-xxxxxxxxxxxxxxxxxxxx@gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

---

### **Method 3: SSH Keys (Advanced)**

#### **Step 1: Generate SSH Key**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "render-deployment"

# Copy public key
cat ~/.ssh/id_ed25519.pub
```

#### **Step 2: Add SSH Key to GitLab**
1. **Login to GitLab:** https://gitlab.trustforge.uk/
2. **Go to:** User Settings → SSH Keys
3. **Paste:** Your public key
4. **Add key**

#### **Step 3: Use SSH URL in Render**
**Repository URL:**
```
git@gitlab.trustforge.uk:root/ssl-monitor-pro.git
```

---

## 🎯 **RECOMMENDED: Deploy Token**

### **Why Deploy Tokens?**
- ✅ **Purpose-built** for CI/CD
- ✅ **Secure** - can be revoked anytime
- ✅ **Simple** - no SSH key management
- ✅ **Works** with HTTPS URLs

### **Quick Setup:**
1. **GitLab:** Project → Settings → Repository → Deploy tokens
2. **Create:** `render-deployment` with `read_repository` scope
3. **Copy:** Username and token
4. **Render:** Use format: `https://[USERNAME]:[TOKEN]@gitlab.trustforge.uk/root/ssl-monitor-pro.git`

---

## 🔧 **DETAILED STEPS**

### **Deploy Token Setup:**

#### **1. Access GitLab Project**
- **URL:** https://gitlab.trustforge.uk/root/ssl-monitor-pro
- **Login:** root user
- **Navigate:** Settings → Repository

#### **2. Create Deploy Token**
- **Expand:** Deploy tokens section
- **Name:** `render-deployment`
- **Scopes:** Check `read_repository`
- **Expires:** Leave empty (no expiration)
- **Create token**

#### **3. Copy Credentials**
You'll get:
- **Username:** `gitlab+deploy-token-[ID]`
- **Token:** `[LONG_TOKEN_STRING]`

#### **4. Update Render**
- **Repository URL:** 
  ```
  https://gitlab+deploy-token-[ID]:[TOKEN]@gitlab.trustforge.uk/root/ssl-monitor-pro.git
  ```
- **Branch:** `main`
- **Save Changes**
- **Manual Deploy**

---

## 🧪 **TESTING**

### **Test Deploy Token:**
```bash
# Test with token
curl -I https://gitlab+deploy-token-[ID]:[TOKEN]@gitlab.trustforge.uk/root/ssl-monitor-pro.git

# Expected: 200 OK or git protocol response
```

### **Test Repository Access:**
```bash
# Clone test
git clone https://gitlab+deploy-token-[ID]:[TOKEN]@gitlab.trustforge.uk/root/ssl-monitor-pro.git test-clone
```

---

## 🚨 **TROUBLESHOOTING**

### **Token Not Working?**
- Check token permissions
- Verify token is not expired
- Ensure correct username format

### **Still Getting 302?**
- Repository might still be private
- Check deploy token scopes
- Verify URL format

### **Render Rejects URL?**
- Check URL format exactly
- Ensure no extra spaces
- Try different browser

---

## 📞 **SUPPORT**

### **GitLab Links:**
- **Project:** https://gitlab.trustforge.uk/root/ssl-monitor-pro
- **Deploy Tokens:** https://gitlab.trustforge.uk/root/ssl-monitor-pro/-/settings/repository
- **Access Tokens:** https://gitlab.trustforge.uk/-/profile/personal_access_tokens

### **Render Dashboard:**
- **Service:** https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg

---

## 🎯 **QUICK ACTION**

### **Fastest Solution:**
1. **GitLab:** Project Settings → Repository → Deploy tokens
2. **Create:** `render-deployment` with `read_repository`
3. **Copy:** Username and token
4. **Render:** 
   ```
   https://[USERNAME]:[TOKEN]@gitlab.trustforge.uk/root/ssl-monitor-pro.git
   ```

### **Expected Result:**
- ✅ Repository accessible with token
- ✅ Render accepts the URL
- ✅ Deployment starts successfully

---

*SSH Access Setup Guide - October 13, 2025*  
*Repository: ssl-monitor-pro*
