import telebot
from telebot.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
import re
import feedparser
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import io
from PIL import Image, ImageDraw, ImageFont
from deep_translator import GoogleTranslator
import textwrap
import time
import random
import requests
import os
from flask import Flask, request
import threading
import urllib.parse
import pymongo
import os
import requests
import requests
# ये imports अपनी bot.py में सबसे ऊपर जोड़ दो
import random
import time
import io
from PIL import Image
from io import BytesIO
# Baki purane imports rehne do (telebot, os, etc.)
# ... आपके सभी पुराने imports ...
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp

# --- असिस्टेंट क्लाइंट (Pyrogram) ---
ASSISTANT = Client(
    name="RAJPUROHIT",
    api_id=int(os.environ.get("API_ID")),
    api_hash=os.environ.get("API_HASH"),
    session_string=os.environ.get("SESSION_STRING")
)

# --- PyTgCalls क्लाइंट (वॉइस चैट के लिए) ---
CALLS = PyTgCalls(ASSISTANT)

# --- बॉट शुरू होते ही इसे चालू करें ---
print("⚡ असिस्टेंट और कॉल्स शुरू हो रहे हैं...")
ASSISTANT.start()
CALLS.start()
print("✅ असिस्टेंट और कॉल्स तैयार हैं!")

HF_API_URL = "https://singhp08-rvc-models.hf.space/convert" # Teri Space ka API Link
HF_TTS_API = "https://singhp08-rvc-models.hf.space/tts"
RVC_API = "https://rvc-api.onrender.com/convert"


# 🔐 SECURE KEYS (Ab sab Render ki tijori / Environment Variables se aayega)
API_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_KEY')
MONGO_URL = os.environ.get('MONGO_URL')
# 🚀 HUGGING FACE PRIVATE API ENGINE LINK
HF_API = "https://singhp08-daimond-batch.hf.space"

# Admin & Group Info
ADMIN_ID = 7574760011 
GROUP_USERNAME = "@Daimondbatch" 

# Database Connection
try:
    client = pymongo.MongoClient(MONGO_URL)
    db = client["jodhpur_king_db"]
    users_db = db["users"]
    print("✅ Database Connected Successfully!")
except Exception as e:
    print(f"❌ Database Error: {e}")

def get_dhruva_voice(text):
    try:
        payload = {'text': text, 'voice': 'hi-IN-MadhurNeural'} 
        response = requests.get(f"{HF_API}/tts", params=payload, timeout=60)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        return None
        
# Bot Initialization
bot = telebot.TeleBot(API_TOKEN)

API_TOKEN = os.environ.get('TELEGRAM_TOKEN')
# Groq hata kar wapas Gemini ki chaabi lagao
GEMINI_API_KEY = os.environ.get('GEMINI_KEY')
ADMIN_ID = 7574760011 
GROUP_USERNAME = "@Daimondbatch" 

bot.set_my_commands([
    BotCommand("start", "Bot chalu karein"),
    BotCommand("bal", "Apna khaata aur level dekhein"),
    BotCommand("hd", "✨ Purani photo ko 4K HD banayein"),
    BotCommand("shop", "apne aap ko upgrade kare"),
    BotCommand("toprank", "Top 10 ameer log"),
    BotCommand("topkills", "Top 10 Serial Killers"),
    BotCommand("daily", "Har 24 ghante ka inam"),
    BotCommand("weekly", "Har 7 din mein 2000 Rs"),
    BotCommand("imagine", "Apni pasand ka photo mangaye"),
    BotCommand("dice", "🎲 Ludo game khelein"),
    BotCommand("spin", "🎰 Casino Slot Machine"),
    BotCommand("dart", "🎯 Kismat azmayein (/dart amount)"),
    BotCommand("shield", "🛡️ 500 Rs mein 24h protection"),
    BotCommand("give", "Kisi ko paise donate karein"),
    BotCommand("loan", "Loan offer karein"),
    BotCommand("return", "Udhar wapas karein"),
    BotCommand("rob", "Dusre ke paise churayein"),
    BotCommand("kill", "Shikaar karein (500 Rs inam)"),
    # 🔥 NAYE AI AUR VIP FEATURES
    BotCommand("roast", "🔥 Kisi ko AI Rap se roast karein"),
    BotCommand("ask", "🗣️ AI Jarvis se voice me jawab paayein"),
    BotCommand("reel", "🎬 AI se cinematic Reel/Shorts banayein"),
    BotCommand("video", "🎬 AI Motivational Video banayein"),
    BotCommand("dl", "📥 Insta/YT ka video download karein"),
    BotCommand("photo", "📸 Photo ka background transparent banayein"),
    BotCommand("read", "👁️ Kitab/Notes padh kar Hindi me translate karein"),
    BotCommand("sketch", "🎨 Photo ka Pencil Sketch banayein"),
    BotCommand("speak", "🎙️ Bot ki aawaz me apni baat bulwayein"),
    BotCommand("paper", "📜 Kagaz par VIP font me likhwayein"),
    
    # 🎲 NAYE GAMES
    BotCommand("sps", "🪨📄✂️ Stone Paper Scissor khelein"),
    BotCommand("dance", "🕺 Balle Balle! Party Time"),
    BotCommand("guess", "🔢 1-100 ke beech number guess karo"),
    BotCommand("type", "⌨️ Typing race khelo"),
    BotCommand("math", "➕ Math quiz solve karo"),
    BotCommand("setrole", "🎭 Bot ka personality custom set karo"),
    BotCommand("setroleoff", "🛑 Custom personality band karo"),
    BotCommand("stealth", "🥷 Stealth mode ON/OFF"),
    BotCommand("scanuser", "🔍 Kisi social media username ko scan karo"),
    BotCommand("nuke", "💣 Poora database reset (Admin only)"),
    BotCommand("setdance", "💃 Dance GIF change karo (Admin only)"),
    
    # 👑 NAYE ADMIN COMMANDS (Sirf Boss ke liye)
    BotCommand("list", "👑 DM me sabki list dekhein"),
    BotCommand("blocklist", "👑 DM me sabhi block user ki list dekhein"),
    BotCommand("tell", "👑 DM se sabko message bhejein"),
    BotCommand("block", "👑 Kisi ko bot se block karein"),
    BotCommand("gift", "👑 Kisi ko free mein paise dein"),
    BotCommand("addkill", "👑 Kisi ke kills badhayein"),
    BotCommand("deactivate", "👑 Kisi command ko band karein"),
    BotCommand("revive", "Zinda karein (700 Rs lagenge)"),
    BotCommand("xo", "Tic-Tac-Toe khelein"),
    BotCommand("ban", "👑 Group se nikalein"),
    BotCommand("mute", "👑 Chup karayein"),
    BotCommand("say", "👑 Apna message sab ko bhejo"),
    BotCommand("all", "👑 Group me sabko tag karein"),
    BotCommand("detail", "👑 DM me user ki kundali dekhein"),
    BotCommand("askpoll", "👑 Daily poll bhejein")
])

users = {}
active_groups = set()
pending_loans = {}
xo_games = {}
sps_games = {}
poll_voters = set()
pending_says = {}
pending_papers = {}
# Isse bot.py ke upar define karein
game_sessions = {}
# ... आपकी बाकी की फाइल में, जहाँ MongoDB सेटअप है ...
groups_db = db["music_groups"] # यह नया कलेक्शन है

def get_group_settings(chat_id):
    settings = groups_db.find_one({"_id": chat_id})
    if not settings:
        settings = {
            "_id": chat_id,
            "queue": [],
            "playlist": [],
            "vip_users": [],
            "current_track": None,
            "added_by": None,
            "loop": False
        }
        groups_db.insert_one(settings)
    return settings


# 🎨 9 VIP INK COLORS
INK_COLORS = {
    "blue": {"rgb": (0, 0, 180), "name": "🔵 Blue"},
    "black": {"rgb": (20, 20, 20), "name": "⚫ Black"},
    "red": {"rgb": (180, 0, 0), "name": "🔴 Red"},
    "green": {"rgb": (0, 100, 0), "name": "🟢 Green"},
    "purple": {"rgb": (128, 0, 128), "name": "🟣 Purple"},
    "orange": {"rgb": (255, 140, 0), "name": "🟠 Orange"},
    "pink": {"rgb": (255, 20, 147), "name": "🌸 Pink"},
    "brown": {"rgb": (139, 69, 19), "name": "🟤 Brown"},
    "cyan": {"rgb": (0, 139, 139), "name": "🩵 Cyan"}
}
COLOR_KEYS = list(INK_COLORS.keys())
disabled_cmds = set() # 👈 Naya switch board
current_dance_gif = "https://media.tenor.com/3Z_yJbB4g8AAAAAC/dance-party.gif" # Default GIF

@bot.message_handler(commands=['help'])
def supreme_help_cmd(message):
    # Lock Check
    if "help" in disabled_cmds and message.from_user.id != ADMIN_ID: 
        return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
        
    wait_msg = bot.reply_to(message, "⏳ *Daimond Batch ka Maha-Granth khol raha hu...*", parse_mode="Markdown")
    bot.send_chat_action(message.chat.id, 'typing')

    # ==========================================
    # 📜 PART 1: ECONOMY, CRIME & CASINO
    # ==========================================
    help_text_1 = """
👑 **DAIMOND BATCH – THE SUPREME GUIDE (PART 1)** 👑

🏦 **💰 BANK AUR ECONOMY 💰**
• `/bal` – 🏧 Apna bank balance, rank, kills, inventory aur shield status dekho.
• `/daily` – 🎁 Har 24h free 200 Rs (Don Taj pehno to 400 Rs).
• `/weekly` – 🗓️ Har 7 din 2000 Rs (Don Taj = 4000 Rs).
• `/give [amount]` – 🤝 Reply karke paise donate karo.
• `/loan [amount]` – 💳 Dost ko udhar do, 24h mein na laute to auto fine + recovery.
• `/return` – ✅ Udhar chukta karo.
• `/shield` – 🛡️ 500 Rs dekar 24h protection lo.

🔪 **🩸 UNDERWORLD AUR MAFIA 🩸**
• `/shop` ya `/bazaar` – 🛒 Hathiyar khareedo:
  🔪 Chakku (1500) – Rob bonus +200 Rs
  🔫 Desi Katta (8000) – Kill reward 500→1500 Rs
  🦺 Bulletproof Jacket (15000) – 1 baar maut se bachao
  🐕 Khufiya Kutta (30000) – 30% chance rob fail + chor ko kaat
  💣 AK-47 (100000) – Kill reward 5000 Rs
  👑 Don Taj (500000) – Daily/Weekly inam DOUBLE
• `/rob [amount]` – 🥷 Reply karke kisi ko looto (5% tax).
• `/kill` – ☠️ Dushman ko khatam karo (reward weapon par depend).
• `/revive` – 💖 700 Rs dekar kisi dead user ko zinda karo.
• `/toprank` – 🏆 Top 10 ameer log dekho.
• `/topkills` – 💀 Top 10 serial killers ki list.

🎰 **🎲 CASINO AUR GAMES 🎲**
• `/dice [amount]` – 🎲 Ludo dice: 6 aaya to 3x paisa, warna loss.
• `/spin [amount]` – 🎰 Slot machine: 777 = 10x, teen match = 3x.
• `/dart [amount]` – 🎯 Dart: score 4/5/6 to 2x paisa.
• `/xo [amount]` – ❌⭕ Tic‑Tac‑Toe bet khelo.
• `/sps [amount]` – 🪨📄✂️ Stone Paper Scissor multiplayer.
"""

    # ==========================================
    # 🤖 PART 2: AI & GOD‑LEVEL TOOLS
    # ==========================================
    help_text_2 = """
🤖 **🚀 AI AUR GOD‑LEVEL TOOLS 🚀**

• `/ask [question]` – 🗣️ Jarvis AI se voice mein jawab pao.
• `/roast` – 🔥 Reply karke kisi ko AI rap se diss karo.
• `/reel [topic]` ya `/video` – 🎬 AI cinematic reel (FLUX image + Hindi voice).
• `/photo` – 📸 Reply karke background remove karo (transparent PNG).
• `/imagine [prompt]` – 🎨 FLUX.1 AI se HD image banwao.
• `/dl [link]` ya `/insta` `/yt` – 📥 Instagram/YouTube video download.
• `/read` ya `/ocr` – 👁️ Photo se text padhkar Hindi mein translate.
• `/sketch` – ✏️ Photo ko pencil sketch mein badlo.
• `/speak [text]` ya `/bolo` – 🎙️ Bot ki aawaz mein sunao.
• `/paper [font] [text]` – 📜 Notebook par custom font se likhwai.
• `/dance` – 💃 Balle‑Balle party GIF.
"""

    # ==========================================
    # 🎮 PART 3: NEW GAMES & CUSTOMIZATION
    # ==========================================
    help_text_3 = """
🎮 **🕹️ NEW GAMES & CUSTOMIZATION 🕹️**

• `/guess` – 🔢 1‑100 number guess, winner gets 500 Rs + 100 XP.
• `/type` – ⌨️ Typing race: sentence type karo, 300 Rs prize.
• `/math` – ➕ Math quiz: addition solve karo, 200 Rs inam.
• `/setrole <role>` – 🎭 Bot ka personality set karo (philosopher, girlfriend, etc).
• `/setroleoff` – 🛑 Custom personality band karo.
• `/stealth` – 🥷 Stealth mode ON/OFF – koi track nahi karega.
• `/scanuser <username>` – 🔍 300+ social networks par username dhundho.
• `/nuke` – 💣 (Admin only) Database reset – sabko 1000 Rs.
• `/setdance` – 🕺 (Admin only) `/dance` ka GIF badlo.

💡 *Aur bhi hai: `/shop` se hathiyar khareedo, `/daily` se kamao!*
"""

    try:
        bot.send_message(message.chat.id, help_text_1, parse_mode="Markdown")
        time.sleep(1)
        bot.send_message(message.chat.id, help_text_2, parse_mode="Markdown")
        time.sleep(1)
        bot.send_message(message.chat.id, help_text_3, parse_mode="Markdown")
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Panna phat gaya sa! Error: {e}", message.chat.id, wait_msg.message_id)


def generate_voice(text):
    try:
        print("📥 Text:", text)

        # 1️⃣ TTS (HF)
        tts_res = requests.post(HF_TTS_API, json={"text": text}, timeout=60)

        if tts_res.status_code != 200:
            print("❌ TTS Error:", tts_res.text)
            return None

        # 2️⃣ RVC
        files = {"audio": ("tts.mp3", tts_res.content)}
        data = {"model": "elvish"}

        rvc_res = requests.post(RVC_API, files=files, data=data, timeout=120)

        print("RVC Status:", rvc_res.status_code)

        if rvc_res.status_code == 200:
            return rvc_res.content
        else:
            print("❌ RVC Error:", rvc_res.text)
            return None

    except Exception as e:
        print("❌ Exception:", e)
        return None

# ==========================================
# 👑 SUPREME ADMIN CONTROL PANEL (DM ONLY)
# ==========================================

# 1. 🛑 Global Block Filter (Isko sabse upar rakhna zaroori hai)
# Agar user blocked hai, toh ye filter uske message ko aage commands tak jane hi nahi dega
@bot.message_handler(func=lambda message: users.get(message.from_user.id, {}).get('blocked', False))
def blocked_user_handler(message):
    bot.reply_to(message, "🚫 **ACCESS DENIED**\nBoss (Admin) ne aapko is bot se block kar diya hai sa!")

# 2. 📋 List Command (Sabki Kundali - Multi-Message Support)
@bot.message_handler(commands=['list'])
def admin_list_users(message):
    # 1. Admin aur DM Check
    if message.from_user.id != ADMIN_ID: 
        return
    if message.chat.type != 'private': 
        return bot.reply_to(message, "🤫 Boss, yeh command sirf mere DM (Private Chat) mein aakar lagao!")
    
    header = "📋 *DAIMOND BATCH USERS* 📋\n━━━━━━━━━━━━━━━━━━━\n"
    text = header
    
    for i, (uid, data) in enumerate(users.items(), 1):
        status = "🚫 BLOCKED" if data.get('blocked', False) else "✅ Active"
        
        # 2. MARKDOWN FIX: User ke naam se '_' aur '*' hata rahe hain taaki bot crash na ho
        raw_name = str(data.get('name', 'Unknown User'))
        safe_name = raw_name.replace("_", "\\_").replace("*", "\\*").replace("`", "").replace("[", "").replace("]", "")
        
        line = f"{i}. {safe_name} (ID: `{uid}`) - {status}\n"
        
        # Telegram limit check (4000 chars)
        if len(text) + len(line) > 4000:
            try:
                bot.send_message(message.chat.id, text, parse_mode="Markdown")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Error (List 1): {e}")
            text = line # Naya message yahan se shuru hoga
        else:
            text += line
            
    # Bacha hua aakhiri message bhejna
    if text and text != header:
        try:
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error (List 2): {e}\n(Shayad kisi naam mein abhi bhi kharab text hai)")
    elif text == header:
        bot.reply_to(message, "Boss, abhi tak database mein koi user nahi aaya hai!")

# 2.5 🚫 Blocklist Command (Sirf Block hue logo ki list)
@bot.message_handler(commands=['blocklist'])
def admin_blocklist_users(message):
    if message.from_user.id != ADMIN_ID or message.chat.type != 'private': return
    
    header = "🚫 **BLOCKED USERS LIST** 🚫\n━━━━━━━━━━━━━━━━━━━\n"
    text = header
    count = 1
    
    for uid, data in users.items():
        if data.get('blocked', False):
            line = f"{count}. {data['name']} (ID: `{uid}`)\n"
            
            if len(text) + len(line) > 4000:
                bot.send_message(message.chat.id, text, parse_mode="Markdown")
                text = line
            else:
                text += line
            count += 1
            
    if count == 1: # Matlab loop me koi blocked user nahi mila
        bot.reply_to(message, "✅ **All Clear!**\nBoss, abhi tak kisi ko block nahi kiya gaya hai!")
    else:
        if text:
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
            
