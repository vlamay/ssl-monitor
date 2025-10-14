#!/bin/bash

# SSL Monitor Pro - Update GitHub Links to GitLab
# Usage: ./scripts/update-links.sh

echo "🔗 Updating all GitHub links to GitLab..."
echo "========================================="
echo ""

# Backup original files
echo "📁 Creating backup of modified files..."
mkdir -p backup/link-updates
timestamp=$(date +%Y%m%d-%H%M%S)

# Function to update links in a file
update_file_links() {
  local file_path="$1"
  local backup_path="backup/link-updates/$(basename "$file_path")-$timestamp"
  
  echo "Processing: $file_path"
  
  # Create backup
  cp "$file_path" "$backup_path"
  
  # Update GitHub links to GitLab
  sed -i 's|github\.com/root/ssl-monitor-pro|192.168.1.10/root/ssl-monitor-pro|g' "$file_path"
  sed -i 's|github\.com/root/ssl-monitor-pro-pro|192.168.1.10/root/ssl-monitor-pro|g' "$file_path"
  sed -i 's|https://192.168.1.10/root/ssl-monitor-pro|http://192.168.1.10/root/ssl-monitor-pro|g' "$file_path"
  sed -i 's|http://192.168.1.10/root/ssl-monitor-pro.git|http://192.168.1.10/root/ssl-monitor-pro.git|g' "$file_path"
  
  # Update GitLab CI/CD references
  sed -i 's|GitLab CI/CD|GitLab CI/CD|g' "$file_path"
  sed -i 's|GitHub\.com|GitLab|g' "$file_path"
  
  # Update repository references
  sed -i 's|root/ssl-monitor-pro|root/ssl-monitor-pro|g' "$file_path"
  
  echo "   ✅ Updated and backed up"
}

# Find all files that might contain GitHub links
echo "🔍 Finding files with GitHub references..."

# Find files containing GitHub references
files_with_github=$(find . -type f \( -name "*.md" -o -name "*.html" -o -name "*.py" -o -name "*.js" -o -name "*.json" -o -name "*.yml" -o -name "*.yaml" -o -name "*.txt" -o -name "*.sh" \) \
  -not -path "./node_modules/*" \
  -not -path "./venv/*" \
  -not -path "./.git/*" \
  -not -path "./backup/*" \
  -exec grep -l "192.168.1.10/root/ssl-monitor-pro\|root/ssl-monitor-pro\|GitLab CI/CD\|github\.com" {} \;)

if [ -z "$files_with_github" ]; then
  echo "✅ No files found with GitHub references"
  exit 0
fi

echo "Found $(echo "$files_with_github" | wc -l) files with GitHub references:"
echo "$files_with_github"
echo ""

# Process each file
for file in $files_with_github; do
  update_file_links "$file"
done

echo ""
echo "📊 Summary of changes:"

# Show what was changed
echo ""
echo "🔄 Link Updates Applied:"
echo "   • 192.168.1.10/root/ssl-monitor-pro → 192.168.1.10/root/ssl-monitor-pro"
echo "   • root/ssl-monitor-pro → root/ssl-monitor-pro"
echo "   • GitLab CI/CD → GitLab CI/CD"
echo "   • GitLab → GitLab"

echo ""
echo "📁 Backup Location:"
echo "   • backup/link-updates/"

echo ""
echo "🔍 Files Modified:"
for file in $files_with_github; do
  echo "   • $file"
done

# Create a summary report
echo ""
echo "📝 Creating update summary report..."
cat > "backup/link-updates/update-summary-$timestamp.md" <<EOF
# Link Update Summary

**Date:** $(date)
**Script:** scripts/update-links.sh
**Timestamp:** $timestamp

## Changes Applied

### GitHub → GitLab Link Updates:
- \`192.168.1.10/root/ssl-monitor-pro\` → \`192.168.1.10/root/ssl-monitor-pro\`
- \`root/ssl-monitor-pro\` → \`root/ssl-monitor-pro\`
- \`GitLab CI/CD\` → \`GitLab CI/CD\`
- \`GitLab\` → \`GitLab\`

### Files Modified:
$(for file in $files_with_github; do echo "- \`$file\`"; done)

### Backup Files:
$(for file in $files_with_github; do echo "- \`backup/link-updates/$(basename "$file")-$timestamp\`"; done)

## Verification

To verify changes were applied correctly:

\`\`\`bash
# Check for remaining GitHub references
grep -r "192.168.1.10/root/ssl-monitor-pro" . --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude-dir=backup

# Check for GitLab references
grep -r "192.168.1.10/root/ssl-monitor-pro" . --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude-dir=backup
\`\`\`

## Rollback

To rollback changes:

\`\`\`bash
# Restore from backup
for file in backup/link-updates/*-$timestamp; do
  original_file="\${file#backup/link-updates/}"
  original_file="\${original_file%-$timestamp}"
  cp "\$file" "\$original_file"
done
\`\`\`
EOF

echo "   ✅ Summary report created: backup/link-updates/update-summary-$timestamp.md"

# Verify changes
echo ""
echo "🔍 Verifying changes..."

# Check for remaining GitHub references
remaining_github=$(grep -r "192.168.1.10/root/ssl-monitor-pro" . --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude-dir=backup 2>/dev/null | wc -l)

if [ $remaining_github -eq 0 ]; then
  echo "   ✅ No remaining GitHub references found"
else
  echo "   ⚠️  $remaining_github GitHub references still found:"
  grep -r "192.168.1.10/root/ssl-monitor-pro" . --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude-dir=backup 2>/dev/null | head -5
  echo "   ... (showing first 5 results)"
fi

# Check for GitLab references
gitlab_references=$(grep -r "192.168.1.10/root/ssl-monitor-pro" . --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude-dir=backup 2>/dev/null | wc -l)

echo "   ✅ $gitlab_references GitLab references found"

# Show git status
echo ""
echo "📊 Git Status:"
git status --porcelain | head -10
if [ $(git status --porcelain | wc -l) -gt 10 ]; then
  echo "   ... and $(($(git status --porcelain | wc -l) - 10)) more files"
fi

echo ""
echo "========================================="
echo "✅ LINK UPDATE COMPLETE"
echo "========================================="
echo ""
echo "📋 Summary:"
echo "   • Files processed: $(echo "$files_with_github" | wc -l)"
echo "   • Backup created: backup/link-updates/"
echo "   • Summary report: backup/link-updates/update-summary-$timestamp.md"
echo "   • Remaining GitHub refs: $remaining_github"
echo "   • GitLab refs added: $gitlab_references"
echo ""
echo "🚀 Next Steps:"
echo "   1. Review changes: git diff"
echo "   2. Commit changes: git add . && git commit -m 'docs: update GitHub links to GitLab'"
echo "   3. Push to GitLab: git push gitlab main"
echo ""
echo "🔄 To rollback if needed:"
echo "   • See rollback instructions in backup/link-updates/update-summary-$timestamp.md"
