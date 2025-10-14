# ⚡ GitLab CE Quick Start Guide

## Быстрая установка GitLab на Ubuntu для cloudsre.xyz

**Email для администратора:** sre.engineer.vm@gmail.com  
**Домен:** gitlab.cloudsre.xyz  
**Время установки:** ~15 минут

---

## 📋 Перед началом

### Что вам нужно:

1. ✅ **Сервер Ubuntu** (20.04 LTS или новее)
   - Минимум: 4GB RAM, 2 CPU cores, 20GB disk
   - Публичный IP-адрес

2. ✅ **Доступ к Cloudflare**
   - Домен `cloudsre.xyz` добавлен в Cloudflare
   - DNS запись создана (см. ниже)

3. ✅ **SSH доступ** к серверу

---

## 🌐 ШАГ 1: Настройка DNS в Cloudflare (2 минуты)

### Откройте Cloudflare Dashboard

1. Перейдите на https://dash.cloudflare.com/
2. Выберите домен **cloudsre.xyz**
3. Перейдите в **DNS → Records**

### Создайте A запись

```
Type:    A
Name:    gitlab
Content: <IP_ВАШЕГО_СЕРВЕРА>
TTL:     Auto
Proxy:   ⚪ DNS only (серое облачко) ← ВАЖНО!
```

**Пример:**
- Если IP сервера: `185.123.45.67`
- Тогда:
  ```
  Type: A
  Name: gitlab  
  IPv4 address: 185.123.45.67
  Proxy status: DNS only (серое облачко 🌐)
  ```

4. Нажмите **Save**

### ⚠️ ВАЖНО: Не включайте оранжевое облачко (Proxy) на этом этапе!

Let's Encrypt нужен прямой доступ к серверу для выпуска SSL сертификата. Мы включим Cloudflare Proxy **после** установки GitLab.

---

## 💻 ШАГ 2: Подключение к серверу (1 минута)

Откройте терминал и подключитесь:

```bash
ssh root@YOUR_SERVER_IP
```

Замените `YOUR_SERVER_IP` на IP вашего сервера.

Если у вас не root, используйте пользователя с sudo:

```bash
ssh your-username@YOUR_SERVER_IP
```

---

## 📦 ШАГ 3: Загрузка и запуск скрипта установки (15 минут)

### Вариант A: Если скрипт уже на сервере

Скопируйте файл `gitlab-install.sh` на сервер:

```bash
# На вашей локальной машине:
scp gitlab-install.sh root@YOUR_SERVER_IP:/root/
```

Затем на сервере:

```bash
chmod +x gitlab-install.sh
sudo bash gitlab-install.sh sre.engineer.vm@gmail.com
```

### Вариант B: Скачать напрямую с GitHub (после миграции)

```bash
wget https://raw.githubusercontent.com/yourusername/ssl-monitor-final/main/gitlab-install.sh
chmod +x gitlab-install.sh
sudo bash gitlab-install.sh sre.engineer.vm@gmail.com
```

### Вариант C: Создать скрипт вручную на сервере

```bash
nano gitlab-install.sh
```

Скопируйте содержимое файла `gitlab-install.sh` из проекта, вставьте в nano.

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

Затем:

```bash
chmod +x gitlab-install.sh
sudo bash gitlab-install.sh sre.engineer.vm@gmail.com
```

---

## ⏳ ШАГ 4: Ожидание установки (10-15 минут)

Скрипт автоматически:

1. ✅ Обновит систему
2. ✅ Установит зависимости (Postfix, OpenSSH, и т.д.)
3. ✅ Настроит firewall
4. ✅ Добавит репозиторий GitLab
5. ✅ Установит GitLab CE
6. ✅ Настроит Let's Encrypt SSL
7. ✅ Покажет пароль root

### Что вы увидите:

```
=================================================
  GitLab CE Installation Script
  Domain: gitlab.cloudsre.xyz
  Email: sre.engineer.vm@gmail.com
=================================================

[1/8] Updating system...
[2/8] Installing dependencies...
[3/8] Configuring firewall...
...
[8/8] Retrieving root password...

=================================================
  GitLab Installation Complete!
=================================================

🎉 GitLab URL: https://gitlab.cloudsre.xyz
👤 Username: root
🔑 Root Password: xA7bK9mL2pR8qW4vT5nY6zU3...

⚠️  IMPORTANT: Save this password!
```

### ⚠️ СКОПИРУЙТЕ И СОХРАНИТЕ ПАРОЛЬ!

Файл с паролем будет удален через 24 часа.

---

## 🔐 ШАГ 5: Первый вход в GitLab (2 минуты)

1. Откройте в браузере: **https://gitlab.cloudsre.xyz**

2. Войдите с данными:
   - **Username:** `root`
   - **Password:** (пароль из предыдущего шага)

3. **Сразу смените пароль!**
   - Нажмите на аватар (правый верхний угол)
   - **Preferences → Password**
   - Установите новый безопасный пароль

4. Обновите email (опционально):
   - **Preferences → Email**
   - Добавьте: `sre.engineer.vm@gmail.com`

---

## 🟠 ШАГ 6: Включение Cloudflare Proxy (1 минута)

Теперь, когда SSL работает:

1. Вернитесь в **Cloudflare Dashboard → DNS**
2. Найдите запись `gitlab` (Type: A)
3. Нажмите на **серое облачко** 🌐 чтобы превратить его в **оранжевое** 🟠
4. Статус должен стать: **Proxied**

Это даст вам:
- 🛡️ Защиту от DDoS
- 🔒 Скрытие IP сервера
- ⚡ Кэширование через Cloudflare CDN

5. Перейдите в **SSL/TLS → Overview**
6. Установите режим: **Full (strict)**

