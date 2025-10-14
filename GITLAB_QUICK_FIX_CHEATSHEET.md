# 🚀 GITLAB QUICK FIX CHEATSHEET

## 🎯 **GOAL:** Make GitLab repository public for Render access

---

## 📋 **QUICK STEPS**

### **1. Login to GitLab**
```
https://gitlab.trustforge.uk/
Username: root
Password: [your GitLab root password]
```

### **2. Find Your Project**
Look for projects with names like:
- `ssl-monitor-pro`
- `ssl-monitor`
- `ssl-monitor-final`
- Any SSL-related project name

### **3. Open Project Settings**
- Click on your project
- Go to: **Settings** → **General**
- Expand: **"Visibility, project features, permissions"**

### **4. Make Public**
- **Project visibility:** Change from `Private` to `Public`
- Click **Save changes**

### **5. Copy Repository URL**
From GitLab project page:
- Click **Clone** button
- Copy **HTTPS** URL
- Should look like: `https://gitlab.trustforge.uk/root/[PROJECT-NAME].git`

### **6. Update Render**
- Go to: https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg
- **Settings** → **Repository**
- **Repository URL:** Paste the URL from step 5
- **Branch:** `main`
- **Save Changes**
- **Manual Deploy**

---

## 🧪 **TESTING**

### **Before Update:**
```bash
curl -I https://gitlab.trustforge.uk/root/[PROJECT-NAME].git
# Expected: 302 redirect to /users/sign_in (Private)
```

### **After Making Public:**
```bash
curl -I https://gitlab.trustforge.uk/root/[PROJECT-NAME].git
# Expected: 200 OK or git protocol response (Public)
```

---

## 🚨 **TROUBLESHOOTING**

### **Still Getting 302 Redirect?**
- Repository is still private
- Wrong project name
- GitLab cache - wait a few minutes

### **Can't Find Your Project?**
- Check different namespaces
- Look in different groups
- Create new project if missing

### **Render Still Shows Invalid URL?**
- Clear browser cache
- Try different browser
- Verify URL ends with `.git`

---

## 🎯 **EXPECTED RESULT**

After making repository public:
- ✅ Repository accessible without authentication
- ✅ Render accepts the URL
- ✅ Deployment starts successfully
- ✅ GitLab CI/CD integration works

---

## 📞 **SUPPORT LINKS**

- **GitLab:** https://gitlab.trustforge.uk/
- **Render Dashboard:** https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg
- **GitLab Projects:** https://gitlab.trustforge.uk/dashboard/projects

---

*Quick fix guide - October 13, 2025*
