#!/bin/bash

# SSL Monitor Pro - Migration Readiness Check
# Usage: ./scripts/migration-readiness-check.sh

echo "🔍 SSL Monitor Pro - Migration Readiness Check"
echo "=============================================="
echo ""

READY=0
WARNINGS=0
CRITICAL=0

# Function to check status
check_status() {
  local check_name="$1"
  local check_command="$2"
  local expected_result="$3"
  local is_critical=${4:-false}
  
  echo -n "Checking: $check_name ... "
  
  if eval "$check_command" >/dev/null 2>&1; then
    if [ ! -z "$expected_result" ]; then
      result=$(eval "$check_command" 2>/dev/null)
      if [[ "$result" == *"$expected_result"* ]]; then
        echo "✅ PASS"
      else
        echo "⚠️  WARN (unexpected result)"
        ((WARNINGS++))
      fi
    else
      echo "✅ PASS"
    fi
  else
    if [ "$is_critical" = true ]; then
      echo "❌ CRITICAL FAIL"
      ((CRITICAL++))
      ((READY++))
    else
      echo "⚠️  WARN"
      ((WARNINGS++))
    fi
  fi
}

# Function to check file exists
check_file() {
  local file_path="$1"
  local description="$2"
  local is_critical=${3:-false}
  
  echo -n "Checking: $description ... "
  
  if [ -f "$file_path" ]; then
    echo "✅ PASS"
  else
    if [ "$is_critical" = true ]; then
      echo "❌ CRITICAL FAIL"
      ((CRITICAL++))
      ((READY++))
    else
      echo "⚠️  WARN"
      ((WARNINGS++))
    fi
  fi
}

# Function to check directory exists
check_directory() {
  local dir_path="$1"
  local description="$2"
  local is_critical=${3:-false}
  
  echo -n "Checking: $description ... "
  
  if [ -d "$dir_path" ]; then
    echo "✅ PASS"
  else
    if [ "$is_critical" = true ]; then
      echo "❌ CRITICAL FAIL"
      ((CRITICAL++))
      ((READY++))
    else
      echo "⚠️  WARN"
      ((WARNINGS++))
    fi
  fi
}

echo "📋 PRE-MIGRATION CHECKS"
echo "======================="

# 1. Git Configuration
echo ""
echo "🔧 Git Configuration:"
check_status "Git repository" "git status" "" true
check_status "GitLab remote" "git remote get-url gitlab" "192.168.1.10" true
check_status "Main branch" "git branch --show-current" "main" false

# 2. Essential Files
echo ""
echo "📁 Essential Files:"
check_file ".gitlab-ci.yml" "GitLab CI/CD configuration" true
check_file "backend/requirements.txt" "Backend dependencies" true
check_file "frontend-modern/package.json" "Frontend dependencies" true
check_file "docker-compose.yml" "Docker configuration" true
check_file "README.md" "Project documentation" false

# 3. Scripts and Tools
echo ""
echo "🛠️  Migration Scripts:"
check_file "scripts/setup-gitlab-vars.sh" "GitLab variables setup script" true
check_file "scripts/smoke-tests.sh" "Smoke tests script" true
check_file "scripts/rollback-to-github.sh" "Rollback script" true
check_file "scripts/migration-readiness-check.sh" "This readiness check script" false

# 4. Credentials and Secrets
echo ""
echo "🔐 Credentials and Secrets:"
check_file ".migration-secrets" "Migration secrets file" true
check_file "env.example" "Environment variables template" false

# 5. Backup and Documentation
echo ""
echo "💾 Backup and Documentation:"
check_directory "backup" "Backup directory" false
check_file "DEPLOYMENT_GUIDE.md" "Deployment guide" false
check_file "WEEK_3_PROGRESS_REPORT.md" "Week 3 progress report" false

# 6. Network and Connectivity
echo ""
echo "🌐 Network and Connectivity:"
check_status "GitLab connectivity" "curl -s --connect-timeout 5 http://192.168.1.10" "" true
check_status "Production API" "curl -s --connect-timeout 10 https://ssl-monitor-api.onrender.com/health" "healthy" false
check_status "Production Frontend" "curl -s --connect-timeout 10 -o /dev/null -w '%{http_code}' https://cloudsre.xyz" "200" false

# 7. Environment Variables Check
echo ""
echo "⚙️  Environment Variables:"
if [ -f ".migration-secrets" ]; then
  echo "Checking: Required environment variables ... "
  
  # Source the secrets file
  source .migration-secrets 2>/dev/null
  
  # Check critical variables
  critical_vars=(
    "RENDER_API_KEY"
    "RENDER_DEPLOY_HOOK_URL"
    "CLOUDFLARE_API_TOKEN"
    "STRIPE_SECRET_KEY"
    "DATABASE_URL"
    "TELEGRAM_BOT_TOKEN"
    "SLACK_WEBHOOK_URL"
  )
  
  missing_vars=0
  for var in "${critical_vars[@]}"; do
    if [ -z "${!var}" ]; then
      echo "   ❌ Missing: $var"
      ((missing_vars++))
    fi
  done
  
  if [ $missing_vars -eq 0 ]; then
    echo "   ✅ PASS (all critical variables present)"
  else
    echo "   ❌ CRITICAL FAIL ($missing_vars variables missing)"
    ((CRITICAL++))
    ((READY++))
  fi