---

## ✅ ШАГ 7: Проверка работоспособности (2 минуты)

### Проверьте, что GitLab работает:

```bash
# На сервере:
sudo gitlab-ctl status
```

Все сервисы должны быть в статусе `run`.

### Запустите health check:

```bash
sudo gitlab-rake gitlab:check
```

Не должно быть критических ошибок.

### Проверьте доступность:

Откройте в браузере:
- ✅ https://gitlab.cloudsre.xyz (должен работать)
- ✅ Должен быть зеленый замочек (SSL)
- ✅ Вход работает

---

## 🚨 Возможные проблемы и решения

### Проблема: "502 Bad Gateway"

**Решение:** Подождите 5-10 минут после установки. GitLab запускается долго.

```bash
sudo gitlab-ctl restart
sudo gitlab-ctl tail  # Смотрим логи
```

### Проблема: Let's Encrypt SSL не выпускается

**Причина:** Cloudflare proxy (оранжевое облачко) был включен слишком рано.

**Решение:**
1. Отключите Cloudflare proxy (серое облачко)
2. На сервере: `sudo gitlab-ctl reconfigure`
3. Дождитесь получения SSL (5-10 минут)
4. Снова включите Cloudflare proxy

### Проблема: "Out of Memory"

**Решение:** GitLab требует минимум 4GB RAM.

Если RAM меньше, уменьшите потребление:

```bash
sudo nano /etc/gitlab/gitlab.rb
```

Добавьте:

```ruby
puma['worker_processes'] = 2
sidekiq['max_concurrency'] = 5
postgresql['shared_buffers'] = "128MB"
```

Затем:

```bash
sudo gitlab-ctl reconfigure
```

### Проблема: Не могу найти пароль root

**Решение:**

```bash
sudo cat /etc/gitlab/initial_root_password
```

Если файл удален (прошло >24 часа), сбросьте пароль:

```bash
sudo gitlab-rake "gitlab:password:reset[root]"
```

---

## 📊 Полезные команды

```bash
# Статус всех сервисов
sudo gitlab-ctl status

# Перезапуск GitLab
sudo gitlab-ctl restart

# Просмотр всех логов
sudo gitlab-ctl tail

# Логи конкретного сервиса
sudo gitlab-ctl tail nginx

# Health check
sudo gitlab-rake gitlab:check

# Информация о версии
sudo gitlab-rake gitlab:env:info

# Создать backup
sudo gitlab-backup create

# Reconfigure после изменения настроек
sudo gitlab-ctl reconfigure
```

---

## 🎯 Следующие шаги

После успешной установки:

### 1. Импорт проекта из GitHub

См. [GITLAB_MIGRATION_GUIDE.md](GITLAB_MIGRATION_GUIDE.md), раздел "Part 4: Repository Migration"

**Кратко:**
1. В GitLab: **New project → Import project → GitHub**
2. Введите GitHub Personal Access Token
3. Выберите репозиторий `ssl-monitor-final`
4. Нажмите **Import**

### 2. Настройка CI/CD

1. Проверьте, что `.gitlab-ci.yml` присутствует в репозитории
2. Добавьте CI/CD переменные: **Settings → CI/CD → Variables**
3. Добавьте секреты (DATABASE_URL, STRIPE_KEY, и т.д.)

### 3. Создание команды

1. **Admin Area → Users → New user**
2. Создайте аккаунты для членов команды
3. Назначьте роли (Developer, Maintainer, и т.д.)

### 4. Настройка бэкапов

```bash
# Создать cron job для ежедневного бэкапа
sudo crontab -e
```

Добавьте:

```
0 2 * * * /opt/gitlab/bin/gitlab-backup create CRON=1
```

---

## 📞 Поддержка

**Email:** sre.engineer.vm@gmail.com  
**Документация:** [GITLAB_MIGRATION_GUIDE.md](GITLAB_MIGRATION_GUIDE.md)  
**Чек-лист:** [GITLAB_CHECKLIST.md](GITLAB_CHECKLIST.md)  
**GitLab Docs:** https://docs.gitlab.com/

---

## 📋 Краткая справка команд

### На локальной машине (копирование скрипта):

```bash
cd /home/vmaidaniuk/Cursor/ssl-monitor-final
scp gitlab-install.sh root@YOUR_SERVER_IP:/root/
```

### На сервере (установка):

```bash
chmod +x gitlab-install.sh
sudo bash gitlab-install.sh sre.engineer.vm@gmail.com
```

### Проверка после установки:

```bash
sudo gitlab-ctl status
sudo gitlab-rake gitlab:check
sudo cat /etc/gitlab/initial_root_password
```

---

## ⏱️ Временная шкала

| Шаг | Действие | Время |
|-----|----------|-------|
| 1 | Настройка DNS | 2 мин |
| 2 | Подключение к серверу | 1 мин |
| 3 | Запуск скрипта | 15 мин |
| 4 | Первый вход | 2 мин |
| 5 | Cloudflare Proxy | 1 мин |
| 6 | Проверка | 2 мин |

**Общее время: ~20-25 минут**

---

## ✨ Готово!

После выполнения всех шагов у вас будет:

- ✅ Работающий GitLab CE на `https://gitlab.cloudsre.xyz`
- ✅ SSL сертификат от Let's Encrypt
- ✅ Защита через Cloudflare
- ✅ Готовность к импорту репозитория

**Следующий документ:** [GITLAB_MIGRATION_GUIDE.md](GITLAB_MIGRATION_GUIDE.md) для импорта проекта из GitHub.

---

**Удачной установки!** 🚀

*Создано: 12 октября 2025*  
*Проект: SSL Monitor Pro*  
*Автор: DevOps Team*

