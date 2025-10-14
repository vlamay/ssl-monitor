# ✅ GitLab Migration Checklist

## Quick reference for migrating SSL Monitor Pro to GitLab CE

---

## 🚀 Pre-Migration (30 minutes)

### Server Preparation
- [ ] VPS/Server ready (Ubuntu 20.04+, 4GB+ RAM, 2+ CPU cores)
- [ ] Public IP address noted: `_______________`
- [ ] SSH access working: `ssh root@your-ip`
- [ ] System updated: `sudo apt update && sudo apt upgrade -y`

### Domain & DNS
- [ ] Cloudflare account ready
- [ ] Domain `cloudsre.xyz` added to Cloudflare
- [ ] DNS A record created:
  - Type: A
  - Name: `gitlab`
  - IP: `your-server-ip`
  - Proxy: ⚪ DNS only (gray cloud - IMPORTANT!)

### GitHub Token
- [ ] GitHub Personal Access Token created
- [ ] Scopes selected: `repo` + `admin:org`
- [ ] Token saved: `ghp_________________`

---

## 📦 Installation (15 minutes)

### Option A: Automated Script
```bash
wget https://raw.githubusercontent.com/yourusername/ssl-monitor-final/main/gitlab-install.sh
chmod +x gitlab-install.sh
sudo bash gitlab-install.sh your-email@example.com
```

- [ ] Script downloaded
- [ ] Script executed successfully
- [ ] Root password saved: `_______________`

### Option B: Manual Installation
```bash
# 1. Add repository
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash

# 2. Install
sudo EXTERNAL_URL="https://gitlab.cloudsre.xyz" apt install gitlab-ce

# 3. Get password
sudo cat /etc/gitlab/initial_root_password
```

- [ ] Repository added
- [ ] GitLab installed
- [ ] Root password retrieved

---

## 🔒 SSL Configuration (10 minutes)

```bash
sudo nano /etc/gitlab/gitlab.rb
```

Add these lines:
```ruby
letsencrypt['enable'] = true
letsencrypt['contact_emails'] = ['your-email@example.com']
letsencrypt['auto_renew'] = true
```

```bash
sudo gitlab-ctl reconfigure
```

- [ ] Config file updated
- [ ] Reconfiguration completed
- [ ] SSL certificate obtained
- [ ] GitLab accessible via HTTPS: https://gitlab.cloudsre.xyz

---

## 🌐 Cloudflare Finalization (2 minutes)

- [ ] Cloudflare DNS record updated to 🟠 Proxied (orange cloud)
- [ ] SSL/TLS mode set to: **Full (strict)**
- [ ] GitLab still accessible after proxy enabled

---

## 📥 Repository Migration (20 minutes)

### GitLab Access
- [ ] Logged into https://gitlab.cloudsre.xyz
- [ ] Username: `root`
- [ ] Password changed to new secure password

### Import Project
- [ ] Clicked **New project → Import project → GitHub**
- [ ] GitHub token entered
- [ ] Repository `ssl-monitor-pro` found
- [ ] Import started
- [ ] Import completed successfully

### Verification
- [ ] All branches present
- [ ] All commits and history intact
- [ ] All tags migrated
- [ ] README visible
- [ ] Files structure correct

---

## 💻 Local Repository Update (5 minutes)

```bash
cd /path/to/ssl-monitor-final

# Update remote
git remote set-url origin https://gitlab.cloudsre.xyz/root/ssl-monitor-pro.git

# Verify
git remote -v

# Test push
git push origin main
```

- [ ] Remote URL updated
- [ ] Test push successful
- [ ] Can pull from new remote

---

## ⚙️ CI/CD Setup (15 minutes)

### .gitlab-ci.yml
- [ ] File `.gitlab-ci.yml` exists in repository
- [ ] File committed and pushed

### CI/CD Variables
Go to: **Settings → CI/CD → Variables**

Add these variables:

| Variable | Value | Masked | Protected |
|----------|-------|--------|-----------|
| `DATABASE_URL` | `postgresql://...` | ✅ | ✅ |
| `REDIS_URL` | `redis://...` | ✅ | ✅ |
| `SECRET_KEY` | `your-secret` | ✅ | ✅ |
| `STRIPE_SECRET_KEY` | `sk_live_...` | ✅ | ✅ |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` | ✅ | ✅ |
| `TELEGRAM_BOT_TOKEN` | `123456:ABC...` | ✅ | ✅ |
| `TELEGRAM_CHAT_ID` | `123456789` | ✅ | ✅ |

- [ ] All variables added
- [ ] All variables masked
- [ ] All variables protected

### Test Pipeline
- [ ] Push a test commit
- [ ] Pipeline triggered automatically
- [ ] All jobs completed successfully
- [ ] Deployment worked (if configured)

---

## 🔧 Post-Migration Configuration (30 minutes)

### GitLab Settings
- [ ] **Admin Area** → Create additional users if needed
- [ ] **Settings → Repository** → Branch protection rules set
- [ ] **Settings → CI/CD** → Runners enabled
- [ ] **Settings → Webhooks** → Configured (if needed)

### Project Configuration
- [ ] README updated with new GitLab URLs
- [ ] CONTRIBUTING.md updated
- [ ] Issue templates created
- [ ] Merge request templates created
- [ ] Project visibility set (Private/Internal/Public)

### Backup Setup
```bash
# Test backup
sudo gitlab-backup create