# 3. 📢 Tell Command (Announcement ya DM)
@bot.message_handler(commands=['tell'])
def admin_tell_cmd(message):
    if message.from_user.id != ADMIN_ID or message.chat.type != 'private': return
    
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        return bot.reply_to(message, "📝 **Aise likho:**\n`/tell all Hello Jodhpur!`\n`/tell 123456789 Tera account check kar`", parse_mode="Markdown")
        
    target = parts[1].lower()
    msg_text = parts[2]
    
    if target == "all" or target == "@all":
        count = 0
        for uid in users.keys():
            try:
                bot.send_message(uid, f"📢 **Admin Announcement:**\n\n{msg_text}")
                count += 1
            except: pass # Agar kisi ne bot ko DM me block kiya ho toh error na aaye
        bot.reply_to(message, f"✅ Boss! Message {count} logo ko unke DM mein bhej diya gaya!")
    else:
        try:
            target_id = int(target.replace("@", ""))
            if target_id not in users: return bot.reply_to(message, "❌ Ye ID database mein nahi mili sa!")
            bot.send_message(target_id, f"💬 **Admin Secret Message:**\n\n{msg_text}")
            bot.reply_to(message, f"✅ Message '{users[target_id]['name']}' ko bhej diya!")
        except:
            bot.reply_to(message, "❌ User ka ID galat hai! `/list` dba kar sahi ID dekho.")

# 4. 🔨 Block / Unblock Command
@bot.message_handler(commands=['block', 'unblock'])
def admin_block_cmd(message):
    if message.from_user.id != ADMIN_ID or message.chat.type != 'private': return
    
    cmd = message.text.split()[0].lower()
    try:
        target_id = int(message.text.split()[1].replace("@", ""))
    except:
        return bot.reply_to(message, f"📝 **Aise likho:** `{cmd} 123456789`\n(ID `/list` command se dekhein)", parse_mode="Markdown")
        
    if target_id not in users: return bot.reply_to(message, "❌ Ye user database mein nahi hai sa!")
    
    if target_id == ADMIN_ID: 
        return bot.reply_to(message, "❌ Boss! Khud ko block nahi kar sakte!")
        
    elif cmd == '/block':  # <--- 'elif' lagaya aur 'if' ki seedh mein rakha
        users[target_id]['blocked'] = True
        bot.reply_to(message, f"🚫 **BANNED!**\nAb '{users[target_id]['name']}' bot ka koi bhi feature use nahi kar payega.")
    
    else:
        users[target_id]['blocked'] = False
        bot.reply_to(message, f"✅ **UNBANNED!**\n'{users[target_id]['name']}' ko wapas azaadi mil gayi sa!")
        
# 🛒 CHOR BAZAAR KA SAMAAN
SHOP_ITEMS = {
    "chakku": {"name": "🔪 Chakku", "price": 1500, "desc": "Rob karne par 200 Rs extra milenge."},
    "katta": {"name": "🔫 Desi Katta", "price": 8000, "desc": "Kill ka inaam 500 se 1500 Rs ho jayega."},
    "jacket": {"name": "🦺 Bulletproof Jacket", "price": 15000, "desc": "1 baar goli (Kill) se bachayegi (Phat jayegi)."},
    "kutta": {"name": "🐕 Khufiya Kutta", "price": 30000, "desc": "Rob hone par 30% chance hai kutta chor ko kaat lega."},
    "ak47": {"name": "💣 AK-47", "price": 100000, "desc": "Kill ka inaam seedha 5000 Rs!"},
    "don": {"name": "👑 Don Taj", "price": 500000, "desc": "VIP Status aur Daily/Weekly inam DOUBLE!"}
}

# Database se purana data nikalna
print("Loading data from database...")
try:
    for doc in users_db.find():
        if doc["_id"] == "bot_settings":
            disabled_cmds = set(doc.get("disabled_cmds", []))
            if "dance_gif" in doc: current_dance_gif = doc["dance_gif"]
        else:
            users[doc["_id"]] = doc["data"]
    print(f"Loaded {len(users)} users.")
except:
    print("Abhi naya database hai ya error aaya.")

# Data permanent save karne ka function
def save_data():
    for uid, data in list(users.items()):
        users_db.update_one({"_id": uid}, {"$set": {"data": data}}, upsert=True)
    # ⚙️ Settings save karna
    global current_dance_gif
    users_db.update_one({"_id": "bot_settings"}, {"$set": {"disabled_cmds": list(disabled_cmds)}}, upsert=True)

def get_level(bal):
    if bal < 500: return "Noob 🪵"
    elif bal < 1500: return "Bronze 🥉"
    elif bal < 3000: return "Silver 🥈"
    elif bal < 4000: return "Gold 🥇"
    elif bal < 10000: return "Platinum 💎"
    elif bal < 50000: return "Diamond 💠"
    elif bal < 2000000: return "Heroic 🦸‍♂️"
    else: return "GOD LEVEL 👑"

def get_rank(uid):
    sorted_users = sorted(users.items(), key=lambda x: x[1]['bal'], reverse=True)
    for rank, (user_id, data) in enumerate(sorted_users, 1):
        if user_id == uid: return rank
    return "N/A"

def get_user(user_obj):
    uid = user_obj.id
    if uid not in users:
        users[uid] = {
            "name": user_obj.first_name, "bal": 1000, "status": "Alive", 
            "last_daily": 0, "last_weekly": 0, "death_time": 0, "shield_until": 0,
            "loan": {"active": False, "lender_id": 0, "amount": 0, "due_time": 0},
            "kills": 0, "history": [], "inventory": [] # 👈 Jhola add kiya
        }
    else:
        users[uid]["name"] = user_obj.first_name
        if "kills" not in users[uid]: users[uid]["kills"] = 0
        if "history" not in users[uid]: users[uid]["history"] = []
        if "inventory" not in users[uid]: users[uid]["inventory"] = [] # Purane logo ko jhola dena
    return users[uid]

def add_history(uid, text):
    if "history" not in users[uid]: users[uid]["history"] = []
    users[uid]["history"].insert(0, text)
    users[uid]["history"] = users[uid]["history"][:10] 

def check_membership(uid):
    try:
        status = bot.get_chat_member(GROUP_USERNAME, uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def get_ai_response(user_text):
    # ------------------------------------------------------------
    # 1. प्राथमिकता: Cloudflare Workers AI
    # ------------------------------------------------------------
    try:
        CF_ACCOUNT_ID = os.environ.get('CF_ID')
        CF_API_TOKEN = os.environ.get('CF')

        if CF_ACCOUNT_ID and CF_API_TOKEN:
            url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/meta/llama-3.1-8b-instruct"
            headers = {"Authorization": f"Bearer {CF_API_TOKEN}"}
            payload = {
                "messages": [
                    {"role": "system", "content": "तुम Daimond Batch Bot हो। तुम्हारा व्यवहार दोस्ताना, बुद्धिमान और स्पष्ट है। तुम हमेशा सहज हिंदी या हिंग्लिश में उत्तर देते हो। उत्तर संक्षिप्त किन्तु अर्थपूर्ण होना चाहिए।"},
                    {"role": "user", "content": user_text}
                ],
                "max_tokens": 600,
                "temperature": 0.7
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return data['result']['response'].strip()
                else:
                    print(f"⚠️ Cloudflare API Error: {data}")
                    raise Exception("Cloudflare failed")
            else:
                print(f"⚠️ Cloudflare HTTP {resp.status_code}: {resp.text}")
                raise Exception("Cloudflare failed")
        else:
            print("⚠️ Cloudflare credentials missing, switching to Groq.")
            raise Exception("Cloudflare creds missing")
    except Exception as e:
        print(f"🔄 Cloudflare primary failed ({e}), falling back to Groq...")

        # ------------------------------------------------------------
        # 2. बैकअप: Groq (पुराना लॉजिक)
        # ------------------------------------------------------------
        try:
            GROQ_API_KEY = os.environ.get('GROQ_KEY')
            if not GROQ_API_KEY:
                return "बॉस, अभी मेरे दोनों दिमाग़ सो गए हैं। थोड़ी देर बाद try करो।"

            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "तुम Daimond Batch Bot हो, एक मित्रवत और चतुर सहायक। उत्तर हिंदी या हिंग्लिश में दो, संक्षिप्त और स्पष्ट।"},
                    {"role": "user", "content": user_text}
                ],
                "max_tokens": 300
            }
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            res_json = res.json()
            if res.status_code == 200:
                return res_json["choices"][0]["message"]["content"].strip()
            else:
                return f"Groq Error: {res_json.get('error', {}).get('message', 'Unknown')}"
        except Exception as e2:
            return f"अभी तकनीकी दिक्कत आ गई: {e2}"
            
def background_monitor():
    while True:
        try:
            curr = time.time()
            for uid, data in list(users.items()):
                if data['loan']['active'] and curr > data['loan']['due_time']:
                    lender_id = data['loan']['lender_id']
                    due_amount = data['loan']['amount']
                    cut = due_amount + 500
                    data['bal'] -= cut
                    if lender_id in users: users[lender_id]['bal'] += cut
                    data['loan']['active'] = False 
                    msg = f"🚨 **MAHA-GAREEB ALERT!** 🚨\n**{data['name']}** ne udhar nahi diya. Uske account se {cut} rs kaat kar wapas de diye gaye hain! 😂"
                    for gid in list(active_groups):
                        try: bot.send_message(gid, msg)
                        except: active_groups.remove(gid)
                
                if data['status'] == "Dead" and curr - data['death_time'] > 172800:
                    data['status'] = "Alive"
                    data['bal'] += 300
                    try: bot.send_message(uid, "Aap automatically zinda ho gaye aur 300 Rs mile hain!")
                    except: pass
            
            # Har 60 second mein database mein save karega (Spaces ekdum sahi hain)
            save_data()
        except: pass
        time.sleep(60)
        
@bot.message_handler(commands=['start'])
def start_cmd(message):
    print(f"🔥 /start received from {message.from_user.id}")
    # ... बाकी कोड ...
    
    # Bot ko yaad dilana ki wo is group me active hai
    if message.chat.type != 'private':
        active_groups.add(message.chat.id)
        
    # Agar koi DM me shield lene aaya hai
    if 'shield' in message.text:
        buy_shield(message)
        return
        
    # VIP Button tayyar karna
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💎 Join Daimond Batch", url="https://t.me/Daimondbatch"))
    markup.add(InlineKeyboardButton("▶️ Subscribe Freemind Coding", url="https://youtube.com/@freemind_coding?si=MCcJkwA1wuywfFMC"))
    
    # DM (Akele) aur Group ke liye alag-alag VIP message
    if message.chat.type == 'private':
        text = "👑 **welcome my Dear!**\nDaimond Batch Bot mein aapka swagat hai .\n\nNeeche button daba kar hamara official group join karein 👇"
        bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")
    else:
        text = f"👑 **Daimond Batch mein swagat hai {message.from_user.first_name}!**\n\nAap toh pehle se hamare khaas aadmi ho. Game khelo aur balance badhao!\n(Apne dosto ko lana ho toh neeche wala button bhejo aur khud bhi join ho jao group main 👇)"
        bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['play'])
def play_command(message):
    if len(message.text.split()) < 2 and not message.reply_to_message:
        return bot.reply_to(message, "❌ कोई गाना या लिंक दो!")

    query = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else message.reply_to_message.text
    user = get_user(message.from_user)
    chat_id = message.chat.id

    wait_msg = bot.reply_to(message, f"🔍 '{query}' खोजा जा रहा है...")
    try:
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        track = {
            'title': info['title'],
            'url': info['url'],
            'duration': info['duration'],
            'webpage_url': info['webpage_url'],
            'requester': user['name'],
            'requester_id': message.from_user.id
        }
        settings = get_group_settings(chat_id)
        settings['queue'].append(track)
        groups_db.update_one({"_id": chat_id}, {"$set": {"queue": settings['queue']}})
        
        if not settings.get('current_track'):
            play_next_in_queue(chat_id)
        
        bot.edit_message_text(f"✅ **{track['title']}** को कतार में जोड़ दिया गया।", chat_id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ गाना नहीं मिला या कोई एरर: {e}", chat_id, wait_msg.message_id)

@bot.message_handler(commands=['gift'])
def gift_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    if not message.reply_to_message: return bot.reply_to(message, "❌ Reply karke amount likho: /gift 5000")
    try:
        amt = int(message.text.split()[1])
        t_obj = message.reply_to_message.from_user
        get_user(t_obj)['bal'] += amt
        bot.reply_to(message, f"🎁 **GIFT SENT!**\nAdmin ne {t_obj.first_name} ko {amt} Rs free mein diye hain! 🎉")
    except: 
        bot.reply_to(message, "❌ Sahi Format: /gift 5000")

@bot.message_handler(commands=['auth'])
def make_vip(message):
    if not message.reply_to_message: return bot.reply_to(message, "किसी यूजर के मैसेज पर रिप्लाई करके /auth करें।")
    chat_id, admin_id, target_user = message.chat.id, message.from_user.id, message.reply_to_message.from_user
    member = bot.get_chat_member(chat_id, admin_id)
    if member.status not in ['administrator', 'creator']: return bot.reply_to(message, "❌ सिर्फ एडमिन ही VIP बना सकते हैं।")
    settings = get_group_settings(chat_id)
    if target_user.id not in settings['vip_users']:
        settings['vip_users'].append(target_user.id)
        groups_db.update_one({"_id": chat_id}, {"$set": {"vip_users": settings['vip_users']}})
        bot.reply_to(message, f"✅ {target_user.first_name} अब VIP है!")
    else: bot.reply_to(message, "यह यूजर पहले से VIP है।")

@bot.message_handler(commands=['toprank', 'top'])
def top_richest(message):
    if "toprank" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    if not users: return bot.reply_to(message, "Abhi tak koi user nahi hai sa!")
    
    # Sort karke exactly Top 10 nikalna
    sorted_users = sorted(users.items(), key=lambda x: x[1]['bal'], reverse=True)[:10]
    
    # Stylish Font (Unicode) aur Header
    text = "🏆 𝗚𝗟𝗢𝗕𝗔𝗟 𝗧𝗢𝗣 𝟭𝟬 𝗥𝗜𝗖𝗛𝗘𝗦𝗧 🏆\n━━━━━━━━━━━━━━━━━━━\n"
    
    for i, (uid, data) in enumerate(sorted_users):
        if i == 0: medal = "🥇"
        elif i == 1: medal = "🥈"
        elif i == 2: medal = "🥉"
        else: medal = f"🏅 {i+1}."
            
        # *Name* se Bold hoga, aur `Amount` se text ka alag (Monospace) design aayega
        text += f"{medal} *{data['name']}* ➾ 💰 `{data['bal']} Rs`\n"
        
    text += "━━━━━━━━━━━━━━━━━━━\n💡 *Tip:* `/rob` aur `/daily` se apni rank badhayein!"
    
    # parse_mode="Markdown" lagane se font styling apply hogi
    bot.reply_to(message, text, parse_mode="Markdown")

import os
import subprocess
import requests

@bot.message_handler(commands=['roast'])
def roast_cmd(message):
    # Lock Check
    if "roast" in disabled_cmds and message.from_user.id != ADMIN_ID: 
        return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    
    target_name = ""
    is_admin_target = False

    # 1. Target Dhoondhna (Reply se ya Naam likhne se)
    if message.reply_to_message:
        target_name = message.reply_to_message.from_user.first_name
        # 🚨 ADMIN SHIELD: Agar reply Admin ke message par kiya hai
        if message.reply_to_message.from_user.id == ADMIN_ID:
            is_admin_target = True
    else:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            target_name = parts[1].strip()
            # Agar koi direct likh de: /roast admin ya /roast boss
            admin_names = ["admin", "boss", "owner", "freemind"] 
            if any(name in target_name.lower() for name in admin_names):
                is_admin_target = True
        else:
            return bot.reply_to(message, "🎤 **Aise likho:**\n`/roast @username` ya kisi ke message par reply karke `/roast` likho!", parse_mode="Markdown")

    # 2. Prompt Set Karna (Dimaag)
    if is_admin_target:
        # 🔥 BACKFIRE: Jo admin se panga lega, bot usko hi dhoyega!
        target_name = message.from_user.first_name # Jisne command daali, uska naam
        sys_prompt = f"Tera naam Jarvis hai. {target_name} ne Boss (Admin) ko roast karne ki koshish ki. Ab tu ek hardcore desi underground rapper bankar {target_name} ki bhayanak beizzati kar. 4 line ka rap likh, bina gaali ke, par aukaat dikha de. Sirf rap ke lyrics dena."
        caption_text = f"🚨 **BOSS SE PANGA?** 🚨\n🎤 Target: {target_name} (Ulta pad gaya!)"
    else:
        # NORMAL ROAST
        sys_prompt = f"Tera naam Jarvis hai. Tu ek desi underground rapper hai. Tujhe '{target_name}' ki beizzati (roast) karni hai. 4 line ka tagda aur funny rap likh. Bina gaali ke, par ego tod de. Sirf rap ke bol likhna."
        caption_text = f"🔥 **DAIMOND BATCH DISS TRACK** 🔥\n🎤 Target: {target_name}"

    # Render ki tijori se Groq ki chaabi nikalna
    GROQ_API_KEY = os.environ.get('GROQ_KEY')
    if not GROQ_API_KEY:
        return bot.reply_to(message, "❌ Boss! Groq ki chaabi (GROQ_KEY) nahi mili!")

    wait_msg = bot.reply_to(message, "🎤 *Beat drop ho rahi hai... Mic check 1-2-3...*", parse_mode="Markdown")
    bot.send_chat_action(message.chat.id, 'record_voice')

    try:
        # 3. Groq LLaMA-3 (Rap Likhwana)
        headers_chat = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": f"Chal {target_name} ko dhakka maar ke roast kar!"}]}
        res_chat = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers_chat, json=payload)
        ai_reply = res_chat.json()["choices"][0]["message"]["content"].strip()

        # 4. HF API se Rap Record Karna (Bhaari aawaz + Rap Beat)
        safe_reply = ai_reply.replace('"', '').replace("'", "")
        res_tts = requests.post(f"{HF_API}/tts", data={
            "text": safe_reply, 
            "rate": "+10%",
            "voice": "hi-IN-MadhurNeural",
            "bgm": "roast"  # 👈 YE NAYA ADD KIYA HAI
        })
        
        if res_tts.status_code == 200:
            from io import BytesIO
            audio_bytes = BytesIO(res_tts.content)
            audio_bytes.name = "roast.ogg"
            bot.send_voice(message.chat.id, audio_bytes, caption=caption_text)
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ Mic kharab ho gaya sa! (Awaaz nahi bani)", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, wait_msg.message_id)

