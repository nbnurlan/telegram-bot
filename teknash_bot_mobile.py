#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional Kino Bot Tizimi - Google Drive Edition
@Kinoselected uchun - Foydalanuvchilarga Drive link yuboradi
"""

import requests
import time
import os
import json
import re
from datetime import datetime

# ============= SOZLAMALAR =============
BOT_TOKEN = "8453590241:AAE2XXL5_7FoTg6IMoZCx7KmJgM-cwGc6E0"
ADMIN_ID = 7021010653
CHANNEL_USERNAME = "@Kinoselected"
CHANNEL_ID = "@Kinoselected"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
DB_FILE = 'kino_database.json'

# ============= MA'LUMOTLAR BAZASI =============
def load_db():
    """Bazani yuklash"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"movies": {}, "stats": {"total_views": 0}, "last_code": 0}
    return {"movies": {}, "stats": {"total_views": 0}, "last_code": 0}

def save_db(db):
    """Bazani saqlash"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"❌ Baza saqlashda xato: {e}")

def get_next_code(db):
    """Keyingi kodni olish"""
    db['last_code'] += 1
    return str(db['last_code']).zfill(4)

# ============= LOG =============
def log(message):
    """Log xabarlar"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

# ============= TELEGRAM FUNKSIYALAR =============
def send_message(chat_id, text, parse_mode="HTML", reply_markup=None):
    """Xabar yuborish"""
    try:
        url = f"{BASE_URL}/sendMessage"
        data = {
            "chat_id": chat_id, 
            "text": text, 
            "parse_mode": parse_mode
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        response = requests.post(url, data=data)
        return response.json()
    except Exception as e:
        log(f"❌ Xabar yuborishda xato: {e}")
        return None

def delete_message(chat_id, message_id):
    """Xabarni o'chirish"""
    try:
        url = f"{BASE_URL}/deleteMessage"
        data = {"chat_id": chat_id, "message_id": message_id}
        requests.post(url, data=data)
    except:
        pass

# ============= GOOGLE DRIVE =============
def extract_drive_id(url):
    """Google Drive link dan FILE_ID olish"""
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
        r'/open\?id=([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def create_drive_download_link(file_id):
    """To'g'ridan-to'g'ri yuklab olish havolasi yaratish"""
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def create_drive_view_link(file_id):
    """Ko'rish havolasi yaratish"""
    return f"https://drive.google.com/file/d/{file_id}/view"

# ============= ADMIN FUNKSIYALAR =============
def admin_add_movie_instructions(chat_id):
    """Kino qo'shish ko'rsatmasi"""
    text = """
📝 <b>YANGI KINO QO'SHISH</b>

<b>Qadamma-qadam:</b>

1️⃣ Kinoni Google Drive ga yuklang
2️⃣ Fayl → O'ng tugma → Ulashish
3️⃣ "Havola olgan har kim ko'ra oladi" tanlang
4️⃣ Havolani nusxa oling
5️⃣ Havolani bu yerga yuboring

<b>Yoki quyidagi formatda:</b>
<code>Kino nomi | Google Drive link</code>

<b>Misol:</b>
<code>Titanik (1997) | https://drive.google.com/file/d/1a2b3c4d5e/view</code>

Yoki faqat link yuboring, kod avtomatik beriladi.
"""
    send_message(chat_id, text)

def process_admin_movie_add(chat_id, text, db):
    """Admin tomonidan qo'shilgan kino"""
    # Format 1: "Nom | Link"
    if '|' in text:
        parts = text.split('|', 1)
        movie_name = parts[0].strip()
        drive_link = parts[1].strip()
    # Format 2: Faqat link
    elif 'drive.google.com' in text:
        drive_link = text.strip()
        movie_name = None
    else:
        send_message(chat_id, "❌ Google Drive havolasini topa olmadim!")
        return
    
    # Drive ID ni olish
    file_id = extract_drive_id(drive_link)
    if not file_id:
        send_message(chat_id, "❌ Google Drive link noto'g'ri formatda!")
        return
    
    # Kod berish
    code = get_next_code(db)
    
    # Bazaga saqlash
    db['movies'][code] = {
        'name': movie_name if movie_name else f"Kino {code}",
        'drive_file_id': file_id,
        'drive_link': drive_link,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'views': 0
    }
    save_db(db)
    
    # Kanalga post qilish
    download_link = create_drive_download_link(file_id)
    view_link = create_drive_view_link(file_id)
    
    caption = f"""
🎬 <b>Kino kodi: {code}</b>
{f"📽️ {movie_name}" if movie_name else ""}

📥 Yuklab olish:
{download_link}

📺 @Kinoselected
"""
    
    # Inline tugmalar
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📥 Yuklab olish", "url": download_link},
                {"text": "▶️ Ko'rish", "url": view_link}
            ]
        ]
    }
    
    # Kanalga yuborish
    result = send_message(CHANNEL_ID, caption, reply_markup=keyboard)
    
    if result and result.get("ok"):
        send_message(chat_id, f"✅ Kino qo'shildi va kanalga yuborildi!\n\n🔢 Kod: <b>{code}</b>\n🎬 {movie_name if movie_name else 'Kino'}")
        log(f"✅ Yangi kino: Kod {code} - {movie_name if movie_name else 'Nomsiz'}")
    else:
        send_message(chat_id, f"⚠️ Kino bazaga qo'shildi (Kod: {code}) lekin kanalga yuborishda xato!\n\nKanal sozlamalarini tekshiring.")

