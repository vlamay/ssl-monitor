#!/usr/bin/env python3
"""
Test Telegram bot connection and get CHAT_ID
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment variables
os.environ['TELEGRAM_BOT_TOKEN'] = '7409378539:AAHGan44vnafc8FOWgyF0FnE3mmHaYhdhrs'

from utils.telegram import test_telegram_connection
import requests

print("🤖 Telegram Bot Connection Test")
print("=" * 60)
print()

# Test 1: Get bot info
print("📋 Step 1: Testing bot connection...")
result = test_telegram_connection()

if result['ok']:
    bot = result['bot']
    print(f"✅ Bot connected successfully!")
    print(f"   Name: {bot.get('first_name')}")
    print(f"   Username: @{bot.get('username')}")
    print(f"   ID: {bot.get('id')}")
    print()
else:
    print(f"❌ Bot connection failed: {result.get('error')}")
    sys.exit(1)

# Test 2: Get chat ID from updates
print("📋 Step 2: Getting CHAT_ID from messages...")
print()
print("⚠️  Please send a message to @CloudereMonitorBot first!")
print("   Then press Enter to continue...")
input()

token = '7409378539:AAHGan44vnafc8FOWgyF0FnE3mmHaYhdhrs'
url = f"https://api.telegram.org/bot{token}/getUpdates"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if data['ok'] and len(data['result']) > 0:
        print("✅ Found messages:")
        print()
        
        chat_ids = set()
        for update in data['result']:
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                username = update['message']['from'].get('username', 'N/A')
                first_name = update['message']['from'].get('first_name', 'N/A')
                text = update['message'].get('text', '')[:50]
                
                chat_ids.add(chat_id)
                
                print(f"   Chat ID: {chat_id}")
                print(f"   Name: {first_name}")
                print(f"   Username: @{username}")
                print(f"   Message: {text}")
                print()
        
        if chat_ids:
            main_chat_id = list(chat_ids)[0]
            print("=" * 60)
            print()
            print("📝 Add this to your .env.production:")
            print()
            print(f"TELEGRAM_CHAT_ID={main_chat_id}")
            print()
            print("=" * 60)
            
            # Test 3: Send test message
            print()
            print("📋 Step 3: Sending test notification...")
            
            os.environ['TELEGRAM_CHAT_ID'] = str(main_chat_id)
            from utils.telegram import send_telegram_alert
            
            test_message = """
✅ <b>SSL Monitor Pro - Test Notification</b>

🚀 Backend: Ready
🎨 Frontend: Ready  
💳 Stripe: Configured
📊 Monitoring: Active

<a href="https://cloudsre.xyz">cloudsre.xyz</a>
"""
            
            if send_telegram_alert(test_message.strip()):
                print("✅ Test message sent successfully!")
                print()
                print("🎉 Telegram bot is fully configured and working!")
            else:
                print("❌ Failed to send test message")
    else:
        print("❌ No messages found!")
        print("   Please send a message to @CloudereMonitorBot and try again")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    sys.exit(1)

