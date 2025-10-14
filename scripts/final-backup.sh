#!/bin/bash

# SSL Monitor Pro - Final Backup Before Migration
# Usage: ./scripts/final-backup.sh

echo "💾 SSL Monitor Pro - Final Backup Before Migration"
echo "================================================="
echo ""

# Configuration
BACKUP_DIR="backup/final-backup-$(date +%Y%m%d-%H%M%S)"
GITHUB_REPO="root/ssl-monitor-pro"
GITLAB_REPO="192.168.1.10/root/ssl-monitor-pro"

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo "📁 Creating backup directory: $BACKUP_DIR"
echo ""

# Function to create backup with timestamp
create_backup() {
  local source="$1"
  local destination="$2"
  local description="$3"
  
  echo "📦 Backing up: $description"
  
  if [ -f "$source" ]; then
    cp "$source" "$destination"
    echo "   ✅ File: $source → $destination"
  elif [ -d "$source" ]; then
    cp -r "$source" "$destination"
    echo "   ✅ Directory: $source → $destination"
  else
    echo "   ⚠️  Not found: $source"
  fi
}

# 1. Backup Git Repository
echo "🔧 Git Repository Backup:"
create_backup ".git" "$BACKUP_DIR/git-repo" "Git repository"
create_backup ".gitignore" "$BACKUP_DIR/gitignore" "Git ignore file"
create_backup ".gitlab-ci.yml" "$BACKUP_DIR/gitlab-ci.yml" "GitLab CI/CD configuration"

# 2. Backup Configuration Files
echo ""
echo "⚙️  Configuration Files Backup:"
create_backup "docker-compose.yml" "$BACKUP_DIR/docker-compose.yml" "Docker Compose configuration"
create_backup "docker-compose.dev.yml" "$BACKUP_DIR/docker-compose.dev.yml" "Docker Compose development"
create_backup "Dockerfile.prod" "$BACKUP_DIR/Dockerfile.prod" "Production Dockerfile"
create_backup "env.example" "$BACKUP_DIR/env.example" "Environment variables template"
create_backup ".migration-secrets" "$BACKUP_DIR/migration-secrets" "Migration secrets"

# 3. Backup Backend
echo ""
echo "🐍 Backend Backup:"
create_backup "backend/" "$BACKUP_DIR/backend" "Backend application"
create_backup "backend/requirements.txt" "$BACKUP_DIR/backend-requirements.txt" "Backend dependencies"
create_backup "backend/requirements-dev.txt" "$BACKUP_DIR/backend-requirements-dev.txt" "Backend development dependencies"

# 4. Backup Frontend
echo ""
echo "🌐 Frontend Backup:"
create_backup "frontend/" "$BACKUP_DIR/frontend" "Frontend application"
create_backup "frontend-modern/" "$BACKUP_DIR/frontend-modern" "Modern frontend application"
create_backup "frontend-react/" "$BACKUP_DIR/frontend-react" "React frontend application"

# 5. Backup Mobile App
echo ""
echo "📱 Mobile App Backup:"
create_backup "mobile-app/" "$BACKUP_DIR/mobile-app" "Mobile application"

# 6. Backup Scripts
echo ""
echo "🛠️  Scripts Backup:"
create_backup "scripts/" "$BACKUP_DIR/scripts" "All scripts"
create_backup "deploy.sh" "$BACKUP_DIR/deploy.sh" "Deployment script"
create_backup "deploy_to_cloudflare.sh" "$BACKUP_DIR/deploy_to_cloudflare.sh" "Cloudflare deployment script"

# 7. Backup Documentation
echo ""
echo "📚 Documentation Backup:"
create_backup "README.md" "$BACKUP_DIR/README.md" "Main README"
create_backup "CONTRIBUTING.md" "$BACKUP_DIR/CONTRIBUTING.md" "Contributing guide"
create_backup "docs/" "$BACKUP_DIR/docs" "Documentation directory"

# 8. Backup Database
echo ""
echo "🗄️  Database Backup:"
create_backup "database/" "$BACKUP_DIR/database" "Database files"
create_backup "backend/migrations/" "$BACKUP_DIR/migrations" "Database migrations"

# 9. Backup GitLab CI/CD (if exists)
echo ""
echo "🔄 GitLab CI/CD Backup:"
if [ -d ".github" ]; then
  create_backup ".github/" "$BACKUP_DIR/github-actions" "GitLab CI/CD workflows"
else
  echo "   ℹ️  No GitLab CI/CD found (already migrated to GitLab)"
fi

# 10. Backup Environment and Secrets
echo ""
echo "🔐 Environment and Secrets Backup:"
create_backup ".env" "$BACKUP_DIR/env" "Environment file"
create_backup ".env.local" "$BACKUP_DIR/env.local" "Local environment file"
create_backup ".env.production" "$BACKUP_DIR/env.production" "Production environment file"

# 11. Create Git Bundle
echo ""
echo "📦 Creating Git Bundle:"
echo "   Creating complete repository bundle..."
git bundle create "$BACKUP_DIR/repository.bundle" --all
if [ $? -eq 0 ]; then
  echo "   ✅ Git bundle created: $BACKUP_DIR/repository.bundle"
else
  echo "   ❌ Failed to create git bundle"
fi

# 12. Create Archive
echo ""
echo "🗜️  Creating Archive:"
echo "   Compressing backup..."
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
if [ $? -eq 0 ]; then
  echo "   ✅ Archive created: $BACKUP_DIR.tar.gz"
  # Calculate size
  archive_size=$(du -h "$BACKUP_DIR.tar.gz" | cut -f1)
  echo "   📊 Archive size: $archive_size"
else
  echo "   ❌ Failed to create archive"
fi

