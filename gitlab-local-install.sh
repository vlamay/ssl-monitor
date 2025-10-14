#!/bin/bash
#
# GitLab CE Installation Script for Local Development
# Domain: gitlab.local (или ваш локальный IP)
# Email: sre.engineer.vm@gmail.com
#
# Usage: bash gitlab-local-install.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
LOCAL_IP="192.168.1.10"
EMAIL="sre.engineer.vm@gmail.com"

echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}  GitLab CE Local Installation Script${NC}"
echo -e "${GREEN}  Local IP: $LOCAL_IP${NC}"
echo -e "${GREEN}  Email: $EMAIL${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Error: Do not run this script as root on your laptop${NC}" 
   echo "This script will use sudo when needed"
   exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: GitLab requires significant resources${NC}"
echo -e "${YELLOW}   Minimum: 4GB RAM, 2 CPU cores, 10GB disk${NC}"
echo -e "${YELLOW}   This will install on your laptop: $LOCAL_IP${NC}"
echo ""

read -p "Continue with installation? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 1
fi

# Step 1: System Update
echo -e "${YELLOW}[1/8] Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

# Step 2: Install Dependencies
echo -e "${YELLOW}[2/8] Installing dependencies...${NC}"
sudo apt install -y curl openssh-server ca-certificates tzdata perl postfix

# Configure postfix
echo "postfix postfix/main_mailer_type select Internet Site" | sudo debconf-set-selections
echo "postfix postfix/mailname string gitlab.local" | sudo debconf-set-selections

# Step 3: Configure Firewall (if UFW is active)
echo -e "${YELLOW}[3/8] Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    sudo ufw allow http
    sudo ufw allow https
    sudo ufw allow OpenSSH
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 22/tcp
    echo "UFW rules added"
else
    echo "UFW not installed, skipping firewall configuration"
fi

# Step 4: Add GitLab Repository
echo -e "${YELLOW}[4/8] Adding GitLab repository...${NC}"
curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash

# Step 5: Install GitLab CE
echo -e "${YELLOW}[5/8] Installing GitLab CE (this may take several minutes)...${NC}"
EXTERNAL_URL="http://$LOCAL_IP" sudo apt install -y gitlab-ce

# Step 6: Configure GitLab for local development
echo -e "${YELLOW}[6/8] Configuring GitLab for local development...${NC}"

# Backup original config
sudo cp /etc/gitlab/gitlab.rb /etc/gitlab/gitlab.rb.backup

# Configure for local development
sudo tee -a /etc/gitlab/gitlab.rb << EOF

# Local Development Configuration
external_url 'http://$LOCAL_IP'

# Disable Let's Encrypt for local development
letsencrypt['enable'] = false

# Use HTTP for local development
nginx['redirect_http_to_https'] = false

# Performance Settings for local development
postgresql['shared_buffers'] = "128MB"
postgresql['max_worker_processes'] = 4
sidekiq['max_concurrency'] = 5

# Backup Settings
gitlab_rails['backup_keep_time'] = 604800  # 7 days

# Email Settings (using Postfix)
gitlab_rails['smtp_enable'] = true
gitlab_rails['smtp_address'] = "localhost"
gitlab_rails['smtp_port'] = 25
gitlab_rails['smtp_domain'] = "gitlab.local"
gitlab_rails['smtp_authentication'] = false
gitlab_rails['smtp_enable_starttls_auto'] = false
gitlab_rails['smtp_tls'] = false
gitlab_rails['smtp_openssl_verify_mode'] = 'none'
gitlab_rails['gitlab_email_from'] = "gitlab@gitlab.local"
gitlab_rails['gitlab_email_reply_to'] = "noreply@gitlab.local"

# Security (relaxed for local development)
nginx['ssl_protocols'] = "TLSv1.2 TLSv1.3"
EOF

# Step 7: Reconfigure GitLab
echo -e "${YELLOW}[7/8] Running GitLab reconfiguration (this will take several minutes)...${NC}"
sudo gitlab-ctl reconfigure

# Step 8: Get root password
echo -e "${YELLOW}[8/8] Retrieving root password...${NC}"
sleep 5

echo ""
echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}  GitLab Local Installation Complete!${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""
echo -e "${GREEN}🎉 GitLab URL:${NC} http://$LOCAL_IP"
echo -e "${GREEN}👤 Username:${NC} root"
echo ""

if [ -f /etc/gitlab/initial_root_password ]; then
    ROOT_PASSWORD=$(sudo grep 'Password:' /etc/gitlab/initial_root_password | awk '{print $2}')
    echo -e "${GREEN}🔑 Root Password:${NC} $ROOT_PASSWORD"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Save this password! This file will be deleted in 24 hours.${NC}"
else
    echo -e "${YELLOW}⚠️  Password file not found. Check /etc/gitlab/initial_root_password manually${NC}"
fi

echo ""
echo -e "${GREEN}📋 Next Steps:${NC}"
echo "1. ✅ GitLab is installed and running"
echo "2. 🌐 Open http://$LOCAL_IP in your browser"
echo "3. 🔐 Login with username 'root' and the password above"
echo "4. 📦 Import your repository from GitHub"
echo "5. 🔧 Configure CI/CD variables"
echo ""
echo -e "${GREEN}Useful Commands:${NC}"
echo "  sudo gitlab-ctl status          # Check GitLab status"
echo "  sudo gitlab-ctl restart         # Restart all services"
echo "  sudo gitlab-ctl tail            # View logs"
echo "  sudo gitlab-rake gitlab:check   # Run health check"
echo "  sudo gitlab-backup create       # Create backup"
echo ""
echo -e "${GREEN}Configuration file:${NC} /etc/gitlab/gitlab.rb"
echo -e "${GREEN}Backup location:${NC} /etc/gitlab/gitlab.rb.backup"
echo ""
echo -e "${YELLOW}⚠️  Note: This is a local development installation.${NC}"
echo -e "${YELLOW}   For production, use a dedicated server with SSL.${NC}"
echo ""
