# 🚇 Cloudflare Tunnel Creation Guide

## После активации Zero Trust

### 1️⃣ НАЙТИ СЕКЦИЮ ТУННЕЛЕЙ

**Вариант A: Прямая ссылка**
- Открыть: https://dash.cloudflare.com/zero-trust/access/tunnels

**Вариант B: Навигация**
1. В левом меню найти **"Access"**
2. Нажать на **"Access"**
3. Внутри найти **"Tunnels"**

**Вариант C: Альтернативная навигация**
1. В левом меню найти **"Networks"**
2. Нажать на **"Networks"**
3. Внутри найти **"Tunnels"**

### 2️⃣ СОЗДАТЬ ТУННЕЛЬ

1. Нажать кнопку **"Create tunnel"** (или **"Add tunnel"**, **"New tunnel"**)
2. Ввести имя туннеля: `gitlab-tunnel`
3. Нажать **"Save tunnel"**

### 3️⃣ ПОЛУЧИТЬ КОМАНДУ УСТАНОВКИ

После создания туннеля Cloudflare покажет команду установки:
```bash
cloudflared tunnel --cred-file /root/.cloudflared/[UUID].json run gitlab-tunnel
```

**Скопировать эту команду!**

### 4️⃣ НАСТРОИТЬ PUBLIC HOSTNAME

1. В созданном туннеле нажать **"Configure"**
2. В разделе **"Public hostname"**:
   - **Subdomain**: `gitlab`
   - **Domain**: `trustforge.uk`
   - **Service**: `http://192.168.1.10:80`
3. Нажать **"Save hostname"**

### 5️⃣ УСТАНОВИТЬ CLOUDFLARED

На сервере GitLab (192.168.1.10):

```bash
# Ubuntu/Debian
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Или через snap
sudo snap install cloudflared
```

### 6️⃣ ЗАПУСТИТЬ ТУННЕЛЬ

```bash
# Выполнить команду из шага 3
cloudflared tunnel --cred-file /root/.cloudflared/[UUID].json run gitlab-tunnel
```

### 7️⃣ ПРОВЕРИТЬ РАБОТУ

```bash
# Проверить доступность
curl -I https://gitlab.trustforge.uk

# Должен вернуть ответ от GitLab
```

### 8️⃣ ОБНОВИТЬ RENDER

1. Перейти: https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg
2. Settings → Build & Deploy → Update Repository
3. URL: `https://gitlab.trustforge.uk/root/ssl-monitor-pro.git`
4. Save Changes
5. Manual Deploy → Deploy latest commit

## Troubleshooting

### Туннель не создается
- Убедиться что Zero Trust активирован
- Попробовать обновить страницу
- Проверить права доступа к аккаунту

### Команда установки не показывается
- Нажать "Configure" в созданном туннеле
- Скопировать команду из раздела "Quick Start"

### GitLab недоступен через туннель
- Проверить что GitLab работает: `curl -I http://localhost:80`
- Проверить правильность Service URL в hostname
- Проверить логи cloudflared

## Результат
- ✅ `https://gitlab.trustforge.uk` → GitLab
- ✅ Render может подключиться
- ✅ Полная интеграция CI/CD
- ✅ Безопасность и надежность
