# 💻 Установка GitLab на локальный ноутбук

## Ваша конфигурация

- **Локальный IP:** `192.168.1.10`
- **GitLab URL:** `http://192.168.1.10`
- **Email:** `sre.engineer.vm@gmail.com`
- **Цель:** Локальная разработка и тестирование

---

## ⚠️ ВАЖНО: Требования к системе

**GitLab требует значительных ресурсов:**
- **RAM:** Минимум 4GB (рекомендуется 8GB+)
- **CPU:** 2+ ядра
- **Disk:** 10GB+ свободного места
- **Порты:** 80, 443, 22 (будут заняты GitLab)

**Если у вас меньше ресурсов - GitLab будет работать медленно или нестабильно.**

---

## 🚀 Быстрая установка

### Шаг 1: Запустите установку

```bash
# В директории проекта
cd /home/vmaidaniuk/Cursor/ssl-monitor-final

# Запустите локальную установку
bash gitlab-local-install.sh
```

### Шаг 2: Подтвердите установку

Скрипт спросит подтверждение. Введите `y` и нажмите Enter.

### Шаг 3: Введите пароль sudo

Когда потребуется, введите пароль вашего пользователя для sudo.

### Шаг 4: Дождитесь завершения

Установка займет **10-15 минут**.

---

## 📋 Что происходит во время установки

```
[1/8] Updating system...
[2/8] Installing dependencies...
[3/8] Configuring firewall...
[4/8] Adding GitLab repository...
[5/8] Installing GitLab CE...
[6/8] Configuring GitLab for local development...
[7/8] Running GitLab reconfiguration...
[8/8] Retrieving root password...
```

---

## 🔐 После установки

### 1. Сохраните пароль root

В конце установки вы увидите:
```
🔑 Root Password: xA7bK9mL2pR8qW4vT5nY6zU3...
```

**⚠️ СКОПИРУЙТЕ И СОХРАНИТЕ ЭТОТ ПАРОЛЬ!**

### 2. Откройте GitLab

В браузере перейдите: **http://192.168.1.10**

### 3. Войдите в систему

- **Username:** `root`
- **Password:** (пароль из установки)

### 4. Смените пароль

- Нажмите на аватар (правый верхний угол)
- **Preferences → Password**
- Установите новый пароль

---

## 🎯 Использование для разработки

### Импорт проекта

1. В GitLab нажмите **New project**
2. **Import project → GitHub**
3. Введите GitHub Personal Access Token
4. Выберите `ssl-monitor-final`
5. Нажмите **Import**

### Настройка CI/CD

1. **Settings → CI/CD → Variables**
2. Добавьте переменные:
   - `DATABASE_URL`
   - `REDIS_URL`
   - `SECRET_KEY`
   - и другие секреты

### Обновление локального git remote

```bash
cd /home/vmaidaniuk/Cursor/ssl-monitor-final

# Добавьте GitLab как remote
git remote add gitlab http://192.168.1.10/root/ssl-monitor-final.git

# Или замените origin
git remote set-url origin http://192.168.1.10/root/ssl-monitor-final.git
```

---

## 🛠️ Полезные команды

```bash
# Проверить статус GitLab
sudo gitlab-ctl status

# Перезапустить GitLab
sudo gitlab-ctl restart

# Просмотр логов
sudo gitlab-ctl tail

# Health check
sudo gitlab-rake gitlab:check

# Остановить GitLab (освободить ресурсы)
sudo gitlab-ctl stop

# Запустить GitLab
sudo gitlab-ctl start
```

---

## ⚡ Альтернатива: Docker GitLab (легче для ноутбука)

Если GitLab слишком тяжелый для вашего ноутбука, используйте Docker:

```bash
# Создайте docker-compose.yml
cat > docker-compose.gitlab.yml << 'EOF'
version: '3.8'
services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    container_name: gitlab
    restart: always
    hostname: '192.168.1.10'
    ports:
      - '8080:80'
      - '8443:443'
      - '2222:22'
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'http://192.168.1.10:8080'
        gitlab_rails['gitlab_shell_ssh_port'] = 2222
        postgresql['shared_buffers'] = "64MB"
        puma['worker_processes'] = 2
        sidekiq['max_concurrency'] = 5
    volumes:
      - gitlab_config:/etc/gitlab
      - gitlab_logs:/var/log/gitlab
      - gitlab_data:/var/opt/gitlab

volumes:
  gitlab_config:
  gitlab_logs:
  gitlab_data:
EOF

# Запустите GitLab в Docker
docker-compose -f docker-compose.gitlab.yml up -d

# Получите пароль root
docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password
```

**GitLab будет доступен по адресу:** `http://192.168.1.10:8080`

---

## 🚨 Возможные проблемы

### Проблема: "Out of Memory"

**Решение:** Остановите GitLab когда не используете:

```bash
sudo gitlab-ctl stop
```

### Проблема: Порты заняты

**Решение:** Проверьте, что использует порты:

```bash
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

### Проблема: Медленная работа

**Решение:** Уменьшите потребление ресурсов:

```bash
sudo nano /etc/gitlab/gitlab.rb
```

Добавьте:
```ruby
puma['worker_processes'] = 1
sidekiq['max_concurrency'] = 2
postgresql['shared_buffers'] = "64MB"
```

Затем:
```bash
sudo gitlab-ctl reconfigure
```

---

## 🎯 Рекомендации

### Для разработки:
- ✅ Используйте локальный GitLab
- ✅ Останавливайте когда не нужен
- ✅ Делайте backup конфигурации

### Для продакшена:
- ❌ Не используйте ноутбук
- ✅ Арендуйте VPS с 4GB+ RAM
- ✅ Настройте SSL и домен

---

## 📊 Сравнение вариантов

| Вариант | RAM | CPU | Установка | Производительность |
|---------|-----|-----|-----------|-------------------|
| **Локальный GitLab** | 4GB+ | 2+ ядра | 15 мин | Медленно |
| **Docker GitLab** | 2GB+ | 1+ ядро | 5 мин | Быстро |
| **VPS GitLab** | 4GB+ | 2+ ядра | 20 мин | Отлично |

---

## 🎉 Готово!

После установки у вас будет:

- ✅ GitLab на `http://192.168.1.10`
- ✅ Готовность к импорту репозиториев
- ✅ CI/CD для тестирования
- ✅ Локальная среда разработки

**Следующий шаг:** Импорт проекта `ssl-monitor-final` из GitHub

---

*Создано: 12 октября 2025*  
*Локальный IP: 192.168.1.10*  
*Email: sre.engineer.vm@gmail.com*

**Удачной разработки!** 💻🚀
