# 🌐 No-IP Quick Setup - Альтернатива DuckDNS

## Если DuckDNS не работает

### 1️⃣ РЕГИСТРАЦИЯ NO-IP
1. Перейти: https://www.noip.com/
2. Нажать "Sign Up"
3. Заполнить форму:
   - Email
   - Username
   - Password
4. Подтвердить email

### 2️⃣ СОЗДАНИЕ ДОМЕНА
1. После входа нажать "Add Hostname"
2. Ввести:
   - Hostname: `ssl-gitlab`
   - Domain: выбрать `.ddns.net` или `.hopto.org`
   - IP Address: оставить пустым (авто)
3. Нажать "Create Hostname"
4. Результат: `ssl-gitlab.ddns.net`

### 3️⃣ ПОЛУЧЕНИЕ ТОКЕНА
1. Перейти в "Account" → "API"
2. Создать API ключ
3. Скопировать токен

### 4️⃣ НАСТРОЙКА РОУТЕРА
1. DDNS Settings:
   - Service: No-IP
   - Domain: `ssl-gitlab.ddns.net`
   - Username: [ваш username]
   - Password: [ваш password]
2. Port Forwarding:
   - 80 → 192.168.1.10:80
   - 443 → 192.168.1.10:443

### 5️⃣ ОБНОВЛЕНИЕ СКРИПТА
Изменить в `scripts/setup-ddns.sh`:
- Domain: `ssl-gitlab.ddns.net`
- Token: [ваш No-IP токен]

### 6️⃣ ОБНОВЛЕНИЕ RENDER
URL: `http://ssl-gitlab.ddns.net/root/ssl-monitor-pro.git`

## Преимущества No-IP
- ✅ Бесплатно (с ограничениями)
- ✅ Надежный сервис
- ✅ Хорошая поддержка роутеров
- ✅ Множество доменов

## Ограничения бесплатного плана
- ⚠️ Нужно подтверждать домен каждые 30 дней
- ⚠️ Ограниченное количество доменов
- ⚠️ Реклама в панели управления
