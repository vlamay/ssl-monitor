#!/usr/bin/env python3
import requests
import json

BOT_TOKEN = "7409378539:AAHGan44vnafc8FOWgyF0FnE3mmHaYhdhrs"

print("🤖 Telegram Bot Setup")
print("=" * 50)
print("")
print("Отправьте любое сообщение боту, затем запустите этот скрипт")
print("")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
data = response.json()

if data['ok'] and len(data['result']) > 0:
    for update in data['result']:
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            username = update['message']['from'].get('username', 'N/A')
            first_name = update['message']['from'].get('first_name', 'N/A')
            
            print(f"✅ Found Chat:")
            print(f"   Chat ID: {chat_id}")
            print(f"   Username: @{username}")
            print(f"   Name: {first_name}")
            print("")
            print(f"📝 Добавьте в .env:")
            print(f"   TELEGRAM_CHAT_ID={chat_id}")
            print("")
else:
    print("❌ Нет сообщений. Отправьте сообщение боту сначала!")
    print(f"   Бот: @YourBotName")