else
  echo "Checking: Environment variables ... ❌ CRITICAL FAIL (secrets file missing)"
  ((CRITICAL++))
  ((READY++))
fi

# 8. GitLab CI/CD Configuration
echo ""
echo "🔧 GitLab CI/CD Configuration:"
if [ -f ".gitlab-ci.yml" ]; then
  echo "Checking: GitLab CI/CD syntax ... "
  if command -v yq >/dev/null 2>&1; then
    if yq eval '.' .gitlab-ci.yml >/dev/null 2>&1; then
      echo "   ✅ PASS (valid YAML syntax)"
    else
      echo "   ❌ CRITICAL FAIL (invalid YAML syntax)"
      ((CRITICAL++))
      ((READY++))
    fi
  else
    echo "   ⚠️  WARN (yq not installed - cannot validate YAML)"
    ((WARNINGS++))
  fi
  
  # Check for required stages
  if grep -q "stages:" .gitlab-ci.yml && grep -q "test\|build\|deploy" .gitlab-ci.yml; then
    echo "   ✅ PASS (required stages present)"
  else
    echo "   ❌ CRITICAL FAIL (missing required stages)"
    ((CRITICAL++))
    ((READY++))
  fi
else
  echo "Checking: GitLab CI/CD configuration ... ❌ CRITICAL FAIL (file missing)"
  ((CRITICAL++))
  ((READY++))
fi

# 9. Production System Health
echo ""
echo "🏥 Production System Health:"
echo "Checking: Backend health ... "
backend_health=$(curl -s --connect-timeout 10 https://ssl-monitor-api.onrender.com/health 2>/dev/null)
if echo "$backend_health" | grep -q "healthy"; then
  echo "   ✅ PASS (backend healthy)"
else
  echo "   ⚠️  WARN (backend health check failed)"
  ((WARNINGS++))
fi

echo "Checking: Frontend accessibility ... "
frontend_status=$(curl -s --connect-timeout 10 -o /dev/null -w '%{http_code}' https://cloudsre.xyz 2>/dev/null)
if [ "$frontend_status" = "200" ]; then
  echo "   ✅ PASS (frontend accessible)"
else
  echo "   ⚠️  WARN (frontend returned HTTP $frontend_status)"
  ((WARNINGS++))
fi

# 10. Disk Space and Resources
echo ""
echo "💽 System Resources:"
echo "Checking: Available disk space ... "
available_space=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "${available_space%.*}" -gt 5 ]; then
  echo "   ✅ PASS (${available_space}G available)"
else
  echo "   ⚠️  WARN (only ${available_space}G available)"
  ((WARNINGS++))
fi

echo "Checking: Available memory ... "
available_memory=$(free -h | awk 'NR==2 {print $7}' | sed 's/Gi//')
if [ "${available_memory%.*}" -gt 2 ]; then
  echo "   ✅ PASS (${available_memory}Gi available)"
else
  echo "   ⚠️  WARN (only ${available_memory}Gi available)"
  ((WARNINGS++))
fi

# Summary
echo ""
echo "=============================================="
echo "📊 MIGRATION READINESS SUMMARY"
echo "=============================================="
echo "✅ Critical Issues: $CRITICAL"
echo "⚠️  Warnings: $WARNINGS"
echo ""

if [ $CRITICAL -eq 0 ]; then
  if [ $WARNINGS -eq 0 ]; then
    echo "🎉 READY FOR MIGRATION!"
    echo "✅ All checks passed - you can proceed with migration"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Run: ./scripts/setup-gitlab-vars.sh"
    echo "   2. Test GitLab pipeline"
    echo "   3. Begin Phase 1 of migration guide"
    exit 0
  else
    echo "✅ READY FOR MIGRATION (with warnings)"
    echo "⚠️  Some warnings found, but migration can proceed"
    echo ""
    echo "🔧 Recommended actions:"
    echo "   1. Review warnings above"
    echo "   2. Fix non-critical issues if possible"
    echo "   3. Proceed with migration"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Run: ./scripts/setup-gitlab-vars.sh"
    echo "   2. Test GitLab pipeline"
    echo "   3. Begin Phase 1 of migration guide"
    exit 0
  fi
else
  echo "❌ NOT READY FOR MIGRATION"
  echo "🚨 Critical issues found - must be fixed before migration"
  echo ""
  echo "🔧 Required Actions:"
  echo "   1. Fix all critical issues above"
  echo "   2. Re-run this check: ./scripts/migration-readiness-check.sh"
  echo "   3. Only proceed when all critical issues are resolved"
  echo ""
  echo "📋 Critical Issues to Fix:"
  echo "   • Check the ❌ CRITICAL FAIL items above"
  echo "   • Ensure all required files are present"
  echo "   • Verify network connectivity"
  echo "   • Complete environment setup"
  exit 1
fi
