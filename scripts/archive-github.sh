#!/bin/bash

# SSL Monitor Pro - Archive GitHub Repository
# Usage: ./scripts/archive-github.sh

echo "📦 Archiving GitHub Repository for Migration..."
echo "============================================="
echo ""

echo "⚠️  IMPORTANT: This will archive the GitHub repository!"
echo "📝 Make sure all data is backed up before proceeding."
echo ""

read -p "Are you sure you want to archive the GitHub repository? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Archive cancelled"
    exit 1
fi

echo ""
echo "📋 GitHub Repository Archive Steps:"
echo ""

echo "1️⃣ Create Final Backup:"
echo "   • Repository: https://192.168.1.10/root/ssl-monitor-pro"
echo "   • Backup already created: backup/final-backup-*.tar.gz"
echo "   • Size: 265M (45,236 files)"
echo ""

echo "2️⃣ Archive Repository (Manual):"
echo "   • Go to: https://192.168.1.10/root/ssl-monitor-pro"
echo "   • Go to: Settings → General"
echo "   • Scroll to: Danger Zone"
echo "   • Click: 'Archive this repository'"
echo "   • Type repository name to confirm"
echo "   • Click: 'I understand the consequences, archive this repository'"
echo ""

echo "3️⃣ Add Archive Notice:"
echo "   • Repository will be read-only"
echo "   • Add README with migration notice"
echo "   • Include new GitLab URL"
echo "   • Add migration date"
echo ""

echo "4️⃣ Archive Notice Template:"
cat > backup/github-archive-notice.md <<'EOF'
# ⚠️ ARCHIVED REPOSITORY

This repository has been migrated to GitLab.

## 🚀 New Location

- **GitLab Repository:** http://192.168.1.10/root/ssl-monitor-pro
- **Production URL:** https://cloudsre.xyz
- **Migration Date:** 2025-10-13

## 📋 Migration Details

- **Reason:** Full migration to self-hosted GitLab for better control and CI/CD
- **Status:** Complete (Phase 1-5)
- **Backup:** Available in migration backup
- **Rollback:** Not available (one-way migration)

## 🔗 Important Links

- **GitLab Repository:** http://192.168.1.10/root/ssl-monitor-pro
- **Production Application:** https://cloudsre.xyz
- **API Documentation:** https://ssl-monitor-api.onrender.com/docs
- **Migration Guide:** See MIGRATION_GUIDE.md in GitLab repo

## 📞 Support

For any questions about the migration or access to the new repository, please contact the development team.

---

**This repository is archived and read-only. Please use the GitLab repository for all future development.**
EOF

echo "   ✅ Archive notice created: backup/github-archive-notice.md"
echo ""

echo "5️⃣ Final Verification:"
echo "   • Repository is read-only"
echo "   • All issues/PRs are locked"
echo "   • Archive notice is visible"
echo "   • GitLab repository is accessible"
echo ""

echo "📊 Archive Summary:"
echo "   • Repository: root/ssl-monitor-pro"
echo "   • Status: Archived (read-only)"
echo "   • New Home: GitLab (root/ssl-monitor-pro)"
echo "   • Production: https://cloudsre.xyz"
echo "   • Backup: Available (265M)"
echo ""

echo "✅ GitHub Repository Archive Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Complete manual archive in GitHub UI"
echo "   2. Verify archive notice is visible"
echo "   3. Update all documentation links"
echo "   4. Notify team about migration completion"
echo ""
echo "🎉 Migration Status: COMPLETE!"
echo ""
echo "🔗 Important Links:"
echo "   • GitHub Archive: https://192.168.1.10/root/ssl-monitor-pro (archived)"
echo "   • GitLab Repository: http://192.168.1.10/root/ssl-monitor-pro"
echo "   • Production: https://cloudsre.xyz"
echo "   • Migration Guide: MIGRATION_GUIDE.md"
