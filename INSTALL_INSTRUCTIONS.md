# 🚀 Персонализированная инструкция по установке GitLab

## Ваша конфигурация

- **Сервер IP:** `193.179.120.33`
- **Домен:** `gitlab.cloudsre.xyz`
- **Email:** `sre.engineer.vm@gmail.com`
- **Время установки:** ~20 минут

---

## ⚡ БЫСТРЫЙ СТАРТ - 3 КОМАНДЫ

```bash
# 1. Скопируйте скрипт на сервер
scp gitlab-install.sh root@193.179.120.33:/root/

# 2. Подключитесь к серверу
ssh root@193.179.120.33

# 3. Запустите установку
chmod +x gitlab-install.sh && sudo bash gitlab-install.sh sre.engineer.vm@gmail.com
```

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### ШАГ 1: Настройка DNS в Cloudflare (2 минуты)

**Откройте:** https://dash.cloudflare.com/

**Действия:**
1. Выберите домен: **cloudsre.xyz**
2. Перейдите в: **DNS → Records**
3. Нажмите: **Add record**

**Настройки записи:**
```
Type:    A
Name:    gitlab
Content: 193.179.120.33
TTL:     Auto
Proxy:   ⚪ DNS only (СЕРОЕ облачко - не оранжевое!)
```

4. Нажмите **Save**

**⚠️ ВАЖНО:** Не включайте оранжевое облачко сейчас! Включим позже.

---

### ШАГ 2: Копирование скрипта на сервер (1 минута)

**На вашей локальной машине** (в директории проекта):

```bash
cd /home/vmaidaniuk/Cursor/ssl-monitor-final

# Скопируйте скрипт
scp gitlab-install.sh root@193.179.120.33:/root/
```

Если запросит пароль - введите root пароль от сервера.

**Альтернатива (если нет root доступа):**

```bash
scp gitlab-install.sh your-username@193.179.120.33:~/
```

---

### ШАГ 3: Подключение к серверу (1 минута)

```bash
ssh root@193.179.120.33
```

Или с обычным пользователем:

```bash
ssh your-username@193.179.120.33
```

---

### ШАГ 4: Запуск установки (15 минут)

**На сервере выполните:**

```bash
# Сделайте скрипт исполняемым
chmod +x gitlab-install.sh

# Запустите установку
sudo bash gitlab-install.sh sre.engineer.vm@gmail.com
```

**Что будет происходить:**

```
=================================================
  GitLab CE Installation Script
  Domain: gitlab.cloudsre.xyz
  Email: sre.engineer.vm@gmail.com
=================================================

[1/8] Updating system...
[2/8] Installing dependencies...
[3/8] Configuring firewall...
[4/8] Adding GitLab repository...
[5/8] Installing GitLab CE (this may take several minutes)...
[6/8] Configuring GitLab with SSL...
[7/8] Running GitLab reconfiguration...
[8/8] Retrieving root password...
```

**Подождите 10-15 минут.** Установка GitLab занимает время.

---

### ШАГ 5: Сохранение пароля root (КРИТИЧНО!)

После завершения установки вы увидите:

```
=================================================
  GitLab Installation Complete!
=================================================

🎉 GitLab URL: https://gitlab.cloudsre.xyz
👤 Username: root
🔑 Root Password: xA7bK9mL2pR8qW4vT5nY6zU3cH8vB2nA

⚠️  IMPORTANT: Save this password! This file will be deleted in 24 hours.
```

**⚠️ СКОПИРУЙТЕ ПАРОЛЬ ПРЯМО СЕЙЧАС!**

Сохраните его в безопасное место (менеджер паролей).

---

### ШАГ 6: Первый вход в GitLab (2 минуты)

1. **Откройте браузер:** https://gitlab.cloudsre.xyz

2. **Войдите:**
   - Username: `root`
   - Password: (пароль из предыдущего шага)

3. **Сразу смените пароль:**
   - Нажмите на аватар (правый верхний угол)
   - **Preferences → Password**
   - Установите новый надежный пароль

---

### ШАГ 7: Включение Cloudflare Proxy (1 минута)

**Теперь, когда SSL работает, включаем защиту:**

1. Вернитесь в **Cloudflare Dashboard → DNS**
2. Найдите запись `gitlab` с IP `193.179.120.33`
3. Нажмите на **серое облачко** 🌐
4. Оно должно стать **оранжевым** 🟠 (Proxied)

**Настройте SSL режим:**

1. Перейдите: **SSL/TLS → Overview**
2. Установите: **Full (strict)**

**Проверьте:** https://gitlab.cloudsre.xyz все еще работает

---

### ШАГ 8: Проверка установки (2 минуты)

**На сервере выполните:**

```bash
# Проверка статуса всех сервисов
sudo gitlab-ctl status

# Проверка здоровья GitLab
sudo gitlab-rake gitlab:check
```

Все сервисы должны быть в статусе `run`.

---

## ✅ ЧЕКЛИСТ УСТАНОВКИ

