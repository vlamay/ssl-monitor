#!/bin/bash
echo "🔍 TRIAL PERIOD AUDIT"
echo "===================="
echo ""

echo "📁 Searching for '14-day' or '14 day' mentions..."
echo "---"
grep -r "14.day\|14 day\|fourteen day\|14-day" . \
  --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" \
  --include="*.py" --include="*.html" --include="*.md" \
  --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build \
  --exclude-dir=venv --exclude-dir=.git \
  -n | grep -v ".cursorrules" | grep -v "audit_trial_period"

echo ""
echo "📁 Searching for '7-day' or '7 day' mentions..."
echo "---"
grep -r "7.day\|7 day\|seven day\|7-day" . \
  --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" \
  --include="*.py" --include="*.html" --include="*.md" \
  --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build \
  --exclude-dir=venv --exclude-dir=.git \
  -n | grep -v ".cursorrules" | grep -v "audit_trial_period"

echo ""
echo "📁 Searching for TRIAL_DAYS or trial_period_days..."
echo "---"
grep -r "TRIAL_DAYS\|trial_period_days\|trialDays\|trial_days" . \
  --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" \
  --include="*.py" --include="*.env*" \
  --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build \
  --exclude-dir=venv --exclude-dir=.git \
  -n | grep -v "audit_trial_period"

echo ""
echo "✅ Audit complete!"