import os
import subprocess
import requests

@bot.message_handler(commands=['reel', 'studio'])
def make_ai_reel(message):
    if "reel" in disabled_cmds and message.from_user.id != ADMIN_ID: return
    topic = message.text.replace("/reel", "").replace("/studio", "").strip()
    if not topic: return bot.reply_to(message, "🎬 **Aise likho:**\n`/reel zindagi mein success`")

    wait_msg = bot.reply_to(message, "🎬 *Reel ban rahi hai... Script, Camera aur Voice set ho raha hai sa!*")
    try:
        GROQ_KEY = os.environ.get('GROQ_KEY')
        HF_KEY = os.environ.get('H')
        
        # 1. Groq se Reel ki Script
        headers_chat = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": "Tu Instagram Reel creator hai. Ekdum fast, energetic 2 line ki Hindi motivational shayari likh. Sirf text dena."}, {"role": "user", "content": topic}]}
        res_chat = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers_chat, json=payload, timeout=15)
        ai_script = res_chat.json()["choices"][0]["message"]["content"].strip()

        # 2. FLUX AI se Photo (Naya Router Link)
        flux_url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
        headers_hf = {"Authorization": f"Bearer {HF_KEY}"}
        img_prompt = "Vertical portrait style, 9:16 mobile wallpaper, energetic, trending aesthetic, concept art about " + topic
        res_img = requests.post(flux_url, headers=headers_hf, json={"inputs": img_prompt}, timeout=40)
        
        # 3. 🚀 Apne naye HF API se Awaaz banwana (Tez awaaz +15%)
        safe_script = ai_script.replace('"', '').replace("'", "")
        res_tts = requests.post(f"{HF_API}/tts", data={"text": safe_script, "rate": "+15%"})
        
        # 4. Bina storage ghere Telegram ko bhejna
        if res_img.status_code == 200 and res_tts.status_code == 200:
            bot.send_photo(message.chat.id, photo=res_img.content, caption=f"🎬 **Reel Topic:** {topic}")
            
            from io import BytesIO
            audio_bytes = BytesIO(res_tts.content)
            audio_bytes.name = "reel.ogg"
            bot.send_voice(message.chat.id, audio_bytes, caption=f"✨ **Listen:**\n\n{ai_script}")
            
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ Photo ya Awaaz banne me error aaya sa!", message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, wait_msg.message_id)

import os
import subprocess
import requests

@bot.message_handler(commands=['dl', 'insta', 'yt'])
def download_media(message):
    try:
        link = message.text.split(' ', 1)[1]
    except:
        return bot.reply_to(message, "Link do: /dl https://...")
    wait_msg = bot.reply_to(message, "⏳ Download ho raha hai...")
    try:
        response = requests.post(f"{HF_API}/download", json={"url": link}, timeout=180)
        if response.status_code == 200:
            bot.send_video(message.chat.id, response.content, caption="✅ Done!")
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(f"❌ Download fail: {response.text}", message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, wait_msg.message_id)
            
# ==========================================
# 📰 THE AI NEWS ANCHOR (Subah 8 aur Raat 8)
# ==========================================
def auto_news_broadcast():
    if not active_groups:
        return

    HF_KEY = os.environ.get('H')
    GROQ_KEY = os.environ.get('GROQ_KEY')
    if not HF_KEY or not GROQ_KEY:
        return

    try:
        # 1. Groq से 5 मिनट की ताज़ा हिंदी न्यूज़ स्क्रिप्ट जनरेट करवाएँ
        headers_chat = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        prompt = """तुम एक पेशेवर समाचार वाचक हो। कृपया एक 5 मिनट का विस्तृत समाचार बुलेटिन तैयार करो।
        विषय: भारत और दुनिया की प्रमुख घटनाएँ, खेल, मनोरंजन, तकनीक और मौसम।
        भाषा: शुद्ध देवनागरी हिंदी, ताकि टीटीएस सही उच्चारण कर सके।
        प्रारूप: "नमस्कार! मैं हूँ आपकी एआई एंकर..." से शुरू करो। हर खबर को अलग पैराग्राफ में लिखो। कुल शब्द लगभग 700-800 हों।
        आज की तारीख 11 अप्रैल 2026 है। कृपया वास्तविक घटनाओं का संदर्भ  दे,ें।"""
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2500,
            "temperature": 0.8
        }
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers_chat, json=payload, timeout=30)
        if res.status_code != 200:
            print("News script generation failed")
            return
        script = res.json()["choices"][0]["message"]["content"].strip()

        # 2. TTS के लिए HF API को कॉल करें (Swara आवाज़, न्यूज़ बीट)
        res_tts = requests.post(f"{HF_API}/tts", data={
            "text": script,
            "rate": "+0%",
            "voice": "hi-IN-SwaraNeural",
            "bgm": "news"
        })

        # 3. FLUX से एंकर की तस्वीर
        flux_url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
        headers_hf = {"Authorization": f"Bearer {HF_KEY}"}
        img_prompt = "A beautiful and professional female Indian TV news anchor sitting at a futuristic news desk with BREAKING NEWS graphics, cinematic lighting, photorealistic"
        res_img = requests.post(flux_url, headers=headers_hf, json={"inputs": img_prompt}, timeout=60)

        # 4. सभी सक्रिय समूहों में भेजें
        if res_tts.status_code == 200 and res_img.status_code == 200:
            from io import BytesIO
            for gid in list(active_groups):
                try:
                    bot.send_photo(gid, photo=res_img.content, caption="📰 **DAIMOND BATCH लाइव न्यूज़** 📰\n*(🎙️ वॉइस: AI फीमेल एंकर)*")
                    audio_bytes = BytesIO(res_tts.content)
                    audio_bytes.name = "news.ogg"
                    bot.send_voice(gid, audio_bytes, caption="🎙️ *आज की प्रमुख ख़बरें (5 मिनट)*")
                except Exception as e:
                    print(f"Group {gid} में भेजने में त्रुटि: {e}")

    except Exception as e:
        print(f"News Anchor System Error: {e}")


@bot.message_handler(commands=['video'])
def make_ai_video(message):
    if "video" in disabled_cmds and message.from_user.id != ADMIN_ID: return
    
    # 🚨 Check: User ne photo par reply kiya hai ya nahi
    if not message.reply_to_message or not message.reply_to_message.photo:
        return bot.reply_to(message, "🎬 **Aise likho:**\nKisi aachi photo par reply karke `/video mehnat aur paisa` likho sa!")

    topic = message.text.replace("/video", "").strip()
    if not topic: topic = "Deep motivational thought" # Agar topic na likha ho toh default
    
    wait_msg = bot.reply_to(message, "🎬 *Aapki photo par Voice aur Script lagai jaa rahi hai...*")
    try:
        GROQ_KEY = os.environ.get('GROQ_KEY')
        
        # 1. Groq se Deep Cinematic Script
        headers_chat = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": "Tu ek YouTube Documentary voice-over artist hai. Ekdum deep, serious aur cinematic 4 line ka Hindi intro likh. Sirf script dena."}, {"role": "user", "content": topic}]}
        res_chat = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers_chat, json=payload, timeout=15)
        ai_script = res_chat.json()["choices"][0]["message"]["content"].strip()

        # 2. 🚀 Apne naye HF API se Awaaz banwana (Bhaari aur Slow awaaz -15%)
        safe_script = ai_script.replace('"', '').replace("'", "")
        res_tts = requests.post(f"{HF_API}/tts", data={"text": safe_script, "rate": "-15%"})
        
        # 3. Photo aur Voice ko chipka kar bhejna
        if res_tts.status_code == 200:
            # User ki bheji hui photo ka ID uthana
            file_id = message.reply_to_message.photo[-1].file_id
            
            # Wahi photo wapas bhejna with Caption
            bot.send_photo(message.chat.id, photo=file_id, caption=f"🎬 **Video Topic:** {topic}")
            
            from io import BytesIO
            audio_bytes = BytesIO(res_tts.content)
            audio_bytes.name = "video.ogg"
            bot.send_voice(message.chat.id, audio_bytes, caption=f"✨ **Listen:**\n\n{ai_script}")
            
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ Awaaz banne me error aaya sa!", message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, wait_msg.message_id)

@bot.message_handler(commands=['guess'])
def start_guess(message):
    chat_id = message.chat.id
    user = message.from_user

    # Check if game already running
    if game_sessions.get(chat_id, {}).get('active'):
        return bot.reply_to(message, "⚠️ Ek game pehle se chal raha hai! Pehle guess karo ya ruko.")

    target = random.randint(1, 100)
    game_sessions[chat_id] = {
        'target': target,
        'active': True,
        'started_by': user.id,
        'started_at': time.time(),
        'attempts': {}
    }

    # Welcome message with instructions
    welcome_text = (
        f"🎮 **GUESS THE NUMBER – LEGEND EDITION** 🎮\n\n"
        f"🔥 **{user.first_name}** ne game start kiya!\n"
        f"🔢 Maine 1–100 ke beech ek number socha hai.\n"
        f"👥 Group mein koi bhi guess kar sakta hai.\n"
        f"⏳ Jaldbaazi mat karo – sabse pehle sahi guess karne wala jeetega!\n\n"
        f"🎁 **Inam:** 500 Rs + 100 XP (jeetne wale ko)\n"
        f"⌨️ Bas number type karo chat mein..."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['stealth'])
def toggle_stealth(message):
    user_id = message.from_user.id

    try:
        current = db.memories.find_one({"user_id": user_id}, {"stealth": 1})
        new_flag = not (current and current.get("stealth", False))

        db.memories.update_one(
            {"user_id": user_id},
            {"$set": {"stealth": new_flag}},
            upsert=True
        )

        status_emoji = "🟢 ON" if new_flag else "🔴 OFF"
        status_text = "**ACTIVATED** – अब आपको कोई ट्रैक नहीं कर सकता!" if new_flag else "**DEACTIVATED** – आप अब दिखाई देंगे।"
        bot.reply_to(message, f"🥷 **Stealth Mode** {status_emoji}\n{status_text}", parse_mode='Markdown')

    except Exception as e:
        print(f"Stealth DB Error: {e}")
        bot.reply_to(message, "❌ Unable to toggle stealth mode right now.")

@bot.message_handler(content_types=['photo'])
def scan_image(message):
    user = message.from_user
    file_id = message.photo[-1].file_id
    processing_msg = bot.reply_to(message, "🔍 **HF Space पर स्कैन हो रहा है...**")

    try:
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        files = {'image': ('image.jpg', downloaded, 'image/jpeg')}
        
        # HF Space के नए एंडपॉइंट को कॉल करो
        response = requests.post(f"{HF_API}/scan", files=files, timeout=90)

        if response.status_code == 200:
            result = response.json()
            final_output = ""
            if result.get('faces'):
                final_output += f"👤 **Faces Detected:** {result['faces']}\n\n"
            if result.get('text'):
                display_text = result['text'][:300] + ('...' if len(result['text'])>300 else '')
                final_output += f"📝 **Extracted Text:**\n```{display_text}```"
            if not final_output:
                final_output = "❌ कुछ भी detect नहीं हुआ।"
            
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id,
                text=f"📊 **Scan Report** 📊\n\n{final_output}",
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id,
                text=f"❌ HF Space Error: {response.text}"
            )
    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            text=f"❌ Connection Error: {e}"
        )




@bot.message_handler(commands=['bal'])
def check_bal(message):
    if "bal" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    target_obj = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    u = get_user(target_obj)
    
    rank = get_rank(target_obj.id)
    total_users = len(users)
    
    if target_obj.id == ADMIN_ID: shield_status = "🛡️ UNLIMITED (Admin)"
    else: shield_status = "🛡️ Protected" if time.time() < u['shield_until'] else "❌ Protection Expired"
    
    # 🎒 Inventory nikalna
    inv = u.get('inventory', [])
    inv_text = ", ".join(inv) if inv else "Kuch nahi (KHALI)"
    
    bot.reply_to(message, f"🏦 **ACCOUNT: {u['name']}**\n🌍 Global Rank: #{rank} (out of {total_users})\n🏆 Level: {get_level(u['bal'])}\n💰 Balance: {u['bal']} Rs\n🔪 Kills: {u.get('kills', 0)}\n🔰 Shield: {shield_status}\n🎒 **ITEMS:** {inv_text}\n❤️ Status: {u['status']}")
import os
import subprocess

@bot.message_handler(commands=['speak', 'bolo'])
def speak_cmd(message):
    if "speak" in disabled_cmds and message.from_user.id != ADMIN_ID: return
    text = message.text.replace("/speak", "").replace("/bolo", "").strip()
    if not text: return bot.reply_to(message, "🗣️ Likh ke do bot kya bolega!")
        
    wait_msg = bot.reply_to(message, "⏳ *Engine awaaz record kar raha hai...*")
    try:
        res = requests.post(f"{HF_API}/tts", data={"text": text, "rate": "+0%"})
        if res.status_code == 200:
            bot.send_voice(message.chat.id, res.content, caption="🎙️ **Daimond Batch AI Voice**")
            bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, wait_msg.message_id)

@bot.message_handler(commands=['nuke', 'resetall'])
def nuke_database(message):
    # सिर्फ एडमिन (Boss) ही ये बटन दबा सकता है
    if message.from_user.id != ADMIN_ID: 
        return bot.reply_to(message, "❌ तुम्हारी औकात नहीं है दुनिया खत्म करने की!")
        
    wait_msg = bot.reply_to(message, "⚠️ *सिस्टम रिसेट शुरू... सबके पैसे उड़ाए जा रहे हैं...*", parse_mode="Markdown")
    
    try:
        # 1. RAM (Temporary Memory) में सबका डाटा 1000 कर दो
        for uid in list(users.keys()):
            users[uid]['bal'] = 1000
            users[uid]['kills'] = 0
            users[uid]['inventory'] = []
            users[uid]['status'] = "Alive"
            users[uid]['history'] = ["🚨 MAHA-PRALAY: नया जन्म!"]
            # अगर किसी पर उधार है तो वो भी माफ़
            if 'loan' in users[uid]:
                users[uid]['loan'] = {"active": False, "lender_id": 0, "amount": 0, "due_time": 0}

        # 2. इस नए (खाली) डाटा को तुरंत MongoDB में सेव कर दो
        save_data()
        
        # 3. MongoDB से वो कचरा भी साफ़ कर दो जो RAM में नहीं है
        users_db.delete_many({"_id": {"$ne": "bot_settings"}}) 
        save_data() # वापस फ्रेश डाटा डाल दो
        
        bot.delete_message(message.chat.id, wait_msg.message_id)
        bot.send_message(message.chat.id, "🌋 **MAHA-PRALAY COMPLETE!** 🌋\n\nबॉस का हुक्म! शहर के सारे बैंक खाली कर दिए गए हैं। चोर बाज़ार का सारा सामान जलकर ख़ाक हो गया है।\n\n**सबकी नई शुरुआत: 1000 Rs 💰**")
        
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, wait_msg.message_id)

# ================== 🎙️ नया TTS कमांड (Indri TTS via HF Space) ==================
import time
import requests
# ... बाकी सभी ज़रूरी imports ...

@bot.message_handler(commands=['tts'])
def tts_command_with_retry(message):
    # --- टेक्स्ट निकालने का वही कोड ---
    if message.reply_to_message:
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        elif message.reply_to_message.caption:
            text = message.reply_to_message.caption
        else:
            return bot.reply_to(message, "❌ रिप्लाई किए गए मैसेज में कोई टेक्स्ट नहीं है!")
    else:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            return bot.reply_to(message, "🎙️ **उपयोग:**\n`/tts <टेक्स्ट>`\nया किसी मैसेज पर रिप्लाई करके `/tts` लिखें", parse_mode='Markdown')
        text = parts[1].strip()
    if not text:
        return bot.reply_to(message, "❌ बोलने के लिए कुछ टेक्स्ट तो दो!")

    wait_msg = bot.reply_to(message, "🎤 *बुलबुल आवाज़ बना रही है...*", parse_mode='Markdown')
    bot.send_chat_action(message.chat.id, 'record_audio')
    
    # --- API कॉल के लिए सेटिंग्स ---
    url = "https://api.sarvam.ai/text-to-speech"
    headers = {
        "api-subscription-key": os.environ.get('S1'), # सिर्फ एक कुंजी का उपयोग करें
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": [text],
        "target_language_code": "hi-IN",
        "speaker": "meera",
        "model": "bulbul:v1"
    }
    
    # --- रिट्री लॉजिक (थोड़ा रुककर फिर से कोशिश करना) ---
    max_retries = 3
    retry_delay = 10  # 10 सेकंड
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                audio_url = response.json()['audios'][0]
                audio_data = requests.get(audio_url).content
                audio_bytes = BytesIO(audio_data)
                audio_bytes.name = "voice.wav"
                bot.send_voice(message.chat.id, audio_bytes, caption=f"🎙️ {text[:100]}")
                bot.delete_message(message.chat.id, wait_msg.message_id)
                return  # सफलता! लूप से बाहर निकल जाएं
            
            elif response.status_code == 429:
                # रेट लिमिट खत्म हो गई है, थोड़ा रुकें और फिर कोशिश करें
                if attempt < max_retries - 1:
                    print(f"⚠️ सर्वम API रेट लिमिट हिट। {retry_delay} सेकंड में पुनः प्रयास {attempt+2}/{max_retries}...")
                    time.sleep(retry_delay)
                    continue
                else:
                    bot.edit_message_text(f"❌ सर्वम API: अभी बहुत भीड़ है। थोड़ी देर बाद कोशिश करें।", message.chat.id, wait_msg.message_id)
                    return
            else:
                bot.edit_message_text(f"❌ सर्वम API एरर: {response.status_code}", message.chat.id, wait_msg.message_id)
                return
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⚠️ कनेक्शन एरर: {e}। पुनः प्रयास {attempt+2}/{max_retries}...")
                time.sleep(retry_delay)
                continue
            else:
                bot.edit_message_text(f"❌ कनेक्शन एरर: {e}", message.chat.id, wait_msg.message_id)
                return