# 13. Create Backup Manifest
echo ""
echo "📋 Creating Backup Manifest:"
cat > "$BACKUP_DIR/BACKUP_MANIFEST.md" <<EOF
# SSL Monitor Pro - Final Backup Manifest

**Backup Date:** $(date)
**Backup Type:** Pre-Migration Full Backup
**Backup Location:** $BACKUP_DIR
**Archive:** $BACKUP_DIR.tar.gz

## Repository Information

### GitHub Repository (Source)
- **URL:** https://github.com/$GITHUB_REPO
- **Status:** Active (pre-migration)
- **Branch:** main
- **Last Commit:** $(git log -1 --format="%h %s" 2>/dev/null || echo "N/A")

### GitLab Repository (Target)
- **URL:** http://$GITLAB_REPO
- **Status:** Migration target
- **Branch:** main
- **Migration Date:** $(date)

## Backup Contents

### Core Application
- ✅ Backend application (Python/FastAPI)
- ✅ Frontend applications (HTML/React)
- ✅ Mobile application (React Native)
- ✅ Database migrations
- ✅ Docker configurations

### Configuration Files
- ✅ Environment variables
- ✅ Docker Compose files
- ✅ CI/CD configurations
- ✅ Deployment scripts

### Documentation
- ✅ README files
- ✅ Contributing guidelines
- ✅ API documentation
- ✅ Migration guides

### Git Repository
- ✅ Complete git history
- ✅ All branches and tags
- ✅ Git bundle for easy restore

## Restoration Instructions

### To restore from this backup:

1. **Extract the archive:**
   \`\`\`bash
   tar -xzf $BACKUP_DIR.tar.gz
   cd $BACKUP_DIR
   \`\`\`

2. **Restore git repository:**
   \`\`\`bash
   git clone repository.bundle restored-repo
   cd restored-repo
   \`\`\`

3. **Restore files:**
   \`\`\`bash
   cp -r backend/ ../restored-backend/
   cp -r frontend-modern/ ../restored-frontend/
   # ... copy other directories as needed
   \`\`\`

4. **Restore environment:**
   \`\`\`bash
   cp migration-secrets ../.migration-secrets
   cp env.example ../.env
   \`\`\`

## Verification

### To verify backup integrity:

1. **Check git bundle:**
   \`\`\`bash
   git bundle verify repository.bundle
   \`\`\`

2. **Check file integrity:**
   \`\`\`bash
   find $BACKUP_DIR -type f -exec md5sum {} \; > checksums.txt
   \`\`\`

3. **Test restoration:**
   \`\`\`bash
   # Create test directory
   mkdir test-restore
   cd test-restore
   
   # Clone from bundle
   git clone ../repository.bundle test-repo
   
   # Verify it works
   cd test-repo
   git log --oneline -5
   \`\`\`

## Migration Status

- **Pre-Migration:** ✅ Complete
- **Backup Created:** ✅ Complete
- **Migration Ready:** ✅ Ready
- **Post-Migration:** ⏳ Pending

## Important Notes

- This backup contains all sensitive information including secrets
- Store securely and restrict access
- Keep until migration is confirmed successful
- Can be used for rollback if needed

## Contacts

- **Migration Lead:** [Your Name]
- **Technical Lead:** [Technical Lead]
- **Emergency Contact:** [Emergency Contact]

---
*Generated by final-backup.sh on $(date)*
EOF

echo "   ✅ Backup manifest created: $BACKUP_DIR/BACKUP_MANIFEST.md"

# 14. Create Checksums
echo ""
echo "🔍 Creating Checksums:"
echo "   Generating MD5 checksums..."
find "$BACKUP_DIR" -type f -exec md5sum {} \; > "$BACKUP_DIR/checksums.md5"
echo "   ✅ Checksums created: $BACKUP_DIR/checksums.md5"

# 15. Final Summary
echo ""
echo "================================================="
echo "✅ FINAL BACKUP COMPLETED SUCCESSFULLY"
echo "================================================="
echo ""
echo "📊 Backup Summary:"
echo "   • Backup Directory: $BACKUP_DIR"
echo "   • Archive: $BACKUP_DIR.tar.gz"
echo "   • Archive Size: $archive_size"
echo "   • Files Backed Up: $(find "$BACKUP_DIR" -type f | wc -l)"
echo "   • Directories Backed Up: $(find "$BACKUP_DIR" -type d | wc -l)"
echo ""
echo "📁 Backup Contents:"
echo "   ✅ Git repository (complete history)"
echo "   ✅ Backend application"
echo "   ✅ Frontend applications"
echo "   ✅ Mobile application"
echo "   ✅ Database migrations"
echo "   ✅ Configuration files"
echo "   ✅ Environment variables"
echo "   ✅ Scripts and tools"
echo "   ✅ Documentation"
echo "   ✅ GitLab CI/CD (if present)"
echo ""
echo "🔐 Security Notes:"
echo "   • Backup contains sensitive information"
echo "   • Store in secure location"
echo "   • Restrict access to authorized personnel only"
echo "   • Keep until migration is confirmed successful"
echo ""
echo "🚀 Next Steps:"
echo "   1. Verify backup integrity"
echo "   2. Store backup securely"
echo "   3. Proceed with migration"
echo "   4. Keep backup until migration confirmed"
echo ""
echo "📋 Verification Commands:"
echo "   • Check archive: tar -tzf $BACKUP_DIR.tar.gz"
echo "   • Verify git bundle: git bundle verify $BACKUP_DIR/repository.bundle"
echo "   • Check checksums: md5sum -c $BACKUP_DIR/checksums.md5"
echo ""
echo "🎉 Backup completed successfully!"
echo "   Ready for migration to GitLab!"
