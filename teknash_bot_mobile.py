#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Kino Bot - GitHub/Heroku/Render uchun
Faqat video yuborish + Admin panel
"""

import requests
import time
import os
import json
from datetime import datetime

# Bot sozlamalari
BOT_TOKEN = "8453590241:AAE2XXL5_7FoTg6IMoZCx7KmJgM-cwGc6E0"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
ADMIN_ID = 123456789  # O'Z TELEGRAM ID INGIZNI YOZING!

# Ma'lumotlar bazasi fayli
DB_FILE = 'movies_db.json'

def load_db():
    """Ma'lumotlar bazasini yuklash"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_message(f"❌ Bazani yuklashda xato: {e}")
            return {}
    else:
        # Boshlang'ich ma'lumotlar
        initial_db = {
            "101": {
                "file_id": "BAACAgIAAxkBAAIBYmZkj..."  # Video file_id
            },
            "102": {
                "file_id": "BAACAgIAAxkBAAIBYmZkj..."
            }
        }
        save_db(initial_db)
        return initial_db

def save_db(db):
    """Ma'lumotlar bazasini saqlash"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        log_message("✅ Baza saqlandi")
    except Exception as e:
        log_message(f"❌ Bazani saqlashda xato: {e}")

def log_message(message):
    """Log xabarlar"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def send_message(chat_id, text, reply_markup=None):
    """Xabar yuborish"""
    try:
        url = f"{BASE_URL}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
            
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        log_message(f"❌ Xabar yuborishda xato: {e}")
        return None

def send_video(chat_id, file_id):
    """Video yuborish (caption siz)"""
    try:
        url = f"{BASE_URL}/sendVideo"
        data = {
            "chat_id": chat_id,
            "video": file_id
        }
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        log_message(f"❌ Video yuborishda xato: {e}")
        return None

def is_admin(user_id):
    """Admin ekanligini tekshirish"""
    return user_id == ADMIN_ID

def handle_start(chat_id, first_name):
    """Start komandasi"""
    text = f"""
🎬 Assalomu alaykum, {first_name}!

Kino botiga xush kelibsiz!

📌 Qanday foydalanish:
• Kino kodini yuboring (masalan: 101)

Kod yuboring va kinoni tomosha qiling! 🍿
"""
    send_message(chat_id, text)

def handle_list(chat_id, movies_db):
    """Kinolar ro'yxati"""
    if not movies_db:
        send_message(chat_id, "📭 Hozircha kinolar yo'q.")
        return
    
    movie_list = "🎬 <b>Mavjud kinolar:</b>\n\n"
    for code in sorted(movies_db.keys()):
        movie_list += f"🔢 <code>{code}</code>\n"
    
    movie_list += "\n💡 Kinoni ko'rish uchun kodini yuboring!"
    send_message(chat_id, movie_list)

def handle_add_movie(chat_id, user_id):
    """Kino qo'shish (Admin)"""
    if not is_admin(user_id):
        send_message(chat_id, "❌ Bu buyruq faqat admin uchun!")
        return
    
    text = """
📝 <b>Yangi kino qo'shish:</b>

Kino kodini yuboring (masalan: 103)
"""
    send_message(chat_id, text)
    return "waiting_for_code"

def handle_admin_panel(chat_id, user_id, movies_db):
    """Admin panel"""
    if not is_admin(user_id):
        send_message(chat_id, "❌ Bu buyruq faqat admin uchun!")
        return
    
    stats = f"""
👑 <b>Admin Panel</b>

📊 <b>Statistika:</b>
• Jami kinolar: {len(movies_db)}

🛠 <b>Buyruqlar:</b>
• /add - Yangi kino qo'shish
• /delete [kod] - Kinoni o'chirish
• /list - Barcha kinolar
• /admin - Bu panel
"""
    send_message(chat_id, stats)

