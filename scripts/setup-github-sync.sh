#!/bin/bash

# GitLab → GitHub Синхронизация Setup Script
# Автоматизирует настройку синхронизации между GitLab и GitHub

set -e

echo "🚀 GitLab → GitHub Синхронизация Setup"
echo "========================================"
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка наличия необходимых файлов
check_requirements() {
    log_info "Проверка требований..."
    
    if [ ! -f ".gitlab-ci.yml" ]; then
        log_error ".gitlab-ci.yml не найден!"
        exit 1
    fi
    
    if [ ! -f ".migration-secrets" ]; then
        log_error ".migration-secrets не найден!"
        exit 1
    fi
    
    log_success "Все файлы найдены"
}

# Загрузка секретов
load_secrets() {
    log_info "Загрузка секретов..."
    source .migration-secrets
    
    if [ -z "$GITHUB_USERNAME" ]; then
        log_error "GITHUB_USERNAME не установлен в .migration-secrets"
        exit 1
    fi
    
    log_success "Секреты загружены"
}

# Создание GitHub репозитория
create_github_repo() {
    log_info "Создание GitHub репозитория..."
    
    echo "📋 Инструкция для создания GitHub репозитория:"
    echo "=============================================="
    echo ""
    echo "1. Зайдите на https://github.com"
    echo "2. Нажмите 'New repository'"
    echo "3. Название: ssl-monitor-pro"
    echo "4. Описание: SSL Monitor Pro - Production Ready"
    echo "5. Публичный репозиторий ✅"
    echo "6. НЕ инициализировать (будет заполнен из GitLab)"
    echo "7. Нажмите 'Create repository'"
    echo ""
    
    read -p "Нажмите Enter когда создадите репозиторий..."
    
    log_success "GitHub репозиторий должен быть создан"
}

# Создание GitHub Personal Access Token
create_github_token() {
    log_info "Создание GitHub Personal Access Token..."
    
    echo "📋 Инструкция для создания GitHub токена:"
    echo "=========================================="
    echo ""
    echo "1. GitHub → Settings → Developer settings → Personal access tokens"
    echo "2. Нажмите 'Generate new token (classic)'"
    echo "3. Note: GitLab CI/CD Sync"
    echo "4. Expiration: 90 days (или больше)"
    echo "5. Scopes:"
    echo "   ✅ repo (Full control of private repositories)"
    echo "   ✅ workflow (Update GitHub Action workflows)"
    echo "6. Нажмите 'Generate token'"
    echo "7. СКОПИРУЙТЕ ТОКЕН (он больше не будет показан!)"
    echo ""
    
    read -p "Введите GitHub Personal Access Token: " GITHUB_TOKEN
    
    if [ -z "$GITHUB_TOKEN" ]; then
        log_error "Токен не может быть пустым!"
        exit 1
    fi
    
    # Добавляем токен в .migration-secrets
    echo "" >> .migration-secrets
    echo "# GitHub Sync Token" >> .migration-secrets
    echo "GITHUB_TOKEN=$GITHUB_TOKEN" >> .migration-secrets
    
    log_success "GitHub токен сохранен в .migration-secrets"
}

# Обновление .gitlab-ci.yml
update_gitlab_ci() {
    log_info "Обновление .gitlab-ci.yml..."
    
    # Создаем backup
    cp .gitlab-ci.yml .gitlab-ci.yml.backup
    
    # Добавляем job для синхронизации
    cat >> .gitlab-ci.yml << 'EOF'

# Sync to GitHub for Render deployment
sync_to_github:
  stage: deploy
  image: alpine/git:latest
  before_script:
    - apk add --no-cache curl
  script:
    - git config --global user.email "gitlab@trustforge.uk"
    - git config --global user.name "GitLab CI"
    - git remote add github https://oauth2:${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/ssl-monitor-pro.git || true
    - git fetch github main || true
    - git push github HEAD:main --force
  only:
    - main
  when: on_success
  allow_failure: false
EOF
    
    log_success ".gitlab-ci.yml обновлен"
}

# Добавление переменной в GitLab CI/CD
add_gitlab_variable() {
    log_info "Добавление GITHUB_TOKEN в GitLab CI/CD Variables..."
    
    echo "📋 Инструкция для добавления переменной в GitLab:"
    echo "================================================="
    echo ""
    echo "1. Зайдите в GitLab: https://gitlab.trustforge.uk/root/ssl-monitor-pro"
    echo "2. Settings → CI/CD → Variables"
    echo "3. Нажмите 'Add variable'"
    echo "4. Key: GITHUB_TOKEN"
    echo "5. Value: $GITHUB_TOKEN"
    echo "6. Flags:"
    echo "   ✅ Protected"
    echo "   ✅ Masked"
    echo "7. Нажмите 'Add variable'"
    echo ""
    
    read -p "Нажмите Enter когда добавите переменную в GitLab..."
    
    log_success "Переменная должна быть добавлена в GitLab"
}

# Обновление Render
update_render() {
    log_info "Обновление Render repository URL..."
    
    echo "📋 Инструкция для обновления Render:"
    echo "===================================="
    echo ""
    echo "1. Зайдите в Render Dashboard"
    echo "2. Ваш сервис → Settings → Repository"
    echo "3. Repository URL: https://github.com/${GITHUB_USERNAME}/ssl-monitor-pro.git"
    echo "4. Branch: main"
    echo "5. Нажмите 'Save Changes'"
    echo "6. Нажмите 'Manual Deploy'"
    echo ""
    
    read -p "Нажмите Enter когда обновите Render..."
    
    log_success "Render должен быть обновлен"
}

# Тестирование синхронизации
test_sync() {
    log_info "Тестирование синхронизации..."
    
    echo "📋 Инструкция для тестирования:"
    echo "==============================="
    echo ""
    echo "1. Сделайте тестовый коммит:"
    echo "   git add ."
    echo "   git commit -m 'test: GitHub sync setup'"
    echo "   git push origin main"
    echo ""
    echo "2. Проверьте GitLab CI/CD:"
    echo "   https://gitlab.trustforge.uk/root/ssl-monitor-pro/-/pipelines"
    echo ""
    echo "3. Проверьте GitHub репозиторий:"
    echo "   https://github.com/${GITHUB_USERNAME}/ssl-monitor-pro"
    echo ""
    echo "4. Проверьте Render deployment:"
    echo "   Render Dashboard → Deployments"
    echo ""
    
    log_success "Готово к тестированию!"
}

# Основная функция
main() {
    echo "🎯 Настройка GitLab → GitHub синхронизации"
    echo "=========================================="
    echo ""
    
    check_requirements
    load_secrets
    create_github_repo
    create_github_token
    update_gitlab_ci
    add_gitlab_variable
    update_render
    test_sync
    
    echo ""
    echo "🎉 Настройка завершена!"
    echo "======================="
    echo ""
    echo "📋 Что было сделано:"
    echo "===================="
    echo "✅ GitHub репозиторий создан"
    echo "✅ GitHub токен получен и сохранен"
    echo "✅ .gitlab-ci.yml обновлен"
    echo "✅ GitLab переменная добавлена"
    echo "✅ Render обновлен на GitHub URL"
    echo ""
    echo "🚀 Следующие шаги:"
    echo "==================="
    echo "1. Сделать тестовый коммит"
    echo "2. Проверить GitLab CI/CD pipeline"
    echo "3. Проверить GitHub репозиторий"
    echo "4. Проверить Render deployment"
    echo ""
    echo "📖 Документация: GITLAB_GITHUB_SYNC_SOLUTION.md"
}

# Запуск скрипта
main "$@"
