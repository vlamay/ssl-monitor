#!/bin/bash
#
# GitLab CE Installation Script for Ubuntu
# Domain: gitlab.cloudsre.xyz
# SSL: Let's Encrypt via GitLab
# Cloudflare: DNS-only initially, then proxied
#
# Usage: sudo bash gitlab-install.sh your-email@example.com
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
GITLAB_DOMAIN="gitlab.cloudsre.xyz"
EMAIL="${1:-admin@cloudsre.xyz}"

echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}  GitLab CE Installation Script${NC}"
echo -e "${GREEN}  Domain: $GITLAB_DOMAIN${NC}"
echo -e "${GREEN}  Email: $EMAIL${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root${NC}" 
   echo "Usage: sudo bash gitlab-install.sh your-email@example.com"
   exit 1
fi

# Step 1: System Update
echo -e "${YELLOW}[1/8] Updating system...${NC}"
apt update && apt upgrade -y

# Step 2: Install Dependencies
echo -e "${YELLOW}[2/8] Installing dependencies...${NC}"
apt install -y curl openssh-server ca-certificates tzdata perl postfix

# Configure postfix
echo "postfix postfix/main_mailer_type select Internet Site" | debconf-set-selections
echo "postfix postfix/mailname string $GITLAB_DOMAIN" | debconf-set-selections

# Step 3: Configure Firewall (if UFW is active)
echo -e "${YELLOW}[3/8] Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow http
    ufw allow https
    ufw allow OpenSSH
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    echo "UFW rules added"
else
    echo "UFW not installed, skipping firewall configuration"
fi

# Step 4: Add GitLab Repository
echo -e "${YELLOW}[4/8] Adding GitLab repository...${NC}"
curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | bash

# Step 5: Install GitLab CE
echo -e "${YELLOW}[5/8] Installing GitLab CE (this may take several minutes)...${NC}"
EXTERNAL_URL="https://$GITLAB_DOMAIN" apt install -y gitlab-ce

# Step 6: Configure GitLab with Let's Encrypt
echo -e "${YELLOW}[6/8] Configuring GitLab with SSL...${NC}"

# Backup original config
cp /etc/gitlab/gitlab.rb /etc/gitlab/gitlab.rb.backup

# Configure SSL
cat >> /etc/gitlab/gitlab.rb << EOF

# SSL Configuration via Let's Encrypt
letsencrypt['enable'] = true
letsencrypt['contact_emails'] = ['$EMAIL']
letsencrypt['auto_renew'] = true
letsencrypt['auto_renew_hour'] = 0
letsencrypt['auto_renew_minute'] = 30
letsencrypt['auto_renew_day_of_month'] = "*/4"

# Performance Settings
postgresql['shared_buffers'] = "256MB"
postgresql['max_worker_processes'] = 8
sidekiq['max_concurrency'] = 10

# Backup Settings
gitlab_rails['backup_keep_time'] = 604800  # 7 days

# Email Settings (using Postfix)
gitlab_rails['smtp_enable'] = true
gitlab_rails['smtp_address'] = "localhost"
gitlab_rails['smtp_port'] = 25
gitlab_rails['smtp_domain'] = "$GITLAB_DOMAIN"
gitlab_rails['smtp_authentication'] = false
gitlab_rails['smtp_enable_starttls_auto'] = false
gitlab_rails['smtp_tls'] = false
gitlab_rails['smtp_openssl_verify_mode'] = 'none'
gitlab_rails['gitlab_email_from'] = "gitlab@$GITLAB_DOMAIN"
gitlab_rails['gitlab_email_reply_to'] = "noreply@$GITLAB_DOMAIN"

# Security
nginx['redirect_http_to_https'] = true
nginx['ssl_protocols'] = "TLSv1.2 TLSv1.3"
EOF

# Step 7: Reconfigure GitLab
echo -e "${YELLOW}[7/8] Running GitLab reconfiguration (this will take several minutes)...${NC}"
gitlab-ctl reconfigure

# Step 8: Get root password
echo -e "${YELLOW}[8/8] Retrieving root password...${NC}"
sleep 5

echo ""
echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}  GitLab Installation Complete!${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""
echo -e "${GREEN}🎉 GitLab URL:${NC} https://$GITLAB_DOMAIN"
echo -e "${GREEN}👤 Username:${NC} root"
echo ""

if [ -f /etc/gitlab/initial_root_password ]; then
    ROOT_PASSWORD=$(grep 'Password:' /etc/gitlab/initial_root_password | awk '{print $2}')
    echo -e "${GREEN}🔑 Root Password:${NC} $ROOT_PASSWORD"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Save this password! This file will be deleted in 24 hours.${NC}"
else
    echo -e "${YELLOW}⚠️  Password file not found. Check /etc/gitlab/initial_root_password manually${NC}"
fi

echo ""
echo -e "${GREEN}📋 Next Steps:${NC}"
echo "1. ✅ GitLab is installed and running"
echo "2. 🌐 Open https://$GITLAB_DOMAIN in your browser"
echo "3. 🔐 Login with username 'root' and the password above"
echo "4. 🔄 Go to Cloudflare DNS and enable Proxy (orange cloud) for $GITLAB_DOMAIN"
echo "5. 📦 Import your repository from GitHub"
echo ""
echo -e "${GREEN}Useful Commands:${NC}"
echo "  gitlab-ctl status          # Check GitLab status"
echo "  gitlab-ctl restart         # Restart all services"
echo "  gitlab-ctl tail            # View logs"
echo "  gitlab-rake gitlab:check   # Run health check"
echo "  gitlab-backup create       # Create backup"
echo ""
echo -e "${GREEN}Configuration file:${NC} /etc/gitlab/gitlab.rb"
echo -e "${GREEN}Backup location:${NC} /etc/gitlab/gitlab.rb.backup"
echo ""
echo -e "${GREEN}Installation log saved to:${NC} /var/log/gitlab/gitlab-install.log"
echo ""