- [ ] DNS запись A создана: gitlab → 193.179.120.33 (серое облачко)
- [ ] Скрипт скопирован на сервер
- [ ] Скрипт запущен с email: sre.engineer.vm@gmail.com
- [ ] Установка завершена успешно
- [ ] Root пароль скопирован и сохранен
- [ ] Первый вход выполнен: https://gitlab.cloudsre.xyz
- [ ] Пароль изменен на новый
- [ ] Cloudflare Proxy включен (оранжевое облачко)
- [ ] SSL режим: Full (strict)
- [ ] `gitlab-ctl status` показывает все сервисы работают

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

### 1. Импорт репозитория из GitHub

**В GitLab:**

1. Нажмите **New project**
2. Выберите **Import project → GitHub**
3. Введите GitHub Personal Access Token
4. Найдите репозиторий `ssl-monitor-final`
5. Нажмите **Import**

**Создание GitHub Token:**
- https://github.com/settings/tokens
- Generate new token (classic)
- Scopes: `repo` + `admin:org`

### 2. Обновите локальный git remote

```bash
cd /home/vmaidaniuk/Cursor/ssl-monitor-final

# Замените origin на GitLab
git remote set-url origin https://gitlab.cloudsre.xyz/root/ssl-monitor-final.git

# Или добавьте как второй remote
git remote add gitlab https://gitlab.cloudsre.xyz/root/ssl-monitor-final.git

# Проверьте
git remote -v
```

### 3. Настройте CI/CD переменные

**Settings → CI/CD → Variables**

Добавьте секреты:
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Для каждой переменной:
- ✅ Mask variable
- ✅ Protect variable

---

## 🚨 TROUBLESHOOTING

### Проблема: "Connection refused" при подключении к серверу

**Проверьте:**
```bash
ping 193.179.120.33
```

Если не отвечает - проверьте firewall на сервере или у хостинг-провайдера.

### Проблема: "502 Bad Gateway" после установки

**Решение:** Подождите 5-10 минут и перезапустите:

```bash
sudo gitlab-ctl restart
```

### Проблема: Let's Encrypt не выпускает SSL

**Причина:** Cloudflare proxy включен слишком рано.

**Решение:**
1. Отключите Cloudflare proxy (серое облачко)
2. На сервере: `sudo gitlab-ctl reconfigure`
3. Подождите 5 минут
4. Снова включите proxy

### Проблема: Забыли сохранить пароль

**Решение:**

```bash
# Если файл еще не удален (<24 часов)
sudo cat /etc/gitlab/initial_root_password

# Если файл удален - сброс пароля
sudo gitlab-rake "gitlab:password:reset[root]"
```

### Проблема: Сервер "Out of Memory"

**Решение:** Уменьшите потребление памяти:

```bash
sudo nano /etc/gitlab/gitlab.rb
```

Добавьте:
```ruby
puma['worker_processes'] = 2
sidekiq['max_concurrency'] = 5
postgresql['shared_buffers'] = "128MB"
```

```bash
sudo gitlab-ctl reconfigure
```

---

## 📞 ПОЛЕЗНЫЕ КОМАНДЫ

```bash
# Подключение к серверу
ssh root@193.179.120.33

# Статус GitLab
sudo gitlab-ctl status

# Перезапуск всех сервисов
sudo gitlab-ctl restart

# Просмотр логов
sudo gitlab-ctl tail

# Health check
sudo gitlab-rake gitlab:check

# Просмотр пароля root (если файл еще существует)
sudo cat /etc/gitlab/initial_root_password

# Создание backup
sudo gitlab-backup create

# Информация о версии
sudo gitlab-rake gitlab:env:info
```

---

## 📊 ИНФОРМАЦИЯ О СЕРВЕРЕ

```
IP Address:    193.179.120.33
Domain:        gitlab.cloudsre.xyz
Full URL:      https://gitlab.cloudsre.xyz
Admin Email:   sre.engineer.vm@gmail.com
Admin User:    root
DNS Provider:  Cloudflare
SSL Provider:  Let's Encrypt (auto-renewed)
```

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

- **Полный гид:** [GITLAB_MIGRATION_GUIDE.md](GITLAB_MIGRATION_GUIDE.md)
- **Чек-лист:** [GITLAB_CHECKLIST.md](GITLAB_CHECKLIST.md)
- **CI/CD конфиг:** [.gitlab-ci.yml](.gitlab-ci.yml)
- **GitLab Docs:** https://docs.gitlab.com/

---

## 🎉 ПОЗДРАВЛЯЕМ!

После выполнения всех шагов у вас будет:

- ✅ GitLab CE на выделенном сервере
- ✅ Домен gitlab.cloudsre.xyz с SSL
- ✅ Защита через Cloudflare
- ✅ Готовность к импорту репозиториев
- ✅ CI/CD готов к настройке

**Время на установку: ~20-25 минут**

---

*Создано: 12 октября 2025*  
*IP: 193.179.120.33*  
*Домен: gitlab.cloudsre.xyz*  
*Email: sre.engineer.vm@gmail.com*

**Удачи! 🚀**

