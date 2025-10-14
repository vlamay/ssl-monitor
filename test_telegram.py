#!/usr/bin/env python3
import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv('backend/.env.production')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7409378539:AAHGan44vnafc8FOWgyF0FnE3mmHaYhdhrs')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not BOT_TOKEN or not CHAT_ID:
    print("❌ TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не настроены")
    sys.exit(1)

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=data)
    return response.json()

# Test message
message = """
✅ <b>SSL Monitor Pro - Production Test</b>

🚀 Backend: Online
🎨 Frontend: Online
💳 Stripe: Configured
📊 Monitoring: Active

🔗 <a href="https://cloudsre.xyz">cloudsre.xyz</a>
📧 devops@upcz.cz
"""

result = send_message(message)

if result.get('ok'):
    print("✅ Telegram test message sent successfully!")
else:
    print(f"❌ Failed to send message: {result}")
