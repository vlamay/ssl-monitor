#!/bin/bash
# Git Commands для push на GitHub

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🔑 GIT COMMANDS - Copy & Execute                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to project
cd /home/vmaidaniuk/ssl-monitor

# Check current status
echo "1. Checking current git status..."
git status
echo ""

# Check existing remotes
echo "2. Checking existing remotes..."
git remote -v
echo ""

# Remove origin if exists
if git remote | grep -q "origin"; then
    echo "3. Removing existing origin..."
    git remote remove origin
    echo "   ✓ Origin removed"
else
    echo "3. No existing origin found"
fi
echo ""

# Add new remote
echo "4. Adding GitHub remote..."
git remote add origin git@github.com:maydanov-dev/ssl-monitor.git
echo "   ✓ Remote added"
echo ""

# Rename branch to main
echo "5. Ensuring branch is named 'main'..."
git branch -M main
echo "   ✓ Branch renamed to main"
echo ""

# Push to GitHub
echo "6. Pushing to GitHub..."
git push -u origin main
echo ""

# Verify
echo "7. Verifying remote..."
git remote -v
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ SUCCESS! Code pushed to GitHub                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🔗 Your repository: https://github.com/maydanov-dev/ssl-monitor"
echo ""
echo "Next steps:"
echo "1. Open the repository URL above"
echo "2. Verify all files are there (~38 files)"
echo "3. Proceed to Render.com deployment"
echo ""

