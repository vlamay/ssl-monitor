# 🚀 RENDER DEPLOY TOKEN UPDATE

## 🎉 **DEPLOY TOKEN CREATED SUCCESSFULLY!**

### **Token Details:**
- **Username:** `gitlab+deploy-token-[ID]` *(need exact ID)*
- **Token:** `gldt-hcsKEuf3uzkuszrPKoYU`
- **Repository:** `ssl-monitor-pro`

---

## 🔍 **STEP 1: GET EXACT USERNAME**

### **In GitLab:**
1. **Go to:** https://gitlab.trustforge.uk/root/ssl-monitor-pro/-/settings/repository
2. **Find:** Deploy tokens section
3. **Look for:** Your token `gldt-hcsKEuf3uzkuszrPKoYU`
4. **Copy:** The exact username (format: `gitlab+deploy-token-[NUMBER]`)

### **Example Username:**
```
gitlab+deploy-token-12345
```

---

## 🔧 **STEP 2: UPDATE RENDER**

### **Repository URL Format:**
```
https://[EXACT_USERNAME]:[TOKEN]@gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

### **Example URL:**
```
https://gitlab+deploy-token-12345:gldt-hcsKEuf3uzkuszrPKoYU@gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

### **Render Dashboard Steps:**
1. **Open:** https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg
2. **Go to:** Settings → Repository
3. **Update Repository URL:** Paste the complete URL above
4. **Set Branch:** `main`
5. **Click:** Save Changes
6. **Click:** Manual Deploy

---

## 🧪 **STEP 3: TEST TOKEN**

### **Test Command:**
```bash
# Replace [EXACT_USERNAME] with the real username from GitLab
curl -I https://[EXACT_USERNAME]:gldt-hcsKEuf3uzkuszrPKoYU@gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

### **Expected Result:**
- ✅ **200 OK** or git protocol response
- ❌ **NOT** 302 redirect to login

---

## 🎯 **COMPLETE URL TEMPLATE**

### **For Render Repository URL:**
```
https://gitlab+deploy-token-[ID]:gldt-hcsKEuf3uzkuszrPKoYU@gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

### **Replace [ID] with the actual number from GitLab**

---

## 🚨 **TROUBLESHOOTING**

### **If Render Still Shows "Invalid URL":**
1. **Check Username:** Make sure you have the exact username with ID
2. **Check Token:** Verify token is correct: `gldt-hcsKEuf3uzkuszrPKoYU`
3. **Check Format:** Ensure URL format is exactly as shown
4. **Test Manually:** Use curl command to test access

### **If Token Not Working:**
1. **Check Token Permissions:** Ensure `read_repository` scope
2. **Check Token Expiry:** Verify token is not expired
3. **Check Repository Access:** Ensure token has access to the repo

---

## ✅ **SUCCESS CRITERIA**

### **After Update:**
- ✅ **Render accepts the URL**
- ✅ **Repository connection successful**
- ✅ **Deployment starts automatically**
- ✅ **GitLab CI/CD integration works**

---

## 📞 **SUPPORT LINKS**

### **GitLab:**
- **Project:** https://gitlab.trustforge.uk/root/ssl-monitor-pro
- **Deploy Tokens:** https://gitlab.trustforge.uk/root/ssl-monitor-pro/-/settings/repository

### **Render:**
- **Dashboard:** https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg
- **Service Settings:** https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg/settings

---

## 🎯 **QUICK CHECKLIST**

- [ ] Get exact username from GitLab deploy tokens
- [ ] Construct complete URL with token
- [ ] Update Render repository URL
- [ ] Set branch to `main`
- [ ] Save changes in Render
- [ ] Trigger manual deploy
- [ ] Verify deployment starts successfully

---

## 🚀 **EXPECTED RESULT**

After successful update:
- ✅ **Render connects to GitLab**
- ✅ **Deployment from GitLab starts**
- ✅ **GitLab CI/CD pipeline triggers**
- ✅ **Full GitLab migration complete**

---

*Deploy Token Update Guide - October 13, 2025*  
*Token: gldt-hcsKEuf3uzkuszrPKoYU*  
*Repository: ssl-monitor-pro*
