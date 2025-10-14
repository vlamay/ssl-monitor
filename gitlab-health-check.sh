#!/bin/bash
# GitLab Health Check Script
# Проверяет статус GitLab и отправляет уведомления

LOG_FILE="/var/log/gitlab-health-check.log"
GITLAB_URL="http://192.168.1.10"

# Функция логирования
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Проверка статуса GitLab сервисов
check_gitlab_status() {
    if systemctl is-active --quiet gitlab-runsvdir; then
        log_message "✅ GitLab service is running"
        return 0
    else
        log_message "❌ GitLab service is not running"
        return 1
    fi
}

# Проверка доступности веб-интерфейса
check_gitlab_web() {
    if curl -s -o /dev/null -w "%{http_code}" "$GITLAB_URL" | grep -q "200\|302"; then
        log_message "✅ GitLab web interface is accessible"
        return 0
    else
        log_message "❌ GitLab web interface is not accessible"
        return 1
    fi
}

# Проверка использования ресурсов
check_resources() {
    # Проверка памяти
    MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    if (( $(echo "$MEMORY_USAGE > 90" | bc -l) )); then
        log_message "⚠️  High memory usage: ${MEMORY_USAGE}%"
    else
        log_message "✅ Memory usage: ${MEMORY_USAGE}%"
    fi
    
    # Проверка диска
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 90 ]; then
        log_message "⚠️  High disk usage: ${DISK_USAGE}%"
    else
        log_message "✅ Disk usage: ${DISK_USAGE}%"
    fi
}

# Основная функция проверки
main() {
    log_message "=== GitLab Health Check Started ==="
    
    # Проверки
    check_gitlab_status
    check_gitlab_web
    check_resources
    
    # Итоговый статус
    if check_gitlab_status && check_gitlab_web; then
        log_message "✅ GitLab is healthy and accessible"
        exit 0
    else
        log_message "❌ GitLab has issues - restarting..."
        sudo systemctl restart gitlab-runsvdir
        sleep 60
        if check_gitlab_status && check_gitlab_web; then
            log_message "✅ GitLab restarted successfully"
        else
            log_message "❌ GitLab restart failed - manual intervention required"
        fi
    fi
    
    log_message "=== GitLab Health Check Completed ==="
}

# Запуск
main "$@"