def admin_stats(chat_id, db):
    """Statistika"""
    total_movies = len(db['movies'])
    total_views = sum(movie.get('views', 0) for movie in db['movies'].values())
    
    # Top 5 kinolar
    top_movies = sorted(db['movies'].items(), key=lambda x: x[1].get('views', 0), reverse=True)[:5]
    top_list = "\n".join([f"🔢 {code} - {movie.get('name', 'Nomsiz')}: {movie['views']} ko'rishlar" for code, movie in top_movies])
    
    stats_text = f"""
📊 <b>STATISTIKA</b>

🎬 Jami kinolar: <b>{total_movies}</b>
👁 Jami ko'rishlar: <b>{total_views}</b>
📈 O'rtacha: <b>{total_views // total_movies if total_movies > 0 else 0}</b> ko'rish/kino

🏆 <b>TOP 5 KINOLAR:</b>
{top_list if top_list else "Ma'lumot yo'q"}

📅 Oxirgi yangilanish: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    send_message(chat_id, stats_text)

def admin_list(chat_id, db):
    """Oxirgi kinolar ro'yxati"""
    if not db['movies']:
        send_message(chat_id, "📭 Hozircha kinolar yo'q.")
        return
    
    movies_list = sorted(db['movies'].items(), key=lambda x: x[1]['added_date'], reverse=True)[:20]
    
    text = "<b>📋 OXIRGI 20 TA KINO:</b>\n\n"
    for code, movie in movies_list:
        views = movie.get('views', 0)
        name = movie.get('name', 'Nomsiz')
        text += f"🔢 <code>{code}</code> - {name} (👁 {views})\n"
    
    send_message(chat_id, text)

def admin_delete(chat_id, code, db):
    """Kinoni o'chirish"""
    if code in db['movies']:
        movie_name = db['movies'][code].get('name', 'Nomsiz')
        del db['movies'][code]
        save_db(db)
        send_message(chat_id, f"✅ <b>{movie_name}</b> (Kod: {code}) o'chirildi!")
        log(f"🗑️ O'chirildi: Kod {code}")
    else:
        send_message(chat_id, f"❌ Kod <b>{code}</b> topilmadi!")

# ============= FOYDALANUVCHI FUNKSIYALARI =============
def user_get_movie(chat_id, code, db, message_id=None):
    """Foydalanuvchi kino so'radi"""
    if code in db['movies']:
        movie = db['movies'][code]
        
        # Ko'rishlar sonini oshirish
        movie['views'] = movie.get('views', 0) + 1
        save_db(db)
        
        # Google Drive linklar yaratish
        file_id = movie['drive_file_id']
        download_link = create_drive_download_link(file_id)
        view_link = create_drive_view_link(file_id)
        movie_name = movie.get('name', f'Kino {code}')
        
        # Foydalanuvchiga yuborish
        message_text = f"""
🎬 <b>{movie_name}</b>

🔢 Kod: <b>{code}</b>
👁 Ko'rishlar: <b>{movie['views']}</b>

📥 <b>Yuklab olish:</b>
{download_link}

💡 <b>Ko'rsatma:</b>
1. "Yuklab olish" tugmasini bosing
2. Google Drive ochiladi
3. Yuklab olish tugmasini bosing

📺 @Kinoselected
"""
        
        # Inline tugmalar
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "📥 Yuklab olish", "url": download_link},
                    {"text": "▶️ Ko'rish", "url": view_link}
                ],
                [
                    {"text": "📺 Kanal", "url": f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"}
                ]
            ]
        }
        
        send_message(chat_id, message_text, reply_markup=keyboard)
        log(f"✅ Havola yuborildi: User {chat_id} - Kod {code}")
        
        # Foydalanuvchi xabarini o'chirish
        if message_id:
            time.sleep(0.5)
            delete_message(chat_id, message_id)
    else:
        # Kod topilmasa
        msg = send_message(chat_id, "❌ Kod noto'g'ri!\n\n📋 Kino kodlarini @Kinoselected kanalida topasiz.")
        
        # 5 sekunddan keyin o'chirish
        if msg and message_id:
            time.sleep(5)
            delete_message(chat_id, message_id)
            if msg.get('result'):
                delete_message(chat_id, msg['result']['message_id'])