def process_updates():
    """Xabarlarni qayta ishlash"""
    offset = 0
    movies_db = load_db()
    user_states = {}  # Foydalanuvchi holatlari
    temp_movie_data = {}  # Vaqtinchalik kino ma'lumotlari
    
    log_message("🤖 Kino bot ishga tushdi!")
    log_message(f"📽️ Jami kino: {len(movies_db)} ta")
    
    while True:
        try:
            url = f"{BASE_URL}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url)
            data = response.json()
            
            if not data.get("ok"):
                break
                
            updates = data.get("result", [])
            
            for update in updates:
                update_id = update.get("update_id")
                message = update.get("message", {})
                
                if not message:
                    offset = update_id + 1
                    continue
                
                chat_id = message.get("chat", {}).get("id")
                user_id = message.get("from", {}).get("id")
                text = message.get("text", "").strip()
                first_name = message.get("from", {}).get("first_name", "Foydalanuvchi")
                video = message.get("video")
                
                # Admin video yuborsa (kino qo'shish)
                if video and is_admin(user_id) and user_states.get(user_id) == "waiting_for_video":
                    file_id = video.get("file_id")
                    code = temp_movie_data.get(user_id)
                    
                    if code:
                        movies_db[code] = {
                            'file_id': file_id
                        }
                        save_db(movies_db)
                        
                        send_message(chat_id, f"✅ Kino qo'shildi!\n\n🔢 Kod: {code}")
                        
                        user_states[user_id] = None
                        temp_movie_data[user_id] = None
                        log_message(f"✅ Yangi kino: Kod {code}")
                
                # Admin kino kodini yuborsa
                elif text and is_admin(user_id) and user_states.get(user_id) == "waiting_for_code":
                    code = text.strip()
                    
                    if code:
                        temp_movie_data[user_id] = code
                        user_states[user_id] = "waiting_for_video"
                        
                        send_message(chat_id, f"✅ Kod saqlandi: {code}\n\nEndi video faylni yuboring.")
                    else:
                        send_message(chat_id, "❌ Kod kiriting!")
                
                # Komandalar
                elif text == "/start":
                    handle_start(chat_id, first_name)
                    log_message(f"👋 Start: {first_name}")
                
                elif text == "/list":
                    handle_list(chat_id, movies_db)
                    log_message(f"📋 List: {first_name}")
                
                elif text == "/add":
                    state = handle_add_movie(chat_id, user_id)
                    if state:
                        user_states[user_id] = state
                    log_message(f"➕ Add: {first_name}")
                
                elif text == "/admin":
                    handle_admin_panel(chat_id, user_id, movies_db)
                    log_message(f"👑 Admin: {first_name}")
                
                elif text.startswith("/delete"):
                    if is_admin(user_id):
                        parts = text.split()
                        if len(parts) == 2:
                            code = parts[1]
                            if code in movies_db:
                                del movies_db[code]
                                save_db(movies_db)
                                send_message(chat_id, f"✅ Kod {code} o'chirildi!")
                                log_message(f"🗑️ O'chirildi: Kod {code}")
                            else:
                                send_message(chat_id, f"❌ '{code}' kodi topilmadi.")
                        else:
                            send_message(chat_id, "❌ Kod kiriting.\n\nMasalan: /delete 101")
                    else:
                        send_message(chat_id, "❌ Bu buyruq faqat admin uchun!")
                
                # Kino kodi
                else:
                    code = text
                    if code in movies_db:
                        movie = movies_db[code]
                        result = send_video(chat_id, movie['file_id'])
                        
                        if result and result.get("ok"):
                            log_message(f"✅ Video yuborildi: {first_name} - Kod {code}")
                        else:
                            send_message(chat_id, "❌ Xatolik yuz berdi!")
                    else:
                        send_message(chat_id, "❌ Kod noto'g'ri!")
                        log_message(f"❌ Noto'g'ri kod: {first_name} - {code}")
                
                offset = update_id + 1
                
            time.sleep(1)
            
        except KeyboardInterrupt:
            log_message("🛑 Bot to'xtatildi")
            break
        except Exception as e:
            log_message(f"❌ Xato: {e}")
            time.sleep(10)

if __name__ == "__main__":
    log_message("=" * 50)
    log_message("🎬 TELEGRAM KINO BOT")
    log_message("=" * 50)
    process_updates()