# Setup automated backups
sudo crontab -e
# Add: 0 2 * * * /opt/gitlab/bin/gitlab-backup create CRON=1
```

- [ ] Manual backup tested
- [ ] Automated backup scheduled
- [ ] Backup storage configured (S3/local)

---

## 🧪 Testing (15 minutes)

### Functionality Tests
- [ ] Clone repository from GitLab works
- [ ] Push changes works
- [ ] Create branch works
- [ ] Create merge request works
- [ ] CI/CD pipeline runs on push
- [ ] All pipeline stages pass

### Access Tests
- [ ] HTTPS works: https://gitlab.cloudsre.xyz
- [ ] SSH works (if configured)
- [ ] API accessible
- [ ] Webhooks functioning (if configured)

### Performance Tests
- [ ] GitLab loads in <5 seconds
- [ ] Git operations are fast
- [ ] Pipeline starts quickly
- [ ] No 502 errors

---

## 📊 Monitoring & Maintenance

### Health Check
```bash
sudo gitlab-ctl status        # All services running?
sudo gitlab-rake gitlab:check # Any issues?
```

- [ ] All services running
- [ ] No errors in health check
- [ ] Logs look normal: `sudo gitlab-ctl tail`

### Regular Maintenance Tasks
- [ ] Setup monitoring (Prometheus/Grafana)
- [ ] Configure email notifications
- [ ] Review security settings
- [ ] Plan update strategy
- [ ] Document custom configurations

---

## 📝 Documentation Updates

- [ ] Update project README with GitLab URLs
- [ ] Update deployment documentation
- [ ] Update CI/CD documentation
- [ ] Update team onboarding guide
- [ ] Create GitLab-specific guides

---

## 🎓 Team Onboarding

- [ ] Share new GitLab URL with team
- [ ] Create user accounts for team members
- [ ] Share login credentials securely
- [ ] Conduct GitLab training session
- [ ] Create internal wiki/docs on GitLab

---

## 🚨 Troubleshooting Reference

### GitLab won't start
```bash
sudo gitlab-ctl restart
sudo gitlab-ctl tail
```

### Let's Encrypt SSL fails
1. Disable Cloudflare proxy (gray cloud)
2. `sudo gitlab-ctl reconfigure`
3. Wait for SSL
4. Re-enable proxy

### Out of memory
```bash
sudo nano /etc/gitlab/gitlab.rb
# Reduce: puma['worker_processes'] = 2
sudo gitlab-ctl reconfigure
```

### Import fails
Use URL method:
```
https://github.com/username/repo.git
```

---

## 📞 Emergency Contacts

**Server Provider Support:** `_______________`  
**Domain Registrar:** Cloudflare  
**Team Lead:** `_______________`  
**DevOps Contact:** vla.maidaniuk@gmail.com  

---

## ✨ Success Criteria

Migration is successful when:

- ✅ GitLab accessible at https://gitlab.cloudsre.xyz
- ✅ All code, branches, and tags migrated
- ✅ CI/CD pipeline working
- ✅ Team can clone/push/pull
- ✅ SSL certificate valid
- ✅ Backups configured
- ✅ No data loss
- ✅ Performance acceptable
- ✅ Documentation updated
- ✅ Team trained and onboarded

---

## 🎉 Post-Migration Celebration

Once all checkboxes are ticked:

1. ✅ Announce migration success to team
2. ✅ Archive old GitHub repository (optional)
3. ✅ Update all external references
4. ✅ Celebrate! 🎊

---

## 📅 Timeline Summary

| Phase | Duration | Total Time |
|-------|----------|------------|
| Pre-Migration | 30 min | 0:30 |
| Installation | 15 min | 0:45 |
| SSL Setup | 10 min | 0:55 |
| Repository Migration | 20 min | 1:15 |
| CI/CD Setup | 15 min | 1:30 |
| Post-Configuration | 30 min | 2:00 |
| Testing | 15 min | 2:15 |

**Total Estimated Time: 2-3 hours**

---

## 📚 Additional Resources

- [Full Migration Guide](GITLAB_MIGRATION_GUIDE.md)
- [Installation Script](gitlab-install.sh)
- [GitLab Documentation](https://docs.gitlab.com/)
- [SSL Monitor Pro Docs](README.md)

---

**Generated:** October 12, 2025  
**Version:** 1.0  
**Project:** SSL Monitor Pro  
**Domain:** gitlab.cloudsre.xyz

---

**Pro Tip:** Print this checklist and tick boxes with a pen as you progress! 📋✍️

