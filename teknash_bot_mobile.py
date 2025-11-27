#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram bot - Heroku/Render uchun
"""

import requests
import time
import os
from datetime import datetime

BOT_TOKEN = "8453590241:AAE2XXL5_7FoTg6IMoZCx7KmJgM-cwGc6E0"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def log_message(message):
    """Log xabarlar"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def send_message(chat_id, text, reply_to_message_id=None):
    """Xabar yuborish"""
    try:
        url = f"{BASE_URL}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
            
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        log_message(f"Xabar yuborishda xato: {e}")
        return None

def process_updates():
    """Xabarlarni qayta ishlash"""
    offset = 0
    processed_count = 0
    
    log_message("🤖 Mobil bot ishga tushdi!")
    
    while True:
        try:
            url = f"{BASE_URL}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url)
            data = response.json()
            
            if not data.get("ok"):
                break
                
            updates = data.get("result", [])
            if not updates:
                continue
                
            for update in updates:
                update_id = update.get("update_id")
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "")
                first_name = message.get("from", {}).get("first_name", "Foydalanuvchi")
                
                if "UZ-5018" in text:
                    reply_text = f"👋 Assalomu alaykum {first_name}!\n\n🆔 Sizning kod: **UZ-5018**\n✅ Ro'yxatdan o'tgan\n🎯 Tizimda aktiv\n\nSalom bering va bot to'liq ishlayapti!"
                elif "/start" in text:
                    reply_text = f"🚀 Mobil bot ishga tushdi!\n\n👋 Assalomu alaykum {first_name}!\n\n✅ **Bot 24/7 ishlayapti**\n📱 Mobil deployment\n\nUZ-5018 kodi bilan test qiling!"
                else:
                    reply_text = f"👋 Assalomu alaykum {first_name}!\n\n✅ **Bot javob berishga tayyor!**\n\nKo'proq qo'llab-quvvatlash: @Kvantexno"
                
                result = send_message(chat_id, reply_text, update.get("message", {}).get("message_id"))
                if result and result.get("ok"):
                    log_message(f"✅ Javob yuborildi: {first_name}")
                    processed_count += 1
                
                offset = update_id + 1
                
            time.sleep(1)
            
        except KeyboardInterrupt:
            log_message("Bot to'xtatildi")
            break
        except Exception as e:
            log_message(f"Xato: {e}")
            time.sleep(10)
    
    log_message(f"✅ Jami qayta ishlandi: {processed_count} ta xabar")

if __name__ == "__main__":
    log_message("=" * 50)
    log_message("📱 MOBIL TELEGRAM BOT")
    log_message("=" * 50)
    process_updates()
