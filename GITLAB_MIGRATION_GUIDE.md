# 🚀 GitLab Migration Guide: GitHub → GitLab CE

## SSL Monitor Pro Migration to Self-Hosted GitLab

**Domain:** `gitlab.cloudsre.xyz`  
**Provider:** Cloudflare DNS + Let's Encrypt SSL  
**Source:** GitHub (private repository)  
**Target:** GitLab CE (self-hosted)

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Part 1: Server Preparation](#part-1-server-preparation)
3. [Part 2: Cloudflare DNS Setup](#part-2-cloudflare-dns-setup)
4. [Part 3: GitLab Installation](#part-3-gitlab-installation)
5. [Part 4: Repository Migration](#part-4-repository-migration)
6. [Part 5: CI/CD Configuration](#part-5-cicd-configuration)
7. [Part 6: Post-Migration Tasks](#part-6-post-migration-tasks)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Server Requirements

- **OS:** Ubuntu 20.04 LTS or newer
- **RAM:** Minimum 4GB (8GB recommended)
- **CPU:** 2 cores minimum (4 cores recommended)
- **Storage:** 20GB+ free space
- **Network:** Public IP address
- **Access:** Root or sudo privileges

### What You'll Need

- ✅ VPS/Server with Ubuntu
- ✅ Domain name (cloudsre.xyz)
- ✅ Cloudflare account with domain configured
- ✅ GitHub Personal Access Token
- ✅ SSH access to your server

---

## Part 1: Server Preparation

### 1.1 Connect to Your Server

```bash
ssh root@your-server-ip
# Or with sudo user:
ssh username@your-server-ip
```

### 1.2 Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 Set Hostname (Optional but Recommended)

```bash
sudo hostnamectl set-hostname gitlab
sudo nano /etc/hosts
```

Add this line:
```
127.0.0.1 gitlab.cloudsre.xyz gitlab
```

### 1.4 Check System Resources

```bash
# Check available RAM
free -h

# Check disk space
df -h

# Check CPU
nproc
```

**Minimum Requirements:**
- RAM: 4GB+
- Disk: 10GB+ free
- CPU: 2+ cores

---

## Part 2: Cloudflare DNS Setup

### 2.1 Login to Cloudflare

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select your domain: **cloudsre.xyz**

### 2.2 Create DNS Record

**Navigate to:** DNS → Records → Add record

**Configuration:**
```
Type:    A
Name:    gitlab
Content: YOUR_SERVER_IP
TTL:     Auto
Proxy:   DNS only (gray cloud) ← IMPORTANT for initial setup
```

**Example:**
```
Type: A
Name: gitlab
IPv4: 185.123.45.67
Proxy: DNS only (🌐 gray cloud)
```

Click **Save**.

### 2.3 Verify DNS Propagation

Wait 2-5 minutes, then test:

```bash
# From your local machine
dig gitlab.cloudsre.xyz

# Or
nslookup gitlab.cloudsre.xyz
```

You should see your server's IP address.

---

## Part 3: GitLab Installation

### Option A: Automated Installation (Recommended)

Use the provided installation script:

```bash
# Download the script
wget https://raw.githubusercontent.com/yourusername/ssl-monitor-final/main/gitlab-install.sh

# Make it executable
chmod +x gitlab-install.sh

# Run the installation
sudo bash gitlab-install.sh your-email@example.com
```

The script will:
- ✅ Update system
- ✅ Install dependencies
- ✅ Configure firewall
- ✅ Install GitLab CE
- ✅ Setup Let's Encrypt SSL
- ✅ Show root password

**Installation time:** 10-15 minutes

### Option B: Manual Installation

#### Step 1: Install Dependencies

```bash
sudo apt install -y curl openssh-server ca-certificates tzdata perl postfix
```

When prompted for Postfix configuration:
- Select: **Internet Site**
- System mail name: **gitlab.cloudsre.xyz**

#### Step 2: Add GitLab Repository

```bash
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
```

#### Step 3: Install GitLab CE

```bash
sudo EXTERNAL_URL="https://gitlab.cloudsre.xyz" apt install -y gitlab-ce
```

This takes 5-10 minutes.

#### Step 4: Configure Let's Encrypt SSL

Edit GitLab configuration:

```bash
sudo nano /etc/gitlab/gitlab.rb
```

Add/modify these lines:

```ruby
external_url 'https://gitlab.cloudsre.xyz'

# Let's Encrypt SSL
letsencrypt['enable'] = true
letsencrypt['contact_emails'] = ['your-email@example.com']
letsencrypt['auto_renew'] = true
letsencrypt['auto_renew_hour'] = 0
letsencrypt['auto_renew_minute'] = 30
letsencrypt['auto_renew_day_of_month'] = "*/4"

# Security
nginx['redirect_http_to_https'] = true
nginx['ssl_protocols'] = "TLSv1.2 TLSv1.3"
```

#### Step 5: Reconfigure GitLab

```bash
sudo gitlab-ctl reconfigure
```

This takes 5-10 minutes.

#### Step 6: Get Root Password

```bash
sudo cat /etc/gitlab/initial_root_password
```

**⚠️ IMPORTANT:** Save this password immediately! The file will be deleted after 24 hours.

---

## Part 4: Repository Migration

### 4.1 Access GitLab

1. Open browser: `https://gitlab.cloudsre.xyz`
2. Login with:
   - **Username:** `root`
   - **Password:** (from previous step)

### 4.2 Change Root Password

1. Click profile icon → **Preferences**
2. Navigate to **Password**
3. Set a new, secure password

### 4.3 Create GitHub Personal Access Token

1. Go to [GitHub Settings → Developer settings](https://github.com/settings/tokens)
2. Click **Personal access tokens → Tokens (classic)**
3. Click **Generate new token (classic)**
4. Configure:
   - **Note:** `GitLab Migration`
   - **Expiration:** 7 days (for migration only)
   - **Scopes:** Check these:
     - ✅ `repo` (all)
     - ✅ `admin:org` (read:org only if migrating org repos)
5. Click **Generate token**
6. **⚠️ Copy the token immediately!** You won't see it again.

### 4.4 Import Repository from GitHub

#### Method 1: Using GitLab GitHub Integration (Recommended)

1. In GitLab, click **New project**
2. Click **Import project** tab
3. Click **GitHub**
4. Paste your GitHub Personal Access Token
5. Click **List GitHub repositories**
6. Find **ssl-monitor-pro** (or your repository name)
7. Click **Import**
8. Wait for import to complete (5-15 minutes depending on repo size)

#### Method 2: Import by URL

If Method 1 doesn't work:

1. Click **New project**
2. Click **Import project**
3. Click **Repository by URL**
4. Enter:
   ```
   Git repository URL: https://github.com/yourusername/ssl-monitor-pro.git
   Username: your-github-username
   Password: your-personal-access-token
   ```
5. Set **Project name:** `ssl-monitor-pro`
6. Click **Create project**

### 4.5 Verify Migration

Check that all these were migrated:

- ✅ All branches
- ✅ All commits and history
- ✅ All tags
- ✅ README and documentation

**Note:** GitLab CI/CD workflows (`.github/workflows/`) will NOT work. You need to migrate to GitLab CI/CD (`.gitlab-ci.yml`).

### 4.6 Update Local Repository

On your local machine:

```bash
cd /path/to/ssl-monitor-pro

# Add GitLab as new remote
git remote add gitlab https://gitlab.cloudsre.xyz/root/ssl-monitor-pro.git

# Or replace origin
git remote set-url origin https://gitlab.cloudsre.xyz/root/ssl-monitor-pro.git

# Verify
git remote -v

# Push all branches
git push gitlab --all

# Push all tags
git push gitlab --tags
```

---

## Part 5: CI/CD Configuration

### 5.1 Add .gitlab-ci.yml

The project already has `.gitlab-ci.yml` file. Verify it exists:

```bash
ls -la .gitlab-ci.yml
```

### 5.2 Configure CI/CD Variables

In GitLab:

1. Go to **Settings → CI/CD → Variables**
2. Click **Add variable**
3. Add these secrets (from your current production):

```
DATABASE_URL          = postgresql://...
REDIS_URL             = redis://...
SECRET_KEY            = your-secret-key
STRIPE_SECRET_KEY     = sk_live_...
STRIPE_WEBHOOK_SECRET = whsec_...
TELEGRAM_BOT_TOKEN    = 123456:ABC...
TELEGRAM_CHAT_ID      = 123456789
```

**Settings for each variable:**
- **Protect variable:** ✅ (for production)
- **Mask variable:** ✅ (hide in logs)
- **Expand variable:** ❌

### 5.3 Configure GitLab Runner

#### Check if Runner is Available

Go to **Settings → CI/CD → Runners**

If you see "Shared runners are enabled", you're good!

#### Install Your Own Runner (Optional)

If you need a dedicated runner on the same server:

```bash
# Download
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash

# Install
sudo apt install gitlab-runner

# Register runner
sudo gitlab-runner register \
  --url https://gitlab.cloudsre.xyz/ \
  --registration-token YOUR_REGISTRATION_TOKEN \
  --executor docker \
  --docker-image python:3.11
```

Get `YOUR_REGISTRATION_TOKEN` from **Settings → CI/CD → Runners → Specific runners**.

---

## Part 6: Post-Migration Tasks

### 6.1 Enable Cloudflare Proxy

Now that SSL is working:

1. Go to **Cloudflare Dashboard → DNS**
2. Find the `gitlab` A record
3. Click the cloud icon to turn it **orange** (Proxied)
4. This will:
   - Hide your server IP
   - Add DDoS protection
   - Enable Cloudflare caching

### 6.2 Configure Cloudflare SSL Settings

Go to **SSL/TLS → Overview**

Set SSL/TLS encryption mode: **Full (strict)**

### 6.3 Create GitLab Users/Team

1. Go to **Admin Area → Users → New user**
2. Create accounts for your team
3. Assign appropriate roles

### 6.4 Setup Backup Strategy

Enable automated backups:

```bash
sudo nano /etc/gitlab/gitlab.rb
```

Add:

```ruby
# Backup settings
gitlab_rails['backup_keep_time'] = 604800  # 7 days
gitlab_rails['backup_upload_connection'] = {
  'provider' => 'AWS',
  'region' => 'eu-central-1',
  'aws_access_key_id' => 'YOUR_KEY',
  'aws_secret_access_key' => 'YOUR_SECRET'
}
gitlab_rails['backup_upload_remote_directory'] = 'gitlab-backups'
```

Reconfigure:

```bash
sudo gitlab-ctl reconfigure
```

Create cron job for daily backups:

```bash
sudo crontab -e
```

Add:

```
0 2 * * * /opt/gitlab/bin/gitlab-backup create CRON=1
```

### 6.5 Setup Monitoring

Check GitLab health:

```bash
sudo gitlab-rake gitlab:check
```

View logs:

```bash
sudo gitlab-ctl tail
```

### 6.6 Update Documentation

Update your project's README and docs to reflect:
- New repository URL
- GitLab-specific instructions
- CI/CD pipeline details

---

## Troubleshooting

### Issue: GitLab is Slow

**Solution:**

```bash
# Increase resources in config
sudo nano /etc/gitlab/gitlab.rb
```

Add:

```ruby
postgresql['shared_buffers'] = "512MB"
puma['worker_processes'] = 4
sidekiq['max_concurrency'] = 20
```

Reconfigure:

```bash
sudo gitlab-ctl reconfigure
```

### Issue: Let's Encrypt SSL Fails

**Reason:** Cloudflare proxy is blocking Let's Encrypt verification.

**Solution:**

1. Disable Cloudflare proxy (gray cloud)
2. Reconfigure GitLab: `sudo gitlab-ctl reconfigure`
3. Wait for SSL to be issued
4. Re-enable Cloudflare proxy (orange cloud)

### Issue: Can't Access GitLab After Installation

**Check:**

```bash
# Check if GitLab is running
sudo gitlab-ctl status

# Restart if needed
sudo gitlab-ctl restart

# Check Nginx logs
sudo gitlab-ctl tail nginx
```

### Issue: Import from GitHub Fails

**Solution:**

1. Use "Import by URL" method instead
2. Make sure GitHub token has correct permissions
3. Try cloning locally and pushing:

```bash
git clone https://github.com/username/repo.git
cd repo
git remote add gitlab https://gitlab.cloudsre.xyz/root/repo.git
git push gitlab --all
git push gitlab --tags
```

### Issue: Out of Memory

GitLab requires minimum 4GB RAM. If you have less:

```bash
# Reduce GitLab's memory footprint
sudo nano /etc/gitlab/gitlab.rb
```

Add:

```ruby
puma['worker_processes'] = 2
sidekiq['max_concurrency'] = 5
postgresql['shared_buffers'] = "128MB"
```

### Issue: 502 Error After Installation

**Wait 5-10 minutes** for all services to start, then:

```bash
sudo gitlab-ctl restart
```

---

## Useful Commands

```bash
# Check GitLab status
sudo gitlab-ctl status

# Restart all services
sudo gitlab-ctl restart

# Restart specific service
sudo gitlab-ctl restart nginx

# View all logs
sudo gitlab-ctl tail

# View specific service logs
sudo gitlab-ctl tail nginx

# Run health check
sudo gitlab-rake gitlab:check

# Create backup
sudo gitlab-backup create

# Restore backup
sudo gitlab-backup restore BACKUP=timestamp_of_backup

# Reconfigure after config change
sudo gitlab-ctl reconfigure

# Check GitLab version
sudo gitlab-rake gitlab:env:info

# Update GitLab
sudo apt update && sudo apt install gitlab-ce
```

---

## Next Steps After Migration

1. ✅ **Test CI/CD Pipeline** - Push a commit and verify pipeline runs
2. ✅ **Setup Branch Protection** - Protect main/production branches
3. ✅ **Configure Webhooks** - Setup notifications (Slack, Discord, etc.)
4. ✅ **Enable Container Registry** - For Docker images
5. ✅ **Setup GitLab Pages** - For project documentation
6. ✅ **Configure Issue Tracking** - Create issue templates
7. ✅ **Setup Merge Request Templates** - Standardize PR process
8. ✅ **Enable Code Quality** - Add code analysis to pipeline
9. ✅ **Setup Monitoring** - Configure Prometheus/Grafana
10. ✅ **Team Training** - Onboard team to GitLab

---

## Resources

- **GitLab Docs:** https://docs.gitlab.com/
- **GitLab CI/CD:** https://docs.gitlab.com/ee/ci/
- **Migration Guide:** https://docs.gitlab.com/ee/user/project/import/github.html
- **GitLab API:** https://docs.gitlab.com/ee/api/
- **Community Forum:** https://forum.gitlab.com/

---

## Support

**Repository Issues:** https://gitlab.cloudsre.xyz/root/ssl-monitor-pro/-/issues  
**Email:** vla.maidaniuk@gmail.com  
**GitLab Status:** https://status.gitlab.com/

---

**🎉 Congratulations! Your project is now running on self-hosted GitLab!**

Built with ❤️ for open source community

