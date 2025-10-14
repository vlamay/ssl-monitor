# 🚀 RENDER CORRECT SETUP GUIDE

## 🚨 **ERROR IDENTIFIED: WRONG LOCATION!**

### **❌ Current Issue:**
- Deploy token added to **Environment Variables**
- Should be in **Repository URL** instead
- Environment variable names cannot contain `+` symbol

---

## 🔧 **CORRECT SOLUTION**

### **Step 1: Remove Environment Variable**
1. **In Render Dashboard:** Environment Variables section
2. **Find:** `gitlab+deploy-token-[ID]` variable
3. **Click:** Trash icon (🗑️) to delete it
4. **Confirm:** Deletion

### **Step 2: Navigate to Repository Settings**
1. **In Render Dashboard:** Go to **Settings**
2. **Click:** **Repository** (NOT Environment Variables)
3. **Find:** Repository URL field

### **Step 3: Update Repository URL**
**Use this format:**
```
https://gitlab+deploy-token-[ID]:gldt-hcsKEuf3uzkuszrPKoYU@gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

**Steps:**
1. **Clear** existing Repository URL
2. **Paste** the URL above (replace `[ID]` with actual ID)
3. **Set Branch:** `main`
4. **Save Changes**
5. **Manual Deploy**

---

## 🎯 **CORRECT LOCATIONS**

### **✅ Repository URL (CORRECT):**
- **Location:** Settings → Repository → Repository URL
- **Purpose:** Tell Render where to pull code from
- **Format:** `https://username:token@gitlab.com/repo.git`

### **❌ Environment Variables (WRONG):**
- **Location:** Settings → Environment
- **Purpose:** Set runtime environment variables
- **Cannot contain:** Special characters like `+`, `@`, etc.

---

## 🔍 **GET EXACT USERNAME**

### **From GitLab:**
1. **Go to:** https://gitlab.trustforge.uk/root/ssl-monitor-pro/-/settings/repository
2. **Find:** Deploy tokens section
3. **Look for:** Token `gldt-hcsKEuf3uzkuszrPKoYU`
4. **Copy:** Exact username (format: `gitlab+deploy-token-[NUMBER]`)

### **Example:**
```
Username: gitlab+deploy-token-12345
Token: gldt-hcsKEuf3uzkuszrPKoYU
```

---

## 📋 **FINAL REPOSITORY URL**

### **Complete URL Template:**
```
https://gitlab+deploy-token-[ACTUAL_ID]:gldt-hcsKEuf3uzkuszrPKoYU@gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

### **Example with Real ID:**
```
https://gitlab+deploy-token-12345:gldt-hcsKEuf3uzkuszrPKoYU@gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

---

## 🧪 **TESTING**

### **Test Repository URL:**
```bash
# Test the complete URL (replace with actual ID)
curl -I https://gitlab+deploy-token-[ID]:gldt-hcsKEuf3uzkuszrPKoYU@gitlab.trustforge.uk/root/ssl-monitor-pro.git

# Expected: 200 OK or git protocol response
# Not Expected: 302 redirect to login
```

---

## ✅ **SUCCESS CHECKLIST**

- [ ] ❌ **Delete** environment variable `gitlab+deploy-token-[ID]`
- [ ] ✅ **Navigate** to Settings → Repository
- [ ] ✅ **Get exact** username from GitLab deploy tokens
- [ ] ✅ **Update** Repository URL with complete URL
- [ ] ✅ **Set branch** to `main`
- [ ] ✅ **Save changes**
- [ ] ✅ **Manual deploy**
- [ ] ✅ **Verify** deployment starts

---

## 🚨 **COMMON MISTAKES TO AVOID**

### **❌ Don't:**
- Add deploy token to Environment Variables
- Use special characters in environment variable names
- Forget to replace `[ID]` with actual number
- Put token in wrong location

### **✅ Do:**
- Put deploy token in Repository URL
- Use exact username from GitLab
- Test URL before saving
- Verify deployment starts

---

## 🎯 **EXPECTED RESULT**

After correct setup:
- ✅ **Repository URL** contains deploy token
- ✅ **Environment Variables** clean (no deploy token)
- ✅ **Render connects** to GitLab successfully
- ✅ **Deployment starts** from GitLab
- ✅ **GitLab CI/CD** integration works

---

## 📞 **SUPPORT LINKS**

### **Render:**
- **Repository Settings:** https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg/settings
- **Environment Variables:** https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg/environment

### **GitLab:**
- **Deploy Tokens:** https://gitlab.trustforge.uk/root/ssl-monitor-pro/-/settings/repository

---

*Correct Setup Guide - October 13, 2025*  
*Fix: Move deploy token from Environment Variables to Repository URL*