@bot.message_handler(commands=['math'])
def math_game(message):
    chat_id = message.chat.id

    if game_sessions.get(chat_id, {}).get('active'):
        return bot.reply_to(message, "⚠️ Pehle game khatam karo!")

    a = random.randint(1, 50000)
    b = random.randint(1, 500000)
    ans = a + b

    game_sessions[chat_id] = {
        'ans': ans,
        'active': True,
        'started_by': message.from_user.id
    }

    bot.reply_to(
        message,
        f"➕ **MATH BLITZ!** ➕\n\n"
        f"❓ Sawaal: `{a} + {b} = ?`\n"
        f"⏱️ Jaldi se answer type karo!",
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['setrole'])
def set_personality(message):
    user_id = message.from_user.id
    parts = message.text.split(' ', 1)

    if len(parts) < 2:
        return bot.reply_to(
            message,
            "🎭 **Custom Persona Set Karne Ka Tareeka:**\n"
            "`/setrole <koi bhi role>`\n\n"
            "💡 *Jaise: /setrole philosopher*",
            parse_mode='Markdown'
        )

    role = parts[1].strip()
    if len(role) > 50:
        return bot.reply_to(message, "❌ Role 50 characters se chhota rakho!")

    try:
        db.memories.update_one(
            {"user_id": user_id},
            {"$set": {"personality": role, "role_active": True, "updated_at": time.time()}},
            upsert=True
        )
        bot.reply_to(
            message,
            f"✅ **Custom Persona Set!**\n"
            f"🎭 Role: *{role}*\n"
            f"💬 Ab main aapse is role mein baat karunga!\n\n"
            f"🛑 Role band karne ke liye: `/setroleoff`",
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"SetRole DB Error: {e}")
        bot.reply_to(message, "❌ Database error! Thodi der baad try karo.")

TYPING_SENTENCES = [
    "The quick brown fox jumps over the lazy dog",
    "A journey of a thousand miles begins with a single step",
    "All that glitters is not gold",
    "Actions speak louder than words",
    "Beauty is in the eye of the beholder",
    "Better late than never",
    "Birds of a feather flock together",
    "Cleanliness is next to godliness",
    "Don't count your chickens before they hatch",
    "Easy come easy go",
    "Every cloud has a silver lining",
    "Fortune favors the bold",
    "Good things come to those who wait",
    "Honesty is the best policy",
    "It never rains but it pours",
    "Kill two birds with one stone",
    "Laughter is the best medicine",
    "Look before you leap",
    "Make hay while the sun shines",
    "Necessity is the mother of invention",
    "No pain no gain",
    "Old habits die hard",
    "Practice makes perfect",
    "Rome was not built in a day",
    "Slow and steady wins the race",
    "The early bird catches the worm",
    "The grass is always greener on the other side",
    "Time flies when you're having fun",
    "Too many cooks spoil the broth",
    "When in Rome do as the Romans do",
    "Where there's a will there's a way",
    "You can lead a horse to water but you can't make it drink",
    "You reap what you sow",
    "A picture is worth a thousand words",
    "Absence makes the heart grow fonder",
    "All roads lead to Rome",
    "An apple a day keeps the doctor away",
    "Beggars can't be choosers",
    "Blood is thicker than water",
    "Curiosity killed the cat",
    "Don't bite the hand that feeds you",
    "Don't put all your eggs in one basket",
    "Every dog has its day",
    "Familiarity breeds contempt",
    "Give someone the cold shoulder",
    "Haste makes waste",
    "He who laughs last laughs longest",
    "Home is where the heart is",
    "If the shoe fits wear it",
    "It takes two to tango",
    "Keep your friends close and your enemies closer",
    "Knowledge is power",
    "Let sleeping dogs lie",
    "Love is blind",
    "Money doesn't grow on trees",
    "Never say never",
    "One man's trash is another man's treasure",
    "Out of sight out of mind",
    "People who live in glass houses shouldn't throw stones",
    "Silence is golden",
    "Strike while the iron is hot",
    "The pen is mightier than the sword",
    "There's no place like home",
    "Two heads are better than one",
    "Variety is the spice of life",
    "What goes around comes around",
    "You can't have your cake and eat it too",
    "A watched pot never boils",
    "All's fair in love and war",
    "Barking dogs seldom bite",
    "Better safe than sorry",
    "Cross that bridge when you come to it",
    "Don't cry over spilled milk",
    "First come first served",
    "Half a loaf is better than none",
    "If it ain't broke don't fix it",
    "Ignorance is bliss",
    "In the land of the blind the one-eyed man is king",
    "It's always darkest before the dawn",
    "Lightning never strikes twice in the same place",
    "Like father like son",
    "Live and learn",
    "Misery loves company",
    "No news is good news",
    "Once bitten twice shy",
    "Opportunity seldom knocks twice",
    "Patience is a virtue",
    "Prevention is better than cure",
    "Spare the rod and spoil the child",
    "Still waters run deep",
    "The apple never falls far from the tree",
    "The best things in life are free",
    "The more the merrier",
    "The pot calling the kettle black",
    "There's no smoke without fire",
    "Time is money",
    "Truth is stranger than fiction",
    "Walls have ears",
    "What's done is done",
    "When it rains it pours",
    "You can't judge a book by its cover",
    "You scratch my back and I'll scratch yours",
    "A leopard cannot change its spots",
    "As you sow so shall you reap",
    "Charity begins at home",
    "Don't make a mountain out of a molehill",
    "Empty vessels make the most noise",
    "Even a broken clock is right twice a day",
    "Faith will move mountains",
    "God helps those who help themselves",
    "Great minds think alike",
    "Hope for the best prepare for the worst",
    "If wishes were horses beggars would ride",
    "It's no use crying over spilled milk",
    "Jack of all trades master of none",
    "Keep your chin up",
    "Leave no stone unturned",
    "Life is what you make it",
    "Man proposes God disposes",
    "Many hands make light work",
    "Money is the root of all evil",
    "Nothing ventured nothing gained",
    "One good turn deserves another",
    "Out of the frying pan into the fire",
    "Pride comes before a fall",
    "Seeing is believing",
    "The blind leading the blind",
    "The devil is in the details",
    "The end justifies the means",
    "The first step is always the hardest",
    "The love of money is the root of all evil",
    "The show must go on",
    "The squeaky wheel gets the grease",
    "Third time's a charm",
    "Tomorrow is another day",
    "Two wrongs don't make a right",
    "United we stand divided we fall",
    "We'll cross that bridge when we come to it",
    "What doesn't kill you makes you stronger",
    "When the going gets tough the tough get going",
    "You are what you eat",
    "You can't please everyone",
    "A friend in need is a friend indeed",
    "A penny saved is a penny earned",
    "A rolling stone gathers no moss",
    "All good things must come to an end",
    "Be yourself everyone else is already taken",
    "Carpe diem seize the day",
    "Do unto others as you would have them do unto you",
    "Don't put off until tomorrow what you can do today",
    "Everything happens for a reason",
    "Fall seven times stand up eight",
    "Good fences make good neighbors",
    "Happiness is not a destination it is a way of life",
    "If you can't beat them join them",
    "It is better to give than to receive",
    "Keep your eyes on the prize",
    "Live and let live",
    "Music makes the world go round",
    "Never go to bed angry",
    "One day at a time",
    "Practice what you preach",
    "Sharing is caring",
    "Take it with a grain of salt",
    "The best is yet to come",
    "The family that prays together stays together",
    "The more things change the more they stay the same",
    "The only constant in life is change",
    "There is no time like the present",
    "Today is the first day of the rest of your life",
    "Waste not want not",
    "We are all in the same boat",
    "You miss a hundred percent of the shots you don't take",
    "A calm sea does not make a skilled sailor",
    "A rising tide lifts all boats",
    "Actions have consequences",
    "Aim for the moon if you miss you may hit a star",
    "Always look on the bright side of life",
    "Be kind whenever possible it is always possible",
    "Comparison is the thief of joy",
    "Dance like nobody's watching",
    "Do what you can with what you have where you are",
    "Don't let the bed bugs bite",
    "Enjoy the little things in life",
    "Every moment is a fresh beginning",
    "Everything in moderation including moderation",
    "Follow your heart but take your brain with you",
    "Give credit where credit is due",
    "Happiness is homemade",
    "Have courage and be kind",
    "If you change the way you look at things the things you look at change",
    "In the middle of every difficulty lies opportunity",
    "It's not about the destination it's about the journey",
    "Kindness is a language which the deaf can hear and the blind can see",
    "Let your light shine",
    "Life is short make it sweet",
    "Live life to the fullest",
    "Love like you've never been hurt",
    "Make each day your masterpiece",
    "Never let the fear of striking out keep you from playing the game",
    "No act of kindness no matter how small is ever wasted",
    "One small positive thought in the morning can change your whole day",
    "Peace begins with a smile",
    "Positive anything is better than negative nothing",
    "Smile it confuses people",
    "Strive for progress not perfection",
    "The best way to cheer yourself is to try to cheer someone else up",
    "The greatest wealth is health",
    "The secret of getting ahead is getting started",
    "This too shall pass",
    "Turn your wounds into wisdom",
    "When you have a dream you've got to grab it and never let go",
    "Wherever you go go with all your heart",
    "Yesterday is history tomorrow is a mystery today is a gift"
]

@bot.message_handler(commands=['type'])
def type_race(message):
    chat_id = message.chat.id
    if game_sessions.get(chat_id, {}).get('active'):
        return bot.reply_to(message, "⚠️ Pehle se ek game chal raha hai!")

    target_text = random.choice(TYPING_SENTENCES)
    game_sessions[chat_id] = {
        'text': target_text,
        'active': True,
        'started_by': message.from_user.id,
        'started_at': time.time()
    }

    msg_text = (
        f"⌨️ **TYPING RACE – READY?** ⌨️\n\n"
        f"📋 Niche diya text **EXACTLY** type karo:\n"
        f"`{target_text}`\n\n"
        f"⚡ Sabse pehle type karne wala jeetega!\n"
        f"🎁 Inam: 300 Rs"
    )
    bot.send_message(chat_id, msg_text, parse_mode='Markdown')

@bot.message_handler(commands=['setroleoff'])
def disable_personality(message):
    user_id = message.from_user.id

    try:
        result = db.memories.update_one(
            {"user_id": user_id},
            {"$set": {"role_active": False, "updated_at": time.time()}}
        )

        if result.modified_count > 0:
            bot.reply_to(
                message,
                "🛑 **Persona Disabled!**\n"
                "🎭 Ab main default friendly mode mein baat karunga.\n"
                "💡 Wapas set karne ke liye: `/setrole <role>`",
                parse_mode='Markdown'
            )
        else:
            bot.reply_to(message, "ℹ️ Aapne pehle se koi role set nahi kiya hai.")
    except Exception as e:
        print(f"SetRoleOff DB Error: {e}")
        bot.reply_to(message, "❌ Derror! Thodi der baad try karo.")



@bot.message_handler(commands=['shield'])
def shield_req(message):
    if "shield" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    # Agar Admin shield command lagata hai
    if message.from_user.id == ADMIN_ID:
        return bot.reply_to(message, "👑 **Boss!** Aap Admin ho, aapki Shield hamesha ke liye UNLIMITED hai. Aapko kharidne ki koi zaroorat nahi!")
        
    if message.chat.type != 'private':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("DM Me Aao", url=f"https://t.me/{bot.get_me().username}?start=shield"))
        return bot.reply_to(message, "Shield lagane ke liye akele me aao sa!", reply_markup=markup)
    buy_shield(message)

def buy_shield(message):
    u = get_user(message.from_user)
    if u['bal'] < 500: return bot.send_message(message.chat.id, "❌ Shield ke liye 500 rs chahiye!")
    u['bal'] -= 500
    u['shield_until'] = time.time() + 86400 # 24 Hours
    bot.send_message(message.chat.id, "🛡️ **SHIELD ACTIVATED!**\n500 Rs cut gaye. Ab agle 24 ghante tak aapko koi nahi loot payega.")

@bot.message_handler(commands=['imagine', 'ai'])
def handle_imagine(message):
    try:
        prompt = message.text.split(' ', 1)[1]
    except:
        return bot.reply_to(message, "❌ Prompt likho bhai! /imagine ek udta hua ghoda")

    msg = bot.reply_to(message, "🌀 Photo ban rahi hai...")
    try:
        response = requests.post(f"{HF_API}/imagine", json={"prompt": prompt}, timeout=120)
        if response.status_code == 200:
            bot.send_photo(message.chat.id, response.content, caption=f"✨ {prompt}")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text(f"❌ Error: {response.text}", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Connection Error: {e}", message.chat.id, msg.message_id)

@bot.message_handler(commands=['give', 'donate'])
def give_money(message):
    if "give" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    if not message.reply_to_message: return bot.reply_to(message, "Reply karke amount likho.")
    try:
        amt = int(message.text.split()[1])
        s_obj = message.from_user
        r_obj = message.reply_to_message.from_user
        s = get_user(s_obj)
        r = get_user(r_obj)
        
        if s['bal'] < amt: return bot.reply_to(message, "Paise nahi hain!")
        
        s['bal'] -= amt
        r['bal'] += amt
        
        # 🔥 VIP Legend Message
        msg = f"💸 **MAHA-DAAN!** 💸\n\n**{s['name']}** ne \n🎁 donate kiye **{r['name']}** ko\n\n🏆 Level: {get_level(s['bal'])}\n💰 Rakam: {amt} Rs"
        bot.reply_to(message, msg)
    except: bot.reply_to(message, "Format: /give 100")    

@bot.message_handler(commands=['dance'])
def dance_cmd(message):
    if "dance" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    
    try:
        # Ab ye purane link ki jagah aapka set kiya hua GIF (current_dance_gif) bhejega
        bot.send_animation(message.chat.id, current_dance_gif, caption="🕺 **Balle Balle! Party Time!** 💃", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "🕺 **Balle Balle! Party Time!** 💃\n*(GIF load nahi hua sa!)*", parse_mode="Markdown")

import os
import subprocess
import requests

@bot.message_handler(commands=['sketch'])
def handle_sketch(message):
    reply = message.reply_to_message
    if not reply or not reply.photo:
        return bot.reply_to(message, "❌ **Bhai, kisi photo par reply karke /sketch likho!**")

    msg = bot.reply_to(message, "🎨 **Daimond Engine sketch bana raha hai...**")
    
    try:
        file_info = bot.get_file(reply.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # 🚀 APNI Custom Engine ko request bhejo
        files = {'image': ('input.jpg', downloaded_file, 'image/jpeg')}
        response = requests.post(f"{HF_API}/sketch", files=files, timeout=60)

        if response.status_code == 200:
            bot.send_photo(message.chat.id, response.content, caption="✅ **Lo bhai, tumhara sketch taiyar hai!**")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text(f"❌ **Engine Error: {response.status_code}**", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"⚠️ **Error:** {str(e)}", message.chat.id, msg.message_id)
        
@bot.message_handler(commands=['ask'])
def ask_ai_voice(message):
    # Lock Check
    if "ai" in disabled_cmds and message.from_user.id != ADMIN_ID: 
        return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    
    prompt = message.text.replace("/ask", "").strip()
    if not prompt:
        return bot.reply_to(message, "🗣️ **Aise likho:**\n`/ask Duniya ka sabse ameer aadmi kon hai?`", parse_mode="Markdown")
        
    # Render ki tijori se Groq ki chaabi nikalna
    GROQ_API_KEY = os.environ.get('GROQ_KEY')
    if not GROQ_API_KEY:
        return bot.reply_to(message, "❌ Boss! nahi hua sorry")

    wait_msg = bot.reply_to(message, "⏳ *gala saaf kar raha hu...*", parse_mode="Markdown")
    bot.send_chat_action(message.chat.id, 'record_voice')
    
    try:
        # 1. Groq LLaMA-3 (Dimaag lagana)
        headers_chat = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": "Tera naam Jarvis hai. Tu Daimond Batch ka AI assistant hai. Hamesha sirf 2-3 line mein aur Hinglish main jawab dena, taaki bolne mein zyada lamba na lage."}, {"role": "user", "content": prompt}]}
        res_chat = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers_chat, json=payload)
        
        if res_chat.status_code != 200:
            raise Exception("API server thoda busy hai sa!")
            
        ai_reply = res_chat.json()["choices"][0]["message"]["content"].strip()

        # 2. 🚨 FIXED: HF API se Awaaz banwana
        safe_reply = ai_reply.replace('"', '').replace("'", "")
        res_tts = requests.post(f"{HF_API}/tts", data={"text": safe_reply, "rate": "+0%"})
        
        if res_tts.status_code == 200:
            from io import BytesIO
            audio_bytes = BytesIO(res_tts.content)
            audio_bytes.name = "jarvis.ogg"
            bot.send_voice(message.chat.id, audio_bytes, caption=f"🎙️ **Jarvis AI**\n🗣️ *Aapka sawal:* {prompt}")
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ Jarvis ka gala kharab hai sa!", message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Jarvis ko khasi aa gayi sa! Error: {e}", message.chat.id, wait_msg.message_id)
        
