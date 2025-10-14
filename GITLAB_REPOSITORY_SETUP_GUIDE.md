# 🚀 GITLAB REPOSITORY SETUP GUIDE

## ❌ **ПРОБЛЕМА:** Invalid repository URL
- **URL:** https://gitlab.trustforge.uk/root/ssl-monitor-pro.git
- **Ошибка:** Invalid repository URL
- **Причина:** Репозиторий не создан в GitLab

---

## 🔍 **ДИАГНОСТИКА**

### **GitLab Status:**
- ✅ **GitLab доступен:** https://gitlab.trustforge.uk/
- ✅ **SSL/TLS:** Работает
- ✅ **Cloudflare Tunnel:** ACTIVE
- ❌ **Репозиторий:** Не существует

### **Repository Access Test:**
```bash
curl -I https://gitlab.trustforge.uk/root/ssl-monitor-pro.git
# Result: 302 redirect to /users/sign_in
# Meaning: Repository doesn't exist or requires authentication
```

---

## 🎯 **РЕШЕНИЯ**

### **1️⃣ СОЗДАТЬ РЕПОЗИТОРИЙ В GITLAB (РЕКОМЕНДУЕТСЯ)**

#### **Step 1: Access GitLab**
1. **Open:** https://gitlab.trustforge.uk/
2. **Login:** Use root credentials
3. **Navigate:** Dashboard

#### **Step 2: Create New Project**
1. **Click:** "New project"
2. **Select:** "Create blank project"
3. **Configure:**
   - **Project name:** `ssl-monitor-pro`
   - **Project slug:** `ssl-monitor-pro`
   - **Visibility:** `Private` (initially)
   - **Initialize with README:** ✅

#### **Step 3: Import Code from GitHub**
1. **In new project:** Click "Import project"
2. **Select:** "GitHub"
3. **Enter GitHub URL:** `https://github.com/vlamay/ssl-monitor`
4. **Configure:**
   - **Project name:** `ssl-monitor-pro`
   - **Visibility:** `Private`
5. **Import:** Click "Import project"

#### **Step 4: Make Repository Public**
1. **Go to:** Project Settings → General
2. **Expand:** Visibility, project features, permissions
3. **Set:** Project visibility to `Public`
4. **Save changes**

#### **Step 5: Test Repository URL**
```bash
# Test public access
curl -I https://gitlab.trustforge.uk/root/ssl-monitor-pro.git

# Expected result: 200 OK or proper git response
```

---

### **2️⃣ АЛЬТЕРНАТИВНОЕ РЕШЕНИЕ: ИСПОЛЬЗОВАТЬ GITHUB**

#### **Temporary Solution:**
1. **Use GitHub URL in Render:**
   ```
   https://github.com/vlamay/ssl-monitor.git
   ```
2. **Configure deployment**
3. **Sync to GitLab later**

#### **Sync Script:**
```bash
# After GitLab repository is created
git remote add gitlab https://gitlab.trustforge.uk/root/ssl-monitor-pro.git
git push gitlab main
```

---

### **3️⃣ БЫСТРОЕ РЕШЕНИЕ: СОЗДАТЬ ЛОКАЛЬНО**

#### **Create Repository Locally:**
```bash
# In project directory
cd /home/vmaidaniuk/Cursor/ssl-monitor-final

# Initialize git if not exists
git init

# Add GitLab remote
git remote add origin https://gitlab.trustforge.uk/root/ssl-monitor-pro.git

# Push to GitLab
git add .
git commit -m "Initial commit"
git push -u origin main
```

---

## 🔧 **DETAILED SETUP STEPS**

### **Method 1: GitLab Web Interface (Recommended)**

#### **1. Login to GitLab**
- **URL:** https://gitlab.trustforge.uk/
- **Username:** `root`
- **Password:** (from GitLab installation)

#### **2. Create Project**
- **Name:** `ssl-monitor-pro`
- **Namespace:** `root`
- **Visibility:** `Private` → `Public`
- **Initialize:** With README

#### **3. Import from GitHub**
- **Source:** GitHub
- **Repository:** `vlamay/ssl-monitor`
- **Import:** All branches and tags

#### **4. Configure Repository**
- **Make Public:** For Render access
- **Set Webhooks:** For CI/CD
- **Configure Variables:** Environment variables

#### **5. Test Access**
```bash
# Test repository URL
curl -I https://gitlab.trustforge.uk/root/ssl-monitor-pro.git

# Clone repository
git clone https://gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

---

### **Method 2: Command Line Setup**

#### **1. Create Repository via GitLab API**
```bash
# Get GitLab access token (from GitLab settings)
GITLAB_TOKEN="your_access_token"

# Create project
curl -X POST \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ssl-monitor-pro",
    "visibility": "public",
    "initialize_with_readme": true
  }' \
  https://gitlab.trustforge.uk/api/v4/projects
```

#### **2. Push Local Code**
```bash
# Add GitLab remote
git remote add gitlab https://gitlab.trustforge.uk/root/ssl-monitor-pro.git

# Push code
git push gitlab main
```

---

## 🧪 **TESTING**

### **Repository Access Test:**
```bash
# Test 1: Repository exists
curl -I https://gitlab.trustforge.uk/root/ssl-monitor-pro.git

# Expected: 200 OK or git protocol response
# Not Expected: 302 redirect to login

# Test 2: Clone repository
git clone https://gitlab.trustforge.uk/root/ssl-monitor-pro.git test-clone

# Test 3: Render URL validation
# Should work in Render dashboard
```

### **Render Integration Test:**
1. **Update Render Repository URL:**
   ```
   https://gitlab.trustforge.uk/root/ssl-monitor-pro.git
   ```
2. **Test Connection:** Should validate successfully
3. **Deploy:** Should start deployment

---

## 🎯 **RECOMMENDED ACTION PLAN**

### **Immediate Steps:**
1. ✅ **Access GitLab:** https://gitlab.trustforge.uk/
2. ✅ **Login:** Use root credentials
3. ✅ **Create Project:** `ssl-monitor-pro`
4. ✅ **Import from GitHub:** `vlamay/ssl-monitor`
5. ✅ **Make Public:** For Render access

### **After Repository Creation:**
1. ✅ **Test URL:** Verify repository accessibility
2. ✅ **Update Render:** Use new GitLab URL
3. ✅ **Deploy:** Test deployment
4. ✅ **Verify:** GitLab CI/CD integration

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues:**

#### **1. Cannot Access GitLab**
```bash
# Check tunnel status
curl -I https://gitlab.trustforge.uk/

# Check cloudflared
sudo systemctl status cloudflared
```

#### **2. Repository Still Not Accessible**
- Verify repository is public
- Check GitLab project settings
- Ensure correct URL format

#### **3. Render Still Shows Invalid URL**
- Clear browser cache
- Try different browser
- Check URL format: must end with `.git`

---

## 📞 **SUPPORT**

### **Useful Commands:**
```bash
# Test GitLab access
curl -I https://gitlab.trustforge.uk/

# Test repository access
curl -I https://gitlab.trustforge.uk/root/ssl-monitor-pro.git

# Check tunnel status
sudo systemctl status cloudflared

# View tunnel logs
sudo journalctl -u cloudflared -f
```

### **Next Steps After Repository Creation:**
1. **Update Render:** Use GitLab URL
2. **Test Deployment:** Verify CI/CD
3. **Complete Migration:** Final verification

---

*Guide created: October 13, 2025*  
*GitLab URL: https://gitlab.trustforge.uk/*  
*Target Repository: ssl-monitor-pro*
