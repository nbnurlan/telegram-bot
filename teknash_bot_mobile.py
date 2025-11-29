#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram bot - Heroku/Render uchun + Kino qo'shildi
"""

import requests
import time
import os
import json
from datetime import datetime

BOT_TOKEN = "8453590241:AAE2XXL5_7FoTg6IMoZCx7KmJgM-cwGc6E0"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def load_movies():
    """Kino ma'lumotlarini JSON fayldan yuklash"""
    try:
        with open('movies.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log_message(f"❌ Kino faylini yuklashda xato: {e}")
        return []

def log_message(message):
    """Log xabarlar"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def send_message(chat_id, text, reply_to_message_id=None):
    """Xaar yuborish"""
    try:
        url = f"{BASE_URL}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
            
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
                    reply_text = f"👋 Assalomu alaykum {first_name}!\n\n🆔 Sizning kod: <b>UZ-5018</b>\n✅ Ro'yxatdan o'tgan\n🎯 Tizimda aktiv\n\nSalom bering va bot to'liq ishlayapti!"
                    result = send_message(chat_id, reply_text, update.get("message", {}).get("message_id"))
                    if result and result.get("ok"):
                        log_message(f"✅ Javob yuborildi: {first_name}")
                        processed_count += 1
                
                elif "/start" in text:
                    reply_text = f"🚀 Mobil bot + KINO MODULI ishga tushdi!\n\n👋 Assalomu alaykum {first_name}!\n\n✅ <b>Bot 24/7 ishlayapti</b>\n📱 Mobil deployment\n🎬 Kino kodini yuboring!\n\nMisal: 001, 002, 003"
                    result = send_message(chat_id, reply_text)
                    if result and result.get("ok"):
                        log_message(f"✅ Javob yuborildi: {first_name}")
                        processed_count += 1
                
                elif "/movies" in text:
                    movies_list = "🎬 <b>BARCHA KINOLAR:</b>\n\n"
                    for movie in movies:
                        movies_list += f"• {movie.get('name')} - Kod: <b>{movie.get('code')}</b>\n"
                    result = send_message(chat_id, movies_list)
                    if result and result.get("ok"):
                        log_message(f"✅ Kino ro'yxati yuborildi: {first_name}")
                        processed_count += 1
                
                else:
                    reply_text = f"👋 Assalomu alaykum {first_name}!\n\n✅ <b>Bot javob berishga tayyor!</b>\n\n📽️ Kino kodi yuboring yoki /movies buyrug'i bilan barcha kinolarni ko'ring\n\nKo'proq qo'llab-quvvatlash: @Kvantexno"
                    result = send_message(chat_id, reply_text)
                    if result and result.get("ok"):
                        log_message(f"✅ Javob yuborildi: {first_name}")
                        processed_count += 1
                
                offset = update_id + 1
                
            time.sleep(1)
            
        except KeyboardInterrupt:
            log_message("🛑 Bot to'xtatildi")
            break
        except Exception as e:
            log_message(f"❌ Xato: {e}")
            time.sleep(10)
    
    log_message(f"✅ Jami qayta ishlandi: {processed_count} ta xabar")

if __name__ == "__main__":
    log_message("=" * 50)
    log_message("🎬 MOBIL TELEGRAM BOT + KINO MODULI")
    log_message("=" * 50)
    process_updates()