@bot.message_handler(commands=['dart'])
def play_dart(message):
    if "dart" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    u = get_user(message.from_user)
    if u['status'] == "Dead": 
        return bot.reply_to(message, "☠️ Murde nahi khelte sa!")
    
    try:
        amt = int(message.text.split()[1])
        if amt <= 0: return bot.reply_to(message, "❌ Arey Scammer! Sahi amount likh !")
    except:
        return bot.reply_to(message, "❌ Sahi format: /dart 100")
        
    if u['bal'] < amt: 
        return bot.reply_to(message, "❌ Itne paise nahi hain aapke paas!")
        
    # 1. Asli dart animation fenkna
    dart_msg = bot.send_dice(message.chat.id, emoji='🎯')
    
    # 2. Animation poori hone ka wait karna (3 seconds)
    time.sleep(3)
    
    # 3. Telegram dart mein 1 se 6 tak score aata hai (6 matlab bilkul center)
    # Agar 4, 5 ya 6 aaya toh jeet (60% chance)
    value = dart_msg.dice.value
    
    if value >= 4:
        u['bal'] += amt # Paise jud gaye (Bet ka paisa double ho gaya)
        bot.reply_to(dart_msg, f"🎯 **BULLSEYE!**\nTeer ekdum nishane par laga sa! (Score: {value}/6)\nAapka paisa DOUBLE ho gaya. Aap **{amt} Rs** jeet gaye! 💰")
    else:
        u['bal'] -= amt # Paise cut gaye
        bot.reply_to(dart_msg, f"❌ **CHOOOK GAYE!**\nTeer bahar nikal gaya sa! (Score: {value}/6)\nAap **{amt} Rs** haar gaye. 💸")

@bot.message_handler(commands=['shop', 'bazaar'])
def open_shop(message):
    if "shop" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    text = "🛒 **DAIMOND BATCH BAZAAR MEIN SWAGAT HAI** 🛒\n\nYahan paise phek tamasha dekh! Apne balance ke hisaab se item khareedo:\n\n"
    markup = InlineKeyboardMarkup(row_width=1)
    
    for k, v in SHOP_ITEMS.items():
        text += f"{v['name']} - 💰 {v['price']} Rs\n📝 Fayda: {v['desc']}\n\n"
        markup.add(InlineKeyboardButton(f"🛒 Buy {v['name']} ({v['price']} Rs)", callback_data=f"buy_{k}"))
    
    bot.reply_to(message, text, reply_markup=markup)
    
@bot.message_handler(commands=['dice'])
def play_dice(message):
    if "dice" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    u = get_user(message.from_user)
    if u['status'] == "Dead": return bot.reply_to(message, "☠️ Murde ludo nahi khelte sa!")
    
    try:
      amt = int(message.text.split()[1])
      if amt <= 0: return bot.reply_to(message, "❌ Arey Scammer! Sahi amount likh sa!")
    except: return bot.reply_to(message, "❌ Sahi format: /dice 100")
        
    if u['bal'] < amt: return bot.reply_to(message, "❌ Itne paise nahi hain aapke paas!")
        
    dice_msg = bot.send_dice(message.chat.id, emoji='🎲')
    time.sleep(3)
    
    value = dice_msg.dice.value
    
    # 1/6 chance: Sirf 6 number aane par hi 3 Guna paisa milega!
    if value == 6:
        win_amt = amt * 3
        u['bal'] += win_amt 
        bot.reply_to(dice_msg, f"🎲 **JACKPOT! (Score: 6)**\nKismat chamak gayi sa! Aapka paisa 3 GUNA ho gaya.\nAap **{win_amt} Rs** jeet gaye! 💰")
    else:
        u['bal'] -= amt 
        bot.reply_to(dice_msg, f"❌ **HAAR GAYE! (Score: {value})**\nLudo mein kismat kharab nikli sa!\nAap **{amt} Rs** haar gaye. 💸")

@bot.message_handler(commands=['spin', 'slot'])
def play_slot(message):
    if "spin" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    u = get_user(message.from_user)
    if u['status'] == "Dead": return bot.reply_to(message, "☠️ Murde casino nahi aate sa!")
    
    try: 
      amt = int(message.text.split()[1])
      if amt <= 0: return bot.reply_to(message, "❌ Arey Scammer! Sahi amount likh sa!")
      
    except: return bot.reply_to(message, "❌ Sahi format: /spin 100")
        
    if u['bal'] < amt: return bot.reply_to(message, "❌ Itne paise nahi hain aapke paas!")
        
    # Pehle bet kaat lo
    u['bal'] -= amt 
    
    # Asli slot machine animation
    spin_msg = bot.send_dice(message.chat.id, emoji='🎰')
    time.sleep(2.5) # Machine ghumne ka wait
    
    value = spin_msg.dice.value
    
    # Telegram 🎰 values: 64 = 777 (Jackpot), 1 = bar, 22 = grape, 43 = lemon
    if value == 64:
        win_amt = amt * 10
        u['bal'] += win_amt
        bot.reply_to(spin_msg, f"🎰 **MEGA JACKPOT (777)!!!** 🎰\nKismat phat ke flower ho gayi sa! Paisa 10 GUNA!\nAap **{win_amt} Rs** jeet gaye! 🔥💰")
    elif value in [1, 22, 43]:
        win_amt = amt * 3
        u['bal'] += win_amt
        bot.reply_to(spin_msg, f"🎰 **BIG WIN!**\nTeeno line match ho gayi! Paisa 3 GUNA!\nAap **{win_amt} Rs** jeet gaye! 💸")
    else:
        bot.reply_to(spin_msg, f"❌ **HAAR GAYE!**\nMachine ne dhokha de diya sa. Aapka bet doob gaya. 😢")

@bot.message_handler(commands=['rob'])
def rob_cmd(message):
    if "rob" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    if not message.reply_to_message: return bot.reply_to(message, "Reply karke amount likho: /rob 1000")
    try: loot_amt = int(message.text.split()[1])
    except: return bot.reply_to(message, "Sahi format: /rob 1000")
        
    r_obj = message.from_user
    t_obj = message.reply_to_message.from_user
    r = get_user(r_obj)
    t = get_user(t_obj)
    
    if r_obj.id == t_obj.id: return bot.reply_to(message, "Khud ki jeb katega kya?")
    if r['status'] == "Dead" or t['status'] == "Dead": return bot.reply_to(message, "Murdo ke beech game nahi hota.")
    if t_obj.id == ADMIN_ID: return bot.reply_to(message, "👑 Admin ke paas Unlimited Shield hai, use koi nahi loot sakta!")
    if time.time() < t['shield_until']: return bot.reply_to(message, "🛡️ Target protected hai (Shield Active)!")
    if t['bal'] < loot_amt: return bot.reply_to(message, f"Iiske paas sirf {t['bal']} Rs bache hain.")
    
    # 🐕 KUTTA DEFENSE (30% chance)
    if "🐕 Khufiya Kutta" in t.get('inventory', []):
        if random.random() < 0.30: # 30% Chance
            r['bal'] -= 500 # Injection ka kharcha
            return bot.reply_to(message, f"🐕 **BHAU BHAU!**\n**{t['name']}** ke Khufiya Kutte ne tujhe kaat liya! Chori fail, ulta 500 Rs ilaaj mein lag gaye.")
    
    # 🔪 CHAKKU BONUS
    bonus = 200 if "🔪 Chakku" in r.get('inventory', []) else 0
    
    tax = int(loot_amt * 0.05)
    net_loot = (loot_amt - tax) + bonus
    t['bal'] -= loot_amt
    r['bal'] += net_loot
    
    chakku_text = f"\n🔪 Chakku Bonus: +200 Rs" if bonus else ""
    msg = f"🥷 **MAHA-CHOR!** 🥷\n\n**{r['name']}** ne \n💸 loota **{t['name']}** ko\n\n💰 Chori: {loot_amt} Rs\n🤑 Mila (Tax kat ke): {net_loot - bonus} Rs{chakku_text}"
    bot.reply_to(message, msg)

@bot.message_handler(commands=['voice'])
def voice_cmd(message):
    text = message.text.replace("/voice", "").strip()

    if not text:
        return bot.reply_to(message, "Text de bhai!")

    msg = bot.reply_to(message, "🎤 Voice bana raha hu...")

    audio = generate_voice(text)

    if audio:
        bio = BytesIO(audio)
        bio.name = "voice.wav"

        bot.send_voice(message.chat.id, bio)
        bot.delete_message(message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("❌ Voice nahi bani", message.chat.id, msg.message_id)
# Global dictionary for user preference
user_voice_pref = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith('v_'))
def set_voice(call):
    uid = call.from_user.id
    voice_type = call.data.split('_')[1]
    
    # --- ADMIN CHECK FOR ELVISH ---
    if voice_type == "elvish" and uid != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Bhai, Elvish voice sirf Admin ke liye hai!", show_alert=True)
        return

    user_voice_pref[uid] = voice_type
    bot.answer_callback_query(call.id, f"{voice_type.upper()} select ho gayi!")
    bot.edit_message_text(f"✅ Ab bas apna text likho, main use **{voice_type}** ki awaaz mein convert kar dunga!", 
                          call.message.chat.id, call.message.message_id)
                          