# ============= ASOSIY FUNKSIYA =============
def process_updates():
    """Xabarlarni qayta ishlash"""
    offset = 0
    db = load_db()
    user_states = {}
    
    log("=" * 60)
    log("🎬 PROFESSIONAL KINO BOT (GOOGLE DRIVE) ISHGA TUSHDI!")
    log(f"📺 Kanal: {CHANNEL_USERNAME}")
    log(f"🎥 Jami kinolar: {len(db['movies'])}")
    log("=" * 60)
    
    while True:
        try:
            url = f"{BASE_URL}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url, timeout=35)
            data = response.json()
            
            if not data.get("ok"):
                continue
            
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
                message_id = message.get("message_id")
                first_name = message.get("from", {}).get("first_name", "Foydalanuvchi")
                
                # START
                if text == "/start":
                    welcome = f"""
🎬 <b>Assalomu alaykum, {first_name}!</b>

📺 @Kinoselected botiga xush kelibsiz!

<b>📌 Qanday foydalanish:</b>
• Kino kodini yuboring (masalan: 0001)
• Kino kodlarini kanalda topasiz
• Sizga Google Drive havola beriladi
• Yuklab oling va tomosha qiling!

🎥 Hozir <b>{len(db['movies'])}</b> ta kino mavjud!

📺 Kanal: @Kinoselected
💬 Savol va takliflar: @Kvantexno
"""
                    send_message(chat_id, welcome)
                    log(f"👋 Start: {first_name}")
                
                # ADMIN PANEL
                elif text == "/admin" and user_id == ADMIN_ID:
                    admin_text = f"""
👑 <b>ADMIN PANEL</b>

📊 <b>Statistika:</b>
• Jami kinolar: {len(db['movies'])}
• Oxirgi kod: {db['last_code']}

🛠 <b>Buyruqlar:</b>
• /add - Kino qo'shish ko'rsatmasi
• Google Drive link yuboring → Avtomatik qo'shiladi
• /stats - Batafsil statistika
• /list - Barcha kinolar ro'yxati
• /delete [kod] - Kinoni o'chirish

💡 <b>Tez qo'shish:</b> Faqat Google Drive linkini yuboring!
"""
                    send_message(chat_id, admin_text)
                
                # ADMIN: ADD
                elif text == "/add" and user_id == ADMIN_ID:
                    admin_add_movie_instructions(chat_id)
                    user_states[user_id] = "waiting_for_drive_link"
                
                # ADMIN: STATS
                elif text == "/stats" and user_id == ADMIN_ID:
                    admin_stats(chat_id, db)
                
                # ADMIN: LIST
                elif text == "/list" and user_id == ADMIN_ID:
                    admin_list(chat_id, db)
                
                # ADMIN: DELETE
                elif text.startswith("/delete") and user_id == ADMIN_ID:
                    parts = text.split()
                    if len(parts) == 2:
                        admin_delete(chat_id, parts[1], db)
                    else:
                        send_message(chat_id, "❌ Format: /delete 0001")
                
                # ADMIN: Google Drive link yubordi
                elif user_id == ADMIN_ID and 'drive.google.com' in text:
                    process_admin_movie_add(chat_id, text, db)
                    user_states[user_id] = None
                
                # FOYDALANUVCHI: KINO KODI
                else:
                    code = text
                    user_get_movie(chat_id, code, db, message_id)
                
                offset = update_id + 1
            
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            log("🛑 Bot to'xtatildi")
            break
        except Exception as e:
            log(f"❌ Xato: {e}")
            time.sleep(10)

# ============= ISHGA TUSHIRISH =============
if __name__ == "__main__":
    process_updates()
