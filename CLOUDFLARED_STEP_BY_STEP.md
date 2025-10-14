# 🚀 ПОШАГОВАЯ УСТАНОВКА CLOUDFLARED

## 📋 КОМАНДЫ ДЛЯ КОПИРОВАНИЯ:

### 1️⃣ ПОДКЛЮЧЕНИЕ К СЕРВЕРУ:
```bash
ssh root@192.168.1.10
```

### 2️⃣ КОПИРОВАНИЕ СКРИПТА (с локальной машины):
```bash
scp install-cloudflared-final.sh root@192.168.1.10:/tmp/
```

### 3️⃣ УСТАНОВКА (на сервере):
```bash
cd /tmp
chmod +x install-cloudflared-final.sh
sudo ./install-cloudflared-final.sh
```

### 4️⃣ ПРОВЕРКА СТАТУСА:
```bash
sudo systemctl status cloudflared
```

### 5️⃣ ПРОВЕРКА ЛОГОВ:
```bash
sudo journalctl -u cloudflared -f
```

### 6️⃣ ТЕСТИРОВАНИЕ (с локальной машины):
```bash
curl -I https://gitlab.trustforge.uk/
```

## 🔧 АЛЬТЕРНАТИВНАЯ УСТАНОВКА:

Если скрипт не работает, выполнить вручную:

```bash
# 1. Установить cloudflared
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt-get update && sudo apt-get install -y cloudflared

# 2. Установить сервис с токеном
sudo cloudflared service install eyJhIjoiNDVjNTFiMzY0OGU3ZWI2YmY0MGY3ZWZlYTVlOGRmOTgiLCJ0IjoiM2JiYmI3ZDQtYWI1MS00NGMzLTkwYzEtZDhkOWViODU1OWQwIiwicyI6IlpEVXhNakF6TlRFdFpHSTFZUzAwTkdNMkxUbGlaalV0TlRNMk1HWXlNVGhqTkdFMSJ9

# 3. Запустить сервис
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# 4. Проверить статус
sudo systemctl status cloudflared
```

## ✅ ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:

### После установки:
- ✅ cloudflared сервис активен
- ✅ В логах: "Tunnel connection established"
- ✅ В Cloudflare Dashboard: туннель **ACTIVE**

### После тестирования:
- ✅ `curl -I https://gitlab.trustforge.uk/` возвращает 200 OK
- ✅ GitLab доступен через браузер
- ✅ Render может подключиться к GitLab

## 🚨 ТРУБЛШУТИНГ:

### Если сервис не запускается:
```bash
# Проверить логи:
sudo journalctl -u cloudflared -f

# Перезапустить:
sudo systemctl restart cloudflared

# Проверить конфигурацию:
sudo cloudflared tunnel list
```

### Если туннель не активен:
1. Проверить интернет соединение на сервере
2. Проверить файрвол
3. Проверить токен туннеля
4. Пересоздать туннель в Cloudflare

## 🎯 СЛЕДУЮЩИЕ ШАГИ:

После успешной установки:
1. Обновить Render на GitLab URL
2. Протестировать GitLab CI/CD
3. Запустить полный pipeline
4. Завершить миграцию

## 📞 ПОДДЕРЖКА:

Если что-то не работает:
1. Проверить логи: `sudo journalctl -u cloudflared -f`
2. Проверить статус: `sudo systemctl status cloudflared`
3. Проверить туннель: `sudo cloudflared tunnel list`
4. Перезапустить: `sudo systemctl restart cloudflared`