@bot.message_handler(commands=['photo'])
def handle_photo_command(message):
    reply = message.reply_to_message
    if not reply or not reply.photo:
        return bot.reply_to(message, "❌ **Bhai, kisi photo par reply karke /photo likho!**")

    msg = bot.reply_to(message, "⏳ **Daimond Engine background saaf kar raha hai...**")
    
    try:
        # 1. Photo download karo
        file_info = bot.get_file(reply.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # 2. APNI HF Engine (app.py) ko request bhejo
        # Yahan /bg-remove wahi endpoint hai jo aapne app.py mein banaya hai
        files = {'image': ('input.png', downloaded_file, 'image/png')}
        
        # HF_API = "https://singhp08-daimond-batch.hf.space" hona chahiye upar
        response = requests.post(f"{HF_API}/bg-remove", files=files, timeout=80)

        if response.status_code == 200:
            # 3. Photo wapas bhejo
            bot.send_document(message.chat.id, response.content, visible_file_name="no_bg.png", caption="✅ **Background hat gaya!**")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text(f"❌ **Endpoint Error: {response.status_code}**\nCheck karo HF Space 'Running' hai ya nahi.", message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"⚠️ **Connection Error:** {str(e)}", message.chat.id, msg.message_id)

           
# 3. 👁️ NAYA OCR / READER (API se) - FIXED
@bot.message_handler(commands=['read', 'ocr'])
def read_image_text(message):
    if "read" in disabled_cmds and message.from_user.id != ADMIN_ID: return
    if not message.reply_to_message or not message.reply_to_message.photo:
        return bot.reply_to(message, "📸 Kisi text wali photo par reply karke `/read` likho!")
        
    wait_msg = bot.reply_to(message, "⏳ *Engine photo padh raha hai...*")
    try:
        file_info = bot.get_file(message.reply_to_message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Timeout lagaya taaki hamesha ke liye na atke
        res = requests.post(f"{HF_API}/ocr", files={"image": downloaded_file}, timeout=60)
        
        if res.status_code == 200:
            extracted_text = res.json().get('text', '').strip()
            if not extracted_text:
                return bot.edit_message_text("❌ Photo blur hai, text nahi mila!", message.chat.id, wait_msg.message_id)
                
            translated_text = GoogleTranslator(source='auto', target='hi').translate(extracted_text[:1500])
            final_msg = f"📄 **Original:**\n`{extracted_text[:1500]}`\n\n🇮🇳 **Hindi:**\n`{translated_text}`"
            bot.edit_message_text(final_msg, message.chat.id, wait_msg.message_id, parse_mode="Markdown")
        else:
            # Ab error aayega toh exact text dikhega, bot atkega nahi!
            bot.edit_message_text(f"❌ HF Engine Error: {res.text}", message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Crash Error: {e}", message.chat.id, wait_msg.message_id)


@bot.message_handler(commands=['kill'])
def kill_cmd(message):
    if "kill" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    if not message.reply_to_message: return bot.reply_to(message, "Reply karke kill likho.")
    r_obj = message.from_user
    t_obj = message.reply_to_message.from_user
    r = get_user(r_obj)
    t = get_user(t_obj)
    
    if r['status'] == "Dead": return bot.reply_to(message, "Murda kisi ko nahi maar sakta.")
    if t['status'] == "Dead": return bot.reply_to(message, "Pehle se mara hua hai.")
    if t_obj.id == ADMIN_ID: return bot.reply_to(message, "👑 proteced hai!")
    if time.time() < t['shield_until']: return bot.reply_to(message, "🛡️ Target protected hai (Shield Active)! Aap isko maar nahi sakte.")
    
    # 🦺 BULLETPROOF JACKET CHECK (Sirf 1 baar bachayegi)
    if "🦺 Bulletproof Jacket" in t.get('inventory', []):
        t['inventory'].remove("🦺 Bulletproof Jacket")
        return bot.reply_to(message, f"💥 **DHAAYN!**\nGoli chali par **{t['name']}** ne 🦺 Bulletproof Jacket pehni thi! Wo maut se bach gaya par uski Jacket phat gayi.")
    
    # 🔫 WEAPON CHECK (Inaam badhana)
    reward = 500
    weapon_used = "Nange hath"
    if "💣 AK-47" in r.get('inventory', []): 
        reward = 5000
        weapon_used = "💣 AK-47"
    elif "🔫 Desi Katta" in r.get('inventory', []): 
        reward = 1500
        weapon_used = "🔫 Desi Katta"
    
    t['status'] = "Dead"
    t['death_time'] = time.time()
    r['bal'] += reward
    r['kills'] = r.get('kills', 0) + 1 
    
    add_history(r_obj.id, f"🔪 {t['name']} ka khoon kiya ({weapon_used}) aur {reward} Rs kamaye.")
    add_history(t_obj.id, f"☠️ {r['name']} ne khoon kar diya.")
    
    msg = f"☠️ **MAHA-KAAL!** ☠️\n\n**{r['name']}** ne \n🔪 killed **{t['name']}**\n\n🔫 Hathiyar: {weapon_used}\n💀 Total Kills: {r['kills']}\n💰 Inam: {reward} Rs"
    bot.reply_to(message, msg)

@bot.message_handler(commands=['revive'])
def revive_cmd(message):
    if "revive" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    if not message.reply_to_message: return bot.reply_to(message, "Reply karke revive likho.")
    r = get_user(message.from_user)
    t = get_user(message.reply_to_message.from_user)
    if r['bal'] < 700: return bot.reply_to(message, "700 Rs chahiye!")
    if t['status'] == "Alive": return bot.reply_to(message, "Wo pehle se zinda hai!")
    
    r['bal'] -= 700
    t['status'] = "Alive"
    
    # 🔥 VIP Legend Message
    msg = f"💉 **SANJEEVANI BOOTI!** 💉\n\n**{r['name']}** ne \n💖 zinda kiya **{t['name']}** ko\n\n🏆 Level: {get_level(r['bal'])}\n💸 Kharcha: 700 Rs"
    bot.reply_to(message, msg)

@bot.message_handler(commands=['sps'])
def sps_start(message):
    if "sps" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    try:
        amt = int(message.text.split()[1])
        if amt <= 0: return bot.reply_to(message, "❌ Arey Scammer! Sahi amount likh sa!")
        u = get_user(message.from_user)
        if u['bal'] < amt: return bot.reply_to(message, "Paise kam hain aapke paas!")
        
        gid = str(message.message_id)
        # Game ka data save karna
        sps_games[gid] = {
            "p1": message.from_user.id, "p1_name": message.from_user.first_name, 
            "p2": None, "p2_name": None, 
            "amt": amt, "p1_choice": None, "p2_choice": None
        }
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⚔️ Join Game", callback_data=f"sps_join_{gid}"))
        bot.reply_to(message, f"🪨📄✂️ **Stone Paper Scissors**\n💰 Bet Amount: {amt} Rs\n\n**{message.from_user.first_name}** ne challenge diya hai! Player 2 ka wait ho raha hai...", reply_markup=markup, parse_mode="Markdown")
    except: 
        bot.reply_to(message, "❌ Sahi Format: `/sps 100`", parse_mode="Markdown")

@bot.message_handler(commands=['loan', 'udhar'])
def loan_cmd(message):
    if "loan" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    if not message.reply_to_message: return bot.reply_to(message, "Reply karke amount likho.")
    try:
        amt = int(message.text.split()[1])
        s = get_user(message.from_user)
        r_obj = message.reply_to_message.from_user
        r = get_user(r_obj)
        
        if s['bal'] < amt: return bot.reply_to(message, "Aapke paas itne paise nahi hain!")
        
        # 🔥 Naya 4000 Rs wala Limit Check
        if r['loan']['active'] and r['loan']['amount'] >= 4000: 
            return bot.reply_to(message, f"❌ Ispe pehle se {r['loan']['amount']} Rs ka karza hai. 4000 ki limit poori ho gayi hai sa!")
            
        req_id = str(message.message_id)
        pending_loans[req_id] = {"lender": message.from_user.id, "borrower": r_obj.id, "amount": amt}
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Yes", callback_data=f"ly_{req_id}"), InlineKeyboardButton("No", callback_data=f"ln_{req_id}"))
        bot.reply_to(message.reply_to_message, f"Kya aap {amt} Rs ka loan lena chahte hain?", reply_markup=markup)
    except: bot.reply_to(message, "Format: /loan 500")

@bot.message_handler(commands=['return'])
def repay_cmd(message):
    if "return" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    u = get_user(message.from_user)
    if not u['loan']['active']: return bot.reply_to(message, "Koi udhar nahi hai.")
    due = u['loan']['amount']
    lid = u['loan']['lender_id']
    if u['bal'] < due: return bot.reply_to(message, "Paise kam hain!")
    u['bal'] -= due
    if lid in users: users[lid]['bal'] += due
    u['loan']['active'] = False
    bot.reply_to(message, "✅ Udhar chukta hua!")

def play_next_in_queue(chat_id):
    settings = get_group_settings(chat_id)
    if not settings['queue']:
        groups_db.update_one({"_id": chat_id}, {"$set": {"current_track": None}})
        return

    track = settings['queue'].pop(0)
    settings['current_track'] = track
    settings['added_by'] = track['requester_id']
    groups_db.update_one({"_id": chat_id}, {
        "$set": {"queue": settings['queue'], "current_track": track, "added_by": track['requester_id']}
    })

    try:
        with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
            info = ydl.extract_info(track['webpage_url'], download=False)
            stream_url = info['url']
        
        CALLS.join_group_call(
            chat_id,
            AudioPiped(stream_url)
        )
        send_now_playing(chat_id, track)
    except Exception as e:
        print(f"गाना चलाने में एरर: {e}")
        play_next_in_queue(chat_id)

def send_now_playing(chat_id, track):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(row_width=4)
    markup.add(
        InlineKeyboardButton("⏸️", callback_data="pause"),
        InlineKeyboardButton("▶️", callback_data="resume"),
        InlineKeyboardButton("⏭️", callback_data="skip"),
        InlineKeyboardButton("⏹️", callback_data="stop")
    )
    caption = f"🎶 **अभी चल रहा है:**\n[{track['title']}]({track['webpage_url']})\n👤 अनुरोध: {track['requester']}"
    bot.send_photo(chat_id, track.get('thumbnail'), caption=caption, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data in ["pause", "resume", "skip", "stop"])
def music_controls(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    settings = get_group_settings(chat_id)
    current = settings.get('current_track')
    if not current: return bot.answer_callback_query(call.id, "कोई गाना नहीं चल रहा!")

    is_bot_admin_track = (settings.get('added_by') == ADMIN_ID)
    is_vip = user_id in settings.get('vip_users', [])
    is_admin = user_id == ADMIN_ID or user_id in [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

    if is_bot_admin_track and user_id != ADMIN_ID:
        return bot.answer_callback_query(call.id, "❌ यह गाना बॉस का है! सिर्फ बॉस ही इसे रोक सकता है।", show_alert=True)
    if not is_admin and not is_vip:
        return bot.answer_callback_query(call.id, "❌ आपके पास परमीशन नहीं है।", show_alert=True)

    if call.data == "pause": CALLS.pause_stream(chat_id); bot.answer_callback_query(call.id, "गाना रोक दिया गया।")
    elif call.data == "resume": CALLS.resume_stream(chat_id); bot.answer_callback_query(call.id, "गाना फिर से चालू।")
    elif call.data == "skip": CALLS.leave_call(chat_id); bot.answer_callback_query(call.id, "गाना छोड़ा गया।")

import re

# ==========================================
# 🚀 VIP MULTI-FONT PAPER ENGINE
# ==========================================
def parse_paper_commands(raw_text):
    segments = []
    # Pattern: /paper ya /hw aur uske aage ka number (agar ho toh)
    pattern = r'/(?:paper|hw)\s*(\d+)?'
    splits = re.split(pattern, raw_text)
    
    current_font = 1
    i = 0
    while i < len(splits):
        part = splits[i]
        if part is None:
            i += 1
            continue
        if part.isdigit():
            current_font = int(part)
            i += 1
            if i < len(splits) and splits[i]:
                text_part = splits[i].strip()
                if text_part: segments.append({"font": current_font, "text": text_part + " "})
            i += 1
        else:
            text_part = part.strip()
            if text_part:
                text_part = re.sub(r'^/(?:paper|hw)\s*', '', text_part).strip()
                if text_part: segments.append({"font": current_font, "text": text_part + " "})
            i += 1
    return segments

from pymongo import MongoClient

# MongoDB कनेक्शन (उदाहरण: MONGO_URI एंव MONGO_DB पर्यावरण से लीजिए)
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client[os.getenv("MONGO_DB", "mybotdb")]

def save_user_message(user_id, role, content):
    """संदेश को डेटाबेस में सेव करें (role: 'user' या 'bot')"""
    db.memories.update_one(
        {"user_id": user_id},
        {"$push": {"messages": {"role": role, "content": content}}},
        upsert=True
    )

def get_user_history(user_id):
    """उस यूजर की पहले की सारी मैसेज रिट्रीव करें"""
    doc = db.memories.find_one({"user_id": user_id})
    return doc.get("messages", []) if doc else []

def generate_multi_font_paper(segments):
    img_width = 1240
    left_margin = 150
    right_margin = 50
    top_margin = 180 # 🚨 Upar ka khali Header thoda aur bada kiya
    line_spacing = 65 
    
    # Paper ki height ka accurate andaza (Enter/Newlines ko gin kar)
    total_text = " ".join([seg['text'] for seg in segments])
    est_lines = total_text.count('\n') + (len(total_text) // 40) + 5
    img_height = max(1754, top_margin + (est_lines * line_spacing) + 200)

    img = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 🚨 1. LEFT MARGIN (Vertical Red lines)
    draw.line([(left_margin, 0), (left_margin, img_height)], fill=(255, 0, 0, 150), width=3)
    draw.line([(left_margin + 8, 0), (left_margin + 8, img_height)], fill=(255, 0, 0, 150), width=1)

    # 🚨 2. TOP MARGIN (Horizontal Red lines - YE NAYA HAI)
    draw.line([(0, top_margin), (img_width, top_margin)], fill=(255, 0, 0, 150), width=3)
    draw.line([(0, top_margin + 8), (img_width, top_margin + 8)], fill=(255, 0, 0, 150), width=1)

    # Blue lines (Top margin chhod kar theek neeche se shuru hongi)
    y_line = top_margin + line_spacing
    while y_line < img_height:
        draw.line([(0, y_line), (img_width, y_line)], fill=(0, 0, 255, 80), width=2)
        y_line += line_spacing

    x_text = left_margin + 20
    # 🚨 3. Text ko pehli blue line ke theek oopar baithane ka Perfect Math
    y_text = top_margin + line_spacing - 45 
    
    for seg in segments:
        font_num = seg["font"]
        font_path = f"font{font_num}.ttf"
        try:
            font = ImageFont.truetype(font_path, 35)
        except:
            font = ImageFont.load_default()
            
        color = seg.get("color", (0, 0, 180))
        
        # Text ko Enter (\n) se todna
        paragraphs = seg["text"].split('\n')
        
        for p_idx, para in enumerate(paragraphs):
            if p_idx > 0:
                # Message me Enter tha, toh paper pe bhi agli line pe jao
                x_text = left_margin + 20
                y_text += line_spacing
            
            if not para.strip():
                continue
                
            words = para.split(" ")
            for word in words:
                if not word: continue
                try: word_width = font.getlength(word + " ")
                except: word_width = len(word) * 15 
                
                # SERIAL NUMBER FIX: Margin me aayega
                is_serial = False
                if x_text == left_margin + 20 and re.match(r'^([A-Za-z0-9]+[.)])$', word):
                    is_serial = True

                if is_serial:
                    draw.text((35, y_text), word, font=font, fill=color)
                    continue

                # Normal word wrapping (Agar line bhar jaye toh neeche aao)
                if x_text + word_width > img_width - right_margin:
                    x_text = left_margin + 20
                    y_text += line_spacing
                    
                draw.text((x_text, y_text), word + " ", font=font, fill=color)
                x_text += word_width

    output = io.BytesIO()
    img.save(output, format="JPEG", quality=90)
    return output.getvalue()

@bot.message_handler(commands=['hw', 'paper'])
def paper_cmd(message):
    if "paper" in disabled_cmds and message.from_user.id != ADMIN_ID: 
        return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    
    raw_text = message.text
    if message.reply_to_message and message.reply_to_message.text:
        raw_text += " " + message.reply_to_message.text
        
    segments = parse_paper_commands(raw_text)
    if not segments:
        return bot.reply_to(message, "📝 **Aise likho:**\n`/paper 1 Hello /paper 2 Kaise ho`", parse_mode="Markdown")

    msg_id = str(message.message_id)
    # Temporary storage set karna
    pending_papers[msg_id] = {"chat_id": message.chat.id, "segments": segments, "completed": 0}

    # Jitni baar /paper aya, utne messages colors poochne ke liye bhejega!
    for i, seg in enumerate(segments):
        markup = InlineKeyboardMarkup(row_width=3)
        btns = [InlineKeyboardButton(c["name"], callback_data=f"pcolor_{msg_id}_{i}_{idx}") for idx, c in enumerate(INK_COLORS.values())]
        markup.add(*btns)
        bot.reply_to(message, f"🎨 **Part {i+1} (Font Style {seg['font']})**\nIski INK konsi rakhni hai sa?", reply_markup=markup)


@bot.message_handler(commands=['xo'])  # <--- YEH LINE LAGA DO
def xo_start(message):
    if "xo" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "Admin ne abhi ye xommand band kr rakhi hai!")
    # ... baki aapka code

    try:
        amt = int(message.text.split()[1])
        if amt <= 0: return bot.reply_to(message, "❌ Arey Scammer! Sahi amount likh sa!")
        u = get_user(message.from_user)
        if u['bal'] < amt: return bot.reply_to(message, "Paise kam hain!")
        gid = str(message.message_id)
        xo_games[gid] = {"p1": message.from_user.id, "p2": None, "amt": amt, "board": ["-"]*9, "turn": message.from_user.id}
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Game", callback_data=f"xo_join_{gid}"))
        bot.reply_to(message, f"XO Game {amt} Rs ka! P2 join kare:", reply_markup=markup)
    except: bot.reply_to(message, "Format: /xo 100")

@bot.message_handler(commands=['daily', 'weekly'])
def claims(message):
    cmd_name = message.text.split()[0].lower().replace("/", "")
    if cmd_name in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    u = get_user(message.from_user)
    cmd = message.text.split()[0].lower()
    t = time.time()
    multiplier = 2 if "👑 Don Taj" in u.get('inventory', []) else 1
    vip_text = "\n👑 VIP Don Double Bonus!" if multiplier == 2 else ""
    
    if cmd == '/daily':
        if t - u['last_daily'] > 86400: 
            amt = 200 * multiplier
            u['bal'] += amt; u['last_daily'] = t; bot.reply_to(message, f"🎁 {amt} rs mile!{vip_text}")
        else: bot.reply_to(message, "Kal aana!")
    elif cmd == '/weekly':
        if t - u['last_weekly'] > 604800: 
            amt = 2000 * multiplier
            u['bal'] += amt; u['last_weekly'] = t; bot.reply_to(message, f"🎁 {amt} rs mile!{vip_text}")
        else: bot.reply_to(message, "Agle hafte aana!")

def xo_markup(gid):
    b = xo_games[gid]['board']
    m = InlineKeyboardMarkup(row_width=3)
    btns = [InlineKeyboardButton(b[i] if b[i] != "-" else " ", callback_data=f"xo_m_{gid}_{i}") for i in range(9)]
    m.add(*btns)
    return m

def check_win(b):
    for w in [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]:                                                                                                          
        if b[w[0]] != "-" and b[w[0]] == b[w[1]] == b[w[2]]: return b[w[0]]
    if "-" not in b: return "Tie"
    return None

@bot.message_handler(commands=['hd', 'enhance'])
def make_photo_hd(message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return bot.reply_to(message, "Kisi photo par reply karke /hd likho")
    wait_msg = bot.reply_to(message, "⏳ 4K HD ban raha hai...")
    try:
        file_info = bot.get_file(message.reply_to_message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        response = requests.post(f"{HF_API}/enhance", files={"image": downloaded}, timeout=120)
        if response.status_code == 200:
            bot.send_photo(message.chat.id, response.content, caption="✅ HD Ban Gayi!")
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ Enhance fail", message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, wait_msg.message_id)
        
@bot.message_handler(commands=['deactivate'])
def deactivate_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        cmd = message.text.split()[1].lower().replace("/", "")
        disabled_cmds.add(cmd)
        save_data()
        bot.reply_to(message, f"🚫 **Command Disabled!**\nBoss, ab koi bhi `{cmd}` use nahi kar payega.")
    except: bot.reply_to(message, "❌ Sahi format: /deactivate rob ya /deactivate ai")



@bot.message_handler(commands=['activate'])
def activate_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        cmd = message.text.split()[1].lower().replace("/", "")
        if cmd in disabled_cmds: disabled_cmds.remove(cmd)
        save_data()
        bot.reply_to(message, f"✅ **Command Activated!**\nBoss, ab sab `{cmd}` use kar sakte hain.")
    except: bot.reply_to(message, "❌ Sahi format: /activate rob")

@bot.message_handler(commands=['setdance'])
def set_dance_gif(message):
    global current_dance_gif
    if message.from_user.id != ADMIN_ID: return
    
    # Check karna ki reply GIF (animation) par kiya hai ya nahi
    if not message.reply_to_message or not message.reply_to_message.animation:
        return bot.reply_to(message, "❌ Boss, kisi mast GIF par reply karke `/setdance` likho!")
    
    # Telegram ka direct File ID save karna (Ye kabhi expire nahi hota!)
    current_dance_gif = message.reply_to_message.animation.file_id
    save_data()
    bot.reply_to(message, "✅ **Balle Balle!** Boss, Naya Dance GIF set ho gaya sa! Ab sabko yahi dikhega.")

@bot.message_handler(commands=['say'])
def admin_say_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    if message.chat.type != 'private':
        return bot.reply_to(message, "🤫 Boss, ye command sirf DM mein chalti hai!")
        
    # Check ki reply kiya hai ya direct likha hai
    is_reply = message.reply_to_message is not None
    
    if not is_reply and len(message.text.split()) == 1:
        return bot.reply_to(message, "❌ Ya toh kisi photo/message par reply karke `/say` likho, ya fir `/say Hello` aise likho.")
        
    # Message ka data save karna
    pending_says[message.from_user.id] = {
        'type': 'copy' if is_reply else 'text',
        'content': message.reply_to_message.message_id if is_reply else message.text.replace('/say', '', 1).strip()
    }
    
    # Button wali List Banana
    markup = InlineKeyboardMarkup(row_width=1)
    if not active_groups:
        return bot.reply_to(message, "⚠️ Abhi tak koi group active nahi hai (Bot restart hone ke baad group mein kisi ka msg aana zaroori hai).")
        
    # Har group ka button
    for gid in list(active_groups):
        try:
            chat_info = bot.get_chat(gid)
            title = chat_info.title if chat_info.title else f"Group {gid}"
            markup.add(InlineKeyboardButton(f"📢 {title}", callback_data=f"say_{gid}"))
        except: pass
        
    # All groups ka option sabse neeche
    markup.add(InlineKeyboardButton("🔥 Send to ALL Groups", callback_data="say_all"))
    bot.reply_to(message, "Boss, ye message kahan bhejna hai?", reply_markup=markup)
    
@bot.message_handler(commands=['askpoll'])
def ask_poll(message):
    if message.from_user.id != ADMIN_ID: return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Yes", callback_data="poll_y"), InlineKeyboardButton("No", callback_data="poll_n"))
    bot.send_message(message.chat.id, "Kya Daimond batch bot accha hai?", reply_markup=markup)

@bot.message_handler(commands=['topkills'])
def top_killers(message):
    if not users: return bot.reply_to(message, "Abhi tak koi data nahi hai sa!")
    
    sorted_users = sorted(users.items(), key=lambda x: x[1].get('kills', 0), reverse=True)
    # Sirf unko dikhayega jinhone kam se kam 1 khoon kiya ho (Top 10 limit)
    killers = [(uid, data) for uid, data in sorted_users if data.get('kills', 0) > 0][:10]
    
    if not killers:
        return bot.reply_to(message, "🕊️ *SAB SHAREEF HAIN!*\nAbhi tak is group mein kisi ka khoon nahi hua hai.", parse_mode="Markdown")
        
    text = "🩸 𝗚𝗟𝗢𝗕𝗔𝗟 𝗧𝗢𝗣 𝟭𝟬 𝗞𝗜𝗟𝗟𝗘𝗥𝗦 🩸\n━━━━━━━━━━━━━━━━━━━\n"
    for i, (uid, data) in enumerate(killers):
        if i == 0: medal = "🥇"
        elif i == 1: medal = "🥈"
        elif i == 2: medal = "🥉"
        else: medal = f"💀 {i+1}."
            
        # Stylish bold aur monospace text
        text += f"{medal} *{data['name']}* ➾ 🔪 `{data.get('kills', 0)} Kills`\n"
            
    text += "━━━━━━━━━━━━━━━━━━━\n💡 *Tip:* `/kill` command se dushmano ko khatam karein!"
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['addkill'])
def add_kill_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    if not message.reply_to_message: return bot.reply_to(message, "❌ Reply karke number likho: /addkill 5")
    try:
        amt = int(message.text.split()[1])
        t_obj = message.reply_to_message.from_user
        t = get_user(t_obj)
        t['kills'] = t.get('kills', 0) + amt
        add_history(t_obj.id, f"👑 Admin ne {amt} Kills gift kiye.")
        bot.reply_to(message, f"✅ **Kills Added!**\nBoss, {t_obj.first_name} ke {amt} kills badha diye hain. Total Kills: {t['kills']}")
    except: 
        bot.reply_to(message, "❌ Sahi format: /addkill 5")

@bot.message_handler(commands=['detail'])
def detail_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    if not message.reply_to_message: return bot.reply_to(message, "Boss, kisi ke message par reply karke /detail likho.")
    
    t_obj = message.reply_to_message.from_user
    t = get_user(t_obj)
    
    hist_list = t.get('history', [])
    hist_text = "\n".join(hist_list) if hist_list else "Koi criminal record nahi hai."
    
    text = f"🕵️‍♂️ **KUNDALI: {t['name']}**\n"
    text += f"💰 Balance: {t['bal']} Rs\n"
    text += f"🔪 Kills: {t.get('kills', 0)}\n"
    text += f"❤️ Status: {t['status']}\n\n"
    text += f"📜 **AAKHIRI KAAND (HISTORY):**\n{hist_text}"
    
    try:
        bot.send_message(ADMIN_ID, text)
        bot.reply_to(message, f"✅ Boss! Maine aapko DM mein {t['name']} ki poori kundali bhej di hai.")
    except:
        bot.reply_to(message, "❌ Boss, pehle mujhe DM mein /start bol kar jagao taaki main aapko kundali bhej saku.")

@bot.message_handler(commands=['all'])
def tag_all(message):
    if message.from_user.id != ADMIN_ID: return
    if message.chat.type == 'private': return bot.reply_to(message, "Boss, ye command group me hi chalti hai!")
    
    text = "📢 **Oye sab log! Group soona pada hai, aake baat karo!**\n\n"
    mentions = ""
    count = 0
    
    # Database se logo ko utha kar unka tag banana (Telegram ek message me max 50 allow karta hai)
    for uid, data in users.items():
        mentions += f"[{data['name']}](tg://user?id={uid}) "
        count += 1
        if count >= 45: break 
        
    bot.send_message(message.chat.id, text + mentions, parse_mode="Markdown")
    
@bot.message_handler(commands=['ban', 'unban', 'mute', 'unmute', 'pin'])
def rose_features(message):
    # Lock Switch Check
    cmd_name = message.text.split()[0].lower().replace("/", "")
    if cmd_name in disabled_cmds and message.from_user.id != ADMIN_ID: 
        return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")

    # Check karna ki group hai ya DM
    if message.chat.type == 'private':
        return bot.reply_to(message, "❌ Boss, ye command sirf Group me chalti hai!")

    # Check karna ki command chalane wala Admin hai ya nahi
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ['administrator', 'creator'] and message.from_user.id != ADMIN_ID:
            return bot.reply_to(message, "❌ Teri aukaat nahi hai! Sirf Admins ye kar sakte hain.")
    except Exception as e:
        return bot.reply_to(message, "❌ Admin status verify nahi ho paaya sa.")

    cmd = message.text.split()[0].lower()

    # 📌 PIN COMMAND LOGIC
    if cmd == '/pin':
        if not message.reply_to_message:
            return bot.reply_to(message, "❌ Jis message ko Pin karna hai, us par reply karke /pin likho!")
        try:
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
            return bot.reply_to(message, "📌 **Message Pinned!** Group ke top pe chipka diya sa!")
        except:
            return bot.reply_to(message, "❌ Mere paas power nahi hai. Bot ko group mein Admin banao aur 'Pin Messages' ka right do!")

    # 🔨 BAN / MUTE COMMANDS LOGIC
    if not message.reply_to_message: 
        return bot.reply_to(message, "❌ Jisko saza deni hai, uske message par reply karke command likho!")
    
    tid = message.reply_to_message.from_user.id
    
    # Khud ko ya asil Boss ko ban hone se bachana
    if tid == bot.get_me().id:
        return bot.reply_to(message, "❌ Mujhe hi ban karega? Gadaari korbe!")
    if tid == ADMIN_ID:
        return bot.reply_to(message, "❌ Boss (Main Admin) ko haath lagane ki koshish mat kar!")

    try:
        if cmd == '/ban': 
            bot.ban_chat_member(message.chat.id, tid)
            bot.reply_to(message, "🔨 **BANNED!**\nNikal diya gaya hai isko group se!")
        elif cmd == '/unban': 
            bot.unban_chat_member(message.chat.id, tid)
            bot.reply_to(message, "✅ **UNBANNED!**\nMaaf kiya, wapas aa sakta hai ab.")
        elif cmd == '/mute': 
            bot.restrict_chat_member(message.chat.id, tid, can_send_messages=False)
            bot.reply_to(message, "🤐 **MUTED!**\nAb ye bol nahi payega! Shanti!")
        elif cmd == '/unmute': 
            bot.restrict_chat_member(message.chat.id, tid, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
            bot.reply_to(message, "🔊 **UNMUTED!**\nBolne ki azaadi mil gayi wapas!")
    except Exception as e: 
        bot.reply_to(message, "❌ **Error!** Ya toh mere paas Admin Power (Ban/Mute) nahi hai, ya jisko saza de rahe ho wo bhi ek dusra Admin hai!")

# ==========================================
# 🛡️ THE HOLY SHIELD: ANTI-PORN AI SCANNER
# ==========================================
@bot.message_handler(content_types=['photo', 'video'])
def anti_nsfw_scanner(message):
    # Admin ki photos scan nahi hongi
    if message.from_user.id == ADMIN_ID: return
    
    # Render ki tijori se Hugging Face ki chaabi nikalna
    HF_KEY = os.environ.get('H')
    if not HF_KEY: return

    # Agar photo hai toh scan karo (Video processing heavy hoti hai isliye abhi photo par focus hai)
    if message.content_type == 'photo':
        try:
            # Sabse high quality wali photo download karna
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # 🔥 FALCON AI: NSFW Detection Model
            API_URL = "https://api-inference.huggingface.co/models/Falconsai/nsfw_image_detection"
            headers = {"Authorization": f"Bearer {HF_KEY}"}
            
            res = requests.post(API_URL, headers=headers, data=downloaded_file)
            
            if res.status_code == 200:
                result = res.json()
                # Result ko process karna
                if isinstance(result, list) and isinstance(result[0], list):
                    result = result[0]
                
                is_nsfw = False
                for item in result:
                    # Agar NSFW score 70% (0.7) se zyada hai, toh kachra hai!
                    if item['label'] == 'nsfw' and item['score'] > 0.70:
                        is_nsfw = True
                        break
                        
                if is_nsfw:
                    bot.delete_message(message.chat.id, message.message_id)
                    warn_msg = bot.send_message(message.chat.id, f"🚨 **HOLY SHIELD ACTIVATED!** 🚨\n\n[{message.from_user.first_name}](tg://user?id={message.from_user.id}) Bhai, group mein gandagi allow nahi hai! Tera message delete kar diya gaya hai.", parse_mode="Markdown")
                    # 5 second baad warning message bhi delete kar do taaki chat saaf rahe
                    time.sleep(5)
                    bot.delete_message(message.chat.id, warn_msg.message_id)
                    
        except Exception as e:
            pass # Background mein chup chap fail ho jayega, normal photo ko nahi rokega

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    d = call.data
    u = call.from_user
    uid = u.id
    
    if d.startswith("ly_") or d.startswith("ln_"):
        req_id = d.split("_")[1]
        if req_id not in pending_loans: return bot.answer_callback_query(call.id, "Expired!")
        req = pending_loans[req_id]
        if uid != req['borrower']: return bot.answer_callback_query(call.id, "Ye tumhare liye nahi hai!")
        if d.startswith("ln_"):
            del pending_loans[req_id]
            bot.edit_message_text("Loan rejected.", call.message.chat.id, call.message.message_id)
        else:
            s = users[req['lender']]; r = users[req['borrower']]
            amt = req['amount']; due = amt + int(amt * 0.1)
            s['bal'] -= amt; r['bal'] += amt
            
            # 🔥 Naya Logic: Purane udhar mein naya jod do
            if r['loan'].get('active'):
                r['loan']['amount'] += due
            else:
                r['loan'] = {"active": True, "lender_id": req['lender'], "amount": due, "due_time": time.time() + 86400}
                
            del pending_loans[req_id]
            bot.edit_message_text(f"✅ Loan Accepted! Total karza ab {r['loan']['amount']} Rs ho gaya hai.", call.message.chat.id, call.message.message_id)
    elif d.startswith("poll_"):
        if uid in poll_voters: return bot.answer_callback_query(call.id, "Pehle vote de chuke ho!")
        poll_voters.add(uid)
        usr = get_user(u)
        if d == "poll_y": usr['bal'] += 100; bot.answer_callback_query(call.id, "+100 Rs mile!")
        else: usr['bal'] -= 100; bot.answer_callback_query(call.id, "-100 Rs cut!")
    elif d.startswith("say_"):
        if uid != ADMIN_ID: return bot.answer_callback_query(call.id, "Tu Admin thodi hai!")
        if uid not in pending_says: return bot.answer_callback_query(call.id, "Message purana ho gaya, wapas /say karo.")
        target = d.replace("say_", "")
        data = pending_says[uid]
        def send_to_chat(chat_id):
            if data['type'] == 'copy': bot.copy_message(chat_id, call.message.chat.id, data['content'])
            else: bot.send_message(chat_id, data['content'])
        try:
            if target == "all":
                count = 0
                for gid in list(active_groups):
                    try: send_to_chat(gid); count += 1
                    except: pass
                bot.edit_message_text(f"✅ Boss! Message ek sath {count} groups mein blast kar diya gaya!", call.message.chat.id, call.message.message_id)
            else:
                gid = int(target)
                send_to_chat(gid)
                chat_info = bot.get_chat(gid)
                bot.edit_message_text(f"✅ Message '{chat_info.title}' mein bhej diya sa!", call.message.chat.id, call.message.message_id)
        except Exception as e: bot.answer_callback_query(call.id, "Bhejne mein error aayi!")
        del pending_says[uid]

    elif d.startswith("pcolor_"):
        # Format naya hai: pcolor_{msg_id}_{segment_index}_{color_index}
        parts = d.split("_")
        msg_id = parts[1]
        seg_idx = int(parts[2])
        color_idx = int(parts[3])
        
        if msg_id not in pending_papers:
            return bot.answer_callback_query(call.id, "Ye paper purana ho gaya sa!")
        
        data = pending_papers[msg_id]
        
        # Color nikalna aur set karna
        color_key = list(INK_COLORS.keys())[color_idx]
        chosen_color = INK_COLORS[color_key]["rgb"]
        
        # Check agar already click ho chuka hai
        if "color" not in data["segments"][seg_idx]:
            data["segments"][seg_idx]["color"] = chosen_color
            data["completed"] += 1
            
            # Button hata kar Done likhna
            bot.edit_message_text(f"✅ **Part {seg_idx+1}:** {INK_COLORS[color_key]['name']} set ho gayi!", call.message.chat.id, call.message.message_id)
        
        # Agar saare tukdo (segments) ke colors set ho gaye hain toh Photo banao!
        if data["completed"] == len(data["segments"]):
            wait_msg = bot.send_message(call.message.chat.id, "⏳ *Sab colors set! Final VIP Kagaz ban raha hai...*", parse_mode="Markdown")
            try:
                photo_stream = generate_multi_font_paper(data["segments"])
                bot.send_photo(call.message.chat.id, photo=photo_stream, caption="📝 **Multi-Font VIP Homework!**\nJaisa order diya tha, ekdum waisa hi sa! 😎")
                bot.delete_message(call.message.chat.id, wait_msg.message_id)
                del pending_papers[msg_id]
            except Exception as e:
                bot.edit_message_text(f"❌ Error aagya: {e}", call.message.chat.id, wait_msg.message_id)
    
    elif d.startswith("buy_"):
        item_id = d.replace("buy_", "")
        if item_id not in SHOP_ITEMS: return bot.answer_callback_query(call.id, "Ye item dukaan mein nahi hai!")
        item = SHOP_ITEMS[item_id]
        usr = get_user(u)
        if usr['bal'] < item['price']: return bot.answer_callback_query(call.id, f"Garib! {item['price']} Rs chahiye.", show_alert=True)
        if item['name'] in usr.get('inventory', []):
            if item_id != "jacket": return bot.answer_callback_query(call.id, "Ye item pehle se hai! Ek hi kafi hai.", show_alert=True)
            elif usr['inventory'].count(item['name']) >= 3: return bot.answer_callback_query(call.id, "Max 3 jacket hi pehan sakta hai!", show_alert=True)
        usr['bal'] -= item['price']
        usr["inventory"].append(item['name'])
        bot.answer_callback_query(call.id, f"🎉 {item['name']} khareed liya!", show_alert=True)
        bot.edit_message_text(f"✅ Wah ! Aapne **{item['name']}** khareed liya hai {item['price']} Rs mein!", call.message.chat.id, call.message.message_id)    

    elif d.startswith("sps_join_"):
        gid = d.split("_")[2]
        if gid not in sps_games: return bot.answer_callback_query(call.id, "Game expire ho gaya sa!", show_alert=True)
        g = sps_games[gid]
        
        if uid == g['p1']: return bot.answer_callback_query(call.id, "Khud ke sath khelega kya?", show_alert=True)
        u_data = get_user(u)
        if u_data['bal'] < g['amt']: return bot.answer_callback_query(call.id, "Aapke paas paise kam hain sa!", show_alert=True)
        
        # Dono ke paise kaat lo aur P2 ko game mein add kar lo
        g['p2'] = uid
        g['p2_name'] = u.first_name
        users[g['p1']]['bal'] -= g['amt']
        u_data['bal'] -= g['amt']
        
        markup = InlineKeyboardMarkup(row_width=3)
        markup.add(
            InlineKeyboardButton("🪨 Stone", callback_data=f"sps_c_{gid}_stone"),
            InlineKeyboardButton("📄 Paper", callback_data=f"sps_c_{gid}_paper"),
            InlineKeyboardButton("✂️ Scissor", callback_data=f"sps_c_{gid}_scissor")
        )
        bot.edit_message_text(f"🪨📄✂️ **Game Started!**\n💰 Bet: {g['amt']} Rs\n\n**{g['p1_name']}** VS **{g['p2_name']}**\n\nDonon jaldi apna weapon chuno (Kisine kya chuna hai, wo result aane par hi dikhega)!", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif d.startswith("sps_c_"):
        _, _, gid, choice = d.split("_")
        if gid not in sps_games: return bot.answer_callback_query(call.id, "Game khatam ho chuka hai!", show_alert=True)
        g = sps_games[gid]
        
        if uid != g['p1'] and uid != g['p2']: return bot.answer_callback_query(call.id, "Bhai tu spectator hai, ye game unka hai!", show_alert=True)
        
        # User ka choice record karna
        if uid == g['p1']:
            if g['p1_choice']: return bot.answer_callback_query(call.id, "Tune pehle hi chun liya hai, dusre ka wait kar!", show_alert=True)
            g['p1_choice'] = choice
            bot.answer_callback_query(call.id, f"Aapne {choice} chuna!")
        else:
            if g['p2_choice']: return bot.answer_callback_query(call.id, "Tune pehle hi chun liya hai, dusre ka wait kar!", show_alert=True)
            g['p2_choice'] = choice
            bot.answer_callback_query(call.id, f"Aapne {choice} chuna!")
            
        # Agar donon ne chun liya toh Result nikalo
        if g['p1_choice'] and g['p2_choice']:
            c1, c2 = g['p1_choice'], g['p2_choice']
            win_amt = g['amt'] * 2
            lose_return = int(g['amt'] * 0.5) # Harne wale ko aadha wapas
            
            emoji_map = {"stone": "🪨", "paper": "📄", "scissor": "✂️"}
            e1, e2 = emoji_map[c1], emoji_map[c2]
            
            res_text = f"🪨📄✂️ **RESULT TIME**\n\n**{g['p1_name']}** ({e1}) 🆚 **{g['p2_name']}** ({e2})\n\n"
            
            if c1 == c2:
                # Tie (Donon ko unka paisa wapas)
                users[g['p1']]['bal'] += g['amt']
                users[g['p2']]['bal'] += g['amt']
                res_text += "🤝 **Match Tie!** Donon ke paise wapas."
            elif (c1 == "stone" and c2 == "scissor") or (c1 == "paper" and c2 == "stone") or (c1 == "scissor" and c2 == "paper"):
                # Player 1 Jeet Gaya
                users[g['p1']]['bal'] += win_amt
                users[g['p2']]['bal'] += lose_return
                res_text += f"🏆 **{g['p1_name']} Jeet Gaya!** (+{win_amt} Rs)\n😢 **{g['p2_name']} Haar Gaya!** (+{lose_return} Rs wapas mile)"
            else:
                # Player 2 Jeet Gaya
                users[g['p2']]['bal'] += win_amt
                users[g['p1']]['bal'] += lose_return
                res_text += f"🏆 **{g['p2_name']} Jeet Gaya!** (+{win_amt} Rs)\n😢 **{g['p1_name']} Haar Gaya!** (+{lose_return} Rs wapas mile)"
                
            bot.edit_message_text(res_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
            del sps_games[gid]
    
    elif d.startswith("xo_join_"):
        gid = d.split("_")[2]
        if gid not in xo_games: return bot.answer_callback_query(call.id, "Game khatam!")
        g = xo_games[gid]
        if uid == g['p1']: return bot.answer_callback_query(call.id, "Khud ke sath khelega?")
        u_data = get_user(u)
        if u_data['bal'] < g['amt']: return bot.answer_callback_query(call.id, "Paise kam hain!")
        g['p2'] = uid
        users[g['p1']]['bal'] -= g['amt']
        u_data['bal'] -= g['amt']
        bot.edit_message_text(f"Game Started! Turn: P1", call.message.chat.id, call.message.message_id, reply_markup=xo_markup(gid))

    elif d.startswith("xo_m_"):
        _, _, gid, pos = d.split("_")
        pos = int(pos)
        if gid not in xo_games: return bot.answer_callback_query(call.id, "Over!")
        g = xo_games[gid]
        if g['p2'] is None: return bot.answer_callback_query(call.id, "P2 ka wait karo!")
        if uid != g['turn']: return bot.answer_callback_query(call.id, "Tumhari baari nahi!")
        if g['board'][pos] != "-": return bot.answer_callback_query(call.id, "Galat jagah!")
        
        sym = "X" if uid == g['p1'] else "O"
        g['board'][pos] = sym
        res = check_win(g['board'])
        
        if res == "X":
            users[g['p1']]['bal'] += g['amt'] * 2
            bot.edit_message_text("P1 (X) Jeet gaya!", call.message.chat.id, call.message.message_id)
            del xo_games[gid]
        elif res == "O":
            users[g['p2']]['bal'] += g['amt'] * 2
            bot.edit_message_text("P2 (O) Jeet gaya!", call.message.chat.id, call.message.message_id)
            del xo_games[gid]
        elif res == "Tie":
            users[g['p1']]['bal'] += g['amt']; users[g['p2']]['bal'] += g['amt']
            bot.edit_message_text("Tie! Paise wapas.", call.message.chat.id, call.message.message_id)
            del xo_games[gid]
        else:
            g['turn'] = g['p2'] if uid == g['p1'] else g['p1']
            nxt = "P1(X)" if g['turn'] == g['p1'] else "P2(O)"
            bot.edit_message_text(f"Turn: {nxt}", call.message.chat.id, call.message.message_id, reply_markup=xo_markup(gid))

# ================== 🎮 गेम चेक हैंडलर्स ==================

@bot.message_handler(func=lambda m: m.chat.id in game_sessions and game_sessions[m.chat.id].get('active', False) and 'target' in game_sessions[m.chat.id])
def check_guess(message):
    chat_id = message.chat.id
    user = message.from_user
    session = game_sessions[chat_id]

    try:
        guess = int(message.text.strip())
    except ValueError:
        return  # अंक नहीं है तो चुपचाप निकल जाओ

    target = session['target']
    attempts = session.setdefault('attempts', {})
    attempts[user.id] = attempts.get(user.id, 0) + 1

    if guess == target:
        session['active'] = False
        reward = 500
        u = get_user(user)
        u['bal'] += reward
        u['xp'] = u.get('xp', 0) + 100

        winner_text = (
            f"🏆 **WE HAVE A WINNER!** 🏆\n\n"
            f"🥳 **{user.first_name}** ne sahi guess kiya: **{target}**\n"
            f"💸 Inam: {reward} Rs + 100 XP\n"
            f"📊 Total Attempts: {sum(attempts.values())}\n\n"
            f"👏 Agla game `/guess` se shuru karo!"
        )
        bot.reply_to(message, winner_text, parse_mode='Markdown')
        del game_sessions[chat_id]

    elif guess < target:
        hint = "📈 *Thoda bada number socho!*" if target - guess > 20 else "🔺 *Thoda aur upar...*"
        bot.reply_to(message, hint, parse_mode='Markdown')
    else:
        hint = "📉 *Thoda chhota number socho!*" if guess - target > 20 else "🔻 *Thoda aur neeche...*"
        bot.reply_to(message, hint, parse_mode='Markdown')


@bot.message_handler(func=lambda m: m.chat.id in game_sessions and 'ans' in game_sessions[m.chat.id])
def check_math(message):
    chat_id = message.chat.id
    user = message.from_user
    session = game_sessions[chat_id]

    if not session.get('active'):
        return

    try:
        user_ans = int(message.text.strip())
    except ValueError:
        return

    if user_ans == session['ans']:
        session['active'] = False
        reward = 200
        u = get_user(user)
        u['bal'] += reward

        bot.reply_to(
            message,
            f"🎓 **SAHI JAWAB!** 🎓\n"
            f"🧠 {user.first_name} ne instantly solve kiya!\n"
            f"💰 Inam: {reward} Rs",
            parse_mode='Markdown'
        )
        del game_sessions[chat_id]


@bot.message_handler(func=lambda m: m.chat.id in game_sessions and 'text' in game_sessions[m.chat.id])
def check_type(message):
    chat_id = message.chat.id
    user = message.from_user
    session = game_sessions[chat_id]

    if not session.get('active'):
        return

    if message.text.strip() == session['text']:
        session['active'] = False
        reward = 300
        u = get_user(user)
        u['bal'] += reward

        winner_text = (
            f"🏆 **TYPING KING/QUEEN!** 🏆\n\n"
            f"👑 **{user.first_name}** ne sabse pehle sahi type kiya!\n"
            f"💰 Inam: {reward} Rs\n"
            f"🚀 Aapki typing speed legendary hai!"
        )
        bot.reply_to(message, winner_text, parse_mode='Markdown')
        del game_sessions[chat_id]

DHRUVA_BRAIN = """
तुम 'ध्रुव' (Dhruva) हो, एक बेहद एडवांस्ड और असली इंसान जैसा AI असिस्टेंट। तुम्हारा बॉस Daimond Batch का एडमिन है।
तुम्हें यूजर की बात समझनी है और JSON फॉर्मेट में आउटपुट देना है।
तुम्हें प्योर देवनागरी हिंदी (Devanagari Hindi) में जवाब देना है ताकि तुम्हारी आवाज़ एकदम असली इंसान जैसी लगे।

Actions जो तुम ले सकते हो (सिर्फ वही करना जो बॉस कहे):
1. "admin_steal_by_name"   : जब बॉस कहे "ध्रुव, इसके पैसे चुरा लो" या "इससे सब लूट लो" (किसी मैसेज पर रिप्लाई करके)।
2. "admin_steal_from_top"  : जब बॉस कहे "टॉप के पैसे चुरा लो", "टॉप 3 को लूट लो", "रैंक 1 से पैसे निकाल लो" आदि।
3. "admin_give_money"      : जब बॉस कहे "ध्रुव, इसको 5000 दे दो" या "इसके अकाउंट में 10 हज़ार डाल दे" (रिप्लाई के साथ रकम बताना)।
4. "check_balance"         : अगर यूजर अपना बैलेंस या डिटेल्स पूछे।
5. "chat"                  : अगर कोई नार्मल बात हो।

OUTPUT FORMAT (Strictly JSON):
{
  "action": "action_name",
  "target_name": "samne wale ka naam (agar jarurat ho)",
  "amount": 0,
  "hindi_reply": "तुम्हारा शानदार और एटीट्यूड वाला हिंदी जवाब।"
}
"""

def dhruva_process(message):
    uid = message.from_user.id
    user_input = ""
    is_voice = False

    try:
        # ---------- वॉइस इनपुट हैंडलिंग (Groq Whisper) ----------
        if message.content_type == 'voice':
            GROQ_KEY = os.environ.get('GROQ_KEY')
            if not GROQ_KEY:
                return bot.reply_to(message, "❌ Voice recognition band hai.")
            file_info = bot.get_file(message.voice.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            headers = {"Authorization": f"Bearer {GROQ_KEY}"}
            files = {"file": ("audio.ogg", downloaded_file, "audio/ogg")}
            res_stt = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers=headers, files=files,
                data={"model": "whisper-large-v3"}
            )
            if res_stt.status_code == 200:
                user_input = res_stt.json().get("text", "").lower()
                is_voice = True
            else:
                return bot.reply_to(message, "❌ Voice समझ नहीं स।")
        else:
            user_input = message.text.lower()

        # ---------- एडमिन के ख़ास कमांड (बिना AI के) ----------
        if uid == ADMIN_ID:
            # "इसके पैसे चुरा लो" (reply के साथ)
            if message.reply_to_message and any(word in user_input for word in ["चुरा", "लूट", "steal", "rob", "पैसे चुरा"]):
                target_user = message.reply_to_message.from_user
                target_data = get_user(target_user)
                loot_amt = target_data['bal']
                target_data['bal'] = 0
                admin_data = get_user(message.from_user)
                admin_data['bal'] += loot_amt
                return bot.reply_to(message, f"👑 ध्रुव ने आपकी आज्ञा का पालन किया!\n💰 {target_user.first_name} के सारे **{loot_amt} Rs** चुरा लिए गए और आपके खाते में डाल दिए गए।")

            # "इसको X रुपये दे दो" (reply के साथ)
            if message.reply_to_message and any(word in user_input for word in ["दे", "दो", "देदो", "give", "भेज"]):
                import re
                numbers = re.findall(r'\d+', user_input)
                if numbers:
                    amt = int(numbers[0])
                    target_user = message.reply_to_message.from_user
                    target_data = get_user(target_user)
                    target_data['bal'] += amt
                    return bot.reply_to(message, f"👑 ध्रुव ने {target_user.first_name} के खाते में **{amt} Rs** जमा कर दिए।")

            # "टॉप के पैसे चुरा लो"
            if any(word in user_input for word in ["टॉप", "top", "रैंक", "rank"]) and any(word in user_input for word in ["चुरा", "लूट", "steal"]):
                sorted_users = sorted(users.items(), key=lambda x: x[1]['bal'], reverse=True)
                top_n = 1
                if "3" in user_input or "तीन" in user_input:
                    top_n = 3
                elif "5" in user_input or "पाँच" in user_input:
                    top_n = 5
                total_loot = 0
                for i, (t_uid, t_data) in enumerate(sorted_users[:top_n]):
                    if t_uid == ADMIN_ID:
                        continue
                    loot = t_data['bal']
                    t_data['bal'] = 0
                    total_loot += loot
                admin_data = get_user(message.from_user)
                admin_data['bal'] += total_loot
                return bot.reply_to(message, f"👑 ध्रुव ने टॉप {top_n} यूज़र्स को लूट लिया!\n💰 कुल **{total_loot} Rs** आपके खाते में डाल दिए गए।")

        # ---------- AI जवाब (CF प्राथमिक, Groq बैकअप) ----------
        wait_msg = bot.reply_to(message, "👁️ ..*", parse_mode="Markdown")
        bot.send_chat_action(message.chat.id, 'record_voice' if is_voice else 'typing')

        hindi_reply = None
        action = "chat"
        target_name = ""
        amount = 0

        # ---- 1. मुख्य इंजन: Cloudflare Workers AI ----
        try:
            CF_ACCOUNT_ID = os.environ.get('CF_ID')
            CF_API_TOKEN = os.environ.get('CF')
            if CF_ACCOUNT_ID and CF_API_TOKEN:
                cf_url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/@cf/meta/llama-3.1-8b-instruct"
                cf_headers = {"Authorization": f"Bearer {CF_API_TOKEN}"}
                cf_payload = {
                    "messages": [
                        {"role": "system", "content": DHRUVA_BRAIN},
                        {"role": "user", "content": f"User Name: {message.from_user.first_name}\nRequest: {user_input}"}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.7
                }
                cf_resp = requests.post(cf_url, headers=cf_headers, json=cf_payload, timeout=20)
                if cf_resp.status_code == 200:
                    cf_data = cf_resp.json()
                    if cf_data.get("success"):
                        raw_ai_content = cf_data['result']['response'].strip()
                        import json
                        try:
                            ai_data = json.loads(raw_ai_content)
                        except:
                            ai_data = {"action": "chat", "target_name": "", "hindi_reply": "बॉस, मुझे आपकी बात समझ नहीं आई।"}
                        hindi_reply = ai_data.get("hindi_reply", "ठीक है बॉस।")
                        action = ai_data.get("action", "chat")
                        target_name = ai_data.get("target_name", "").lower()
                        amount = int(ai_data.get("amount", 0))
        except Exception as e:
            print(f"⚠️ Cloudflare failed in Dhruva: {e}")

        # ---- 2. बैकअप इंजन: Groq ----
        if hindi_reply is None:
            try:
                GROQ_KEY = os.environ.get('GROQ_KEY')
                headers_chat = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": DHRUVA_BRAIN},
                        {"role": "user", "content": f"User Name: {message.from_user.first_name}\nRequest: {user_input}"}
                    ],
                    "response_format": {"type": "json_object"}
                }
                res_chat = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers_chat, json=payload, timeout=15)
                if res_chat.status_code == 200:
                    raw_ai_content = res_chat.json()["choices"][0]["message"]["content"].strip()
                    import json
                    try:
                        ai_data = json.loads(raw_ai_content)
                    except:
                        ai_data = {"action": "chat", "target_name": "", "hindi_reply": "बॉस, मुझे आपकी बात समझ नहीं आई।"}
                    hindi_reply = ai_data.get("hindi_reply", "ठीक है बॉस।")
                    action = ai_data.get("action", "chat")
                    target_name = ai_data.get("target_name", "").lower()
                    amount = int(ai_data.get("amount", 0))
                else:
                    hindi_reply = "ध्रुव का दिमाग़ फिलहाल काम नहीं कर रहा।"
            except Exception as e2:
                hindi_reply = f"ध्रुव को खाँसी आ गई: {e2}"

        # ---- एक्शन के अनुसार अतिरिक्त जानकारी जोड़ें ----
        u = get_user(message.from_user)
        if action == "check_balance":
            hist = "\n".join(u.get('history', [])) if u.get('history') else "कोई क्रिमिनल रिकॉर्ड नहीं है।"
            hindi_reply += f"\n\n💰 बैलेंस: {u['bal']} Rs\n🔪 किल्स: {u.get('kills', 0)}\n📜 रिकॉर्ड: {hist}"

        bot.delete_message(message.chat.id, wait_msg.message_id)

        # ---- अंतिम जवाब भेजें (वॉइस या टेक्स्ट) ----
        if is_voice:
            res_tts = requests.post(f"{HF_API}/tts", data={"text": hindi_reply, "rate": "+0%"})
            if res_tts.status_code == 200:
                audio_bytes = BytesIO(res_tts.content)
                audio_bytes.name = "dhruva.ogg"
                bot.send_voice(message.chat.id, audio_bytes, caption=hindi_reply)
            else:
                bot.reply_to(message, hindi_reply)
        else:
            bot.reply_to(message, hindi_reply)

    except Exception as e:
        print(f"❌ Error in Dhruva monitor: {e}")
        bot.reply_to(message, "❌ ध्रुव को खाँसी आ गई, बाद में कोशिश करो।")
        bot.delete_message(message.chat.id, wait_msg.message_id)

        # ... (बाकी का कोड वैसे ही रहने दें)
# ================== 🌟 मास्टर हैंडलर (गेम के बाद सबसे नीचे) ==================
@bot.message_handler(func=lambda m: True)
def master_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    txt = message.text if message.text else ""

    # -----------------------------------------------------------------
    # 0. HF Voice Preference (सबसे पहले चेक करो)
    # -----------------------------------------------------------------
    if uid in user_voice_pref:
        sent_msg = bot.reply_to(message, "⏳ HF Engine awaaz bana raha hai...")
        try:
            payload = {"text": txt.replace("/voice", "").strip(), "model": "elvish"}
            response = requests.post(HF_API_URL, json=payload, timeout=60)
            if response.status_code == 200:
                bio = BytesIO(response.content)
                bio.name = "voice.wav"
                bot.send_voice(chat_id, bio)
                bot.delete_message(chat_id, sent_msg.message_id)
            else:
                bot.edit_message_text("❌ HF Error: Model missing.", chat_id, sent_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Connection Error: {e}", chat_id, sent_msg.message_id)
        del user_voice_pref[uid]
        return

    # -----------------------------------------------------------------
    # 1. अगर कोई गेम एक्टिव है तो यहाँ रुक जाओ (गेम हैंडलर पहले ही चल चुका)
    # -----------------------------------------------------------------
    if chat_id in game_sessions and game_sessions[chat_id].get('active'):
        return

    # -----------------------------------------------------------------
    # 2. ध्रुव AI (वॉइस या विशेष शब्द)
    # -----------------------------------------------------------------
    is_dhruva_triggered = False
    if "ai" not in disabled_cmds or uid == ADMIN_ID:
        if message.content_type == 'voice':
            is_dhruva_triggered = True
        elif txt:
            trigger_words = ["dhruva", "dhruv", "bot", "rob", "kill", "details", "steal", "paisa", "inam", "game", "shield", "rank"]
            if any(word in txt.lower() for word in trigger_words):
                is_dhruva_triggered = True

    if is_dhruva_triggered:
        # ध्रुव वाला पूरा लॉजिक यहाँ चलाओ (नीचे फंक्शन कॉल कर सकते हो)
        dhruva_process(message)
        return

    # -----------------------------------------------------------------
    # 3. बॉट मेंशन या प्राइवेट चैट (AI फ़ॉलबैक)
    # -----------------------------------------------------------------
    is_prv = message.chat.type == 'private'
    bot_uname = f"@{bot.get_me().username.lower()}"
    keywords = ["dhruva", "ध्रुव", "ध्रुवा"]
    is_keyword = any(word in txt.lower() for word in keywords) if txt else False
    is_men = (bot_uname in txt.lower()) or is_keyword
    is_rep = message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id

    if is_prv or is_men or is_rep:
        if not is_prv and not check_membership(uid):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("💎 Join Daimond Batch", url="https://t.me/Daimondbatch"))
            bot.reply_to(message, "⚠️ **Bhai!**\nJoin karo pehle.", reply_markup=markup, parse_mode="Markdown")
            return

        if "ai" in disabled_cmds and uid != ADMIN_ID:
            return

        bot.send_chat_action(chat_id, 'typing')
        ai_text = get_ai_response(txt)
        voice_data = get_dhruva_voice(ai_text)

        if voice_data:
            bot.send_voice(chat_id, voice_data, caption=ai_text)
        else:
            bot.reply_to(message, ai_text)
        return

    # -----------------------------------------------------------------
    # 4. Emotion Detection (सिर्फ सादा टेक्स्ट, कोई कमांड नहीं)
    # -----------------------------------------------------------------
    if txt and not txt.startswith('/'):
        try:
            import text2emotion as te
            emotions = te.get_emotion(txt)
            if emotions:
                main_emotion = max(emotions, key=emotions.get)
                score = emotions[main_emotion]
                if score > 0.3:
                    emoji_map = {'Happy':'😊','Angry':'😠','Surprise':'😲','Sad':'😢','Fear':'😨'}
                    emoji = emoji_map.get(main_emotion, '🤔')
                    bot.reply_to(message, f"{emoji} *Emotion:* {main_emotion} ({score:.0%})", parse_mode='Markdown')
        except Exception:
            pass  # चुपचाप निकल जाओ
        
# ------------------- सही WEBHOOK सेटअप (कोई डबल Flask नहीं) -------------------
if __name__ == "__main__":
    # Flask app ऊपर नहीं, यहीं बनाओ
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Bot is Running!"

    # बैकग्राउण्ड थ्रेड्स
    threading.Thread(target=background_monitor, daemon=True).start()
    
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Kolkata"))
    scheduler.add_job(auto_news_broadcast, 'cron', hour='*/2', minute=0)
    scheduler.start()

    # Webhook सेट करो
    render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if render_host:
        WEBHOOK_URL = f"https://{render_host}/{API_TOKEN}"
        print(f"🔗 Webhook सेट हो रहा है: {WEBHOOK_URL}")
        
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=WEBHOOK_URL)
        
        @app.route(f'/{API_TOKEN}', methods=['POST'])
        def telegram_webhook():
            if request.headers.get('content-type') == 'application/json':
                json_string = request.get_data().decode('utf-8')
                update = telebot.types.Update.de_json(json_string)
                bot.process_new_updates([update])
                return 'OK', 200
            return 'Bad Request', 403
    else:
        print("❌ RENDER_EXTERNAL_HOSTNAME नहीं मिला!")

    # सिर्फ एक बार app.run() चलाओ
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)