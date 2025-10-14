# 🌐 Cloudflare Tunnel Setup - Лучшее решение!

## Преимущества Cloudflare Tunnel
- ✅ **Не нужен port forwarding** на роутере
- ✅ **Безопасно** - GitLab не открыт напрямую
- ✅ **Быстро** - использует ваш существующий домен
- ✅ **Надежно** - Cloudflare инфраструктура
- ✅ **Бесплатно** - входит в бесплатный план

## Пошаговая настройка

### 1️⃣ ОТКРЫТЬ CLOUDFLARE DASHBOARD
1. Перейти: https://dash.cloudflare.com/
2. Выбрать домен: `trustforge.uk`
3. Перейти в **Zero Trust** (слева в меню)

### 2️⃣ АКТИВИРОВАТЬ ZERO TRUST
1. Если Zero Trust не активирован:
   - Нажать "Get started"
   - Выбрать бесплатный план
   - Завершить настройку

### 3️⃣ СОЗДАТЬ ТУННЕЛЬ
1. В Zero Trust → **Access** → **Tunnels**
2. Нажать **"Create a tunnel"**
3. Имя туннеля: `gitlab-tunnel`
4. Нажать **"Save tunnel"**

### 4️⃣ УСТАНОВИТЬ CLOUDFLARED
1. Скопировать команду установки (будет показана)
2. На сервере GitLab (192.168.1.10) выполнить:
```bash
# Ubuntu/Debian
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Или через snap
sudo snap install cloudflared
```

### 5️⃣ ЗАПУСТИТЬ ТУННЕЛЬ
1. Скопировать команду запуска из Cloudflare
2. Выполнить на сервере GitLab:
```bash
sudo cloudflared service install [ваш-токен]
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### 6️⃣ НАСТРОИТЬ PUBLIC HOSTNAME
1. В туннеле нажать **"Configure"**
2. **Public hostname**:
   - Subdomain: `gitlab`
   - Domain: `trustforge.uk`
   - Service: `http://localhost:80`
3. Нажать **"Save hostname"**

### 7️⃣ ПРОВЕРИТЬ РАБОТУ
```bash
# Проверить доступность
curl -I https://gitlab.trustforge.uk

# Проверить GitLab
curl -I https://gitlab.trustforge.uk/root/ssl-monitor-pro.git
```

## Обновление Render

### 1️⃣ RENDER DASHBOARD
1. Перейти: https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg
2. Settings → Build & Deploy → Update Repository
3. URL: `https://gitlab.trustforge.uk/root/ssl-monitor-pro.git`
4. Save Changes

### 2️⃣ ЗАПУСТИТЬ DEPLOYMENT
1. Manual Deploy → Deploy latest commit
2. Проверить логи

## Преимущества перед DDNS

| DDNS | Cloudflare Tunnel |
|------|------------------|
| Нужен port forwarding | ❌ Не нужен |
| Открывает порты | ❌ Безопасно |
| Настройка роутера | ❌ Только сервер |
| DNS propagation | ❌ Мгновенно |
| SSL сертификаты | ❌ Автоматически |

## Troubleshooting

### Туннель не работает
```bash
# Проверить статус
sudo systemctl status cloudflared

# Перезапустить
sudo systemctl restart cloudflared

# Логи
sudo journalctl -u cloudflared -f
```

### GitLab недоступен
1. Проверить что GitLab работает: `curl -I http://localhost:80`
2. Проверить туннель: `cloudflared tunnel list`
3. Проверить hostname: `cloudflared tunnel route dns list`

## Результат
- ✅ `https://gitlab.trustforge.uk` → GitLab
- ✅ Render может подключиться
- ✅ Полная интеграция CI/CD
- ✅ Безопасность и надежность
