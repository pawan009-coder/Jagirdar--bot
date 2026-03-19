import telebot
from telebot.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
import re
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import time
import random
import requests
import os
from flask import Flask
import threading
import urllib.parse
import pymongo 

# Flask Server Setup (Render ke liye zaroori)
app = Flask('')
@app.route('/')
def home(): return "your friend daimond batch bot is here!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive(): threading.Thread(target=run).start()

# 🔐 SECURE KEYS (Ab sab Render ki tijori / Environment Variables se aayega)
API_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_KEY')
MONGO_URL = os.environ.get('MONGO_URL')

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

# Bot Initialization
bot = telebot.TeleBot(API_TOKEN)

API_TOKEN = os.environ.get('TELEGRAM_TOKEN')
# Groq hata kar wapas Gemini ki chaabi lagao
GEMINI_API_KEY = os.environ.get('GEMINI_KEY')
ADMIN_ID = 7574760011 
GROUP_USERNAME = "@Daimondbatch" 
bot = telebot.TeleBot(API_TOKEN)

bot.set_my_commands([
    BotCommand("start", "Bot chalu karein"),
    BotCommand("bal", "Apna khaata aur level dekhein"),
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
poll_voters = set()
pending_says = {}
pending_papers = {}

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
    try:
        # Render ki tijori se Groq ki chaabi nikalna
        GROQ_API_KEY = os.environ.get('GROQ_KEY')
        
        if not GROQ_API_KEY:
            return "Bhai meri Groq ki chaabi gum ho gayi hai, Render par check kar!"

        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Insaan banne ki training aur user ka text
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system", 
                    "content": "tera naam Daimond batch bot hai. aur tera behaviuor friendly hai. Hamesha sirf 1 ya 2 line mein chota aur Hinglish main jawab dena. kabhi jarurat ho toh hi bada msg bhejna tum bhut samajdaar ho toh msg bhi samjadari se karte ho ."
                },
                {
                    "role": "user", 
                    "content": user_text
                }
            ],
            "max_tokens": 150 
        }
        
        # Request bhejna (Groq 1-2 second mein hi jawab de deta hai)
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        res_json = res.json()
        
        if res.status_code == 200:
            return res_json["choices"][0]["message"]["content"].strip()
        else:
            return f"Error aagya sa: {res_json.get('error', {}).get('message', 'Unknown')}"
            
    except Exception as e: 
        return "Bhai thoda network ka lafda hai, wapas bol."
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
    get_user(message.from_user)
    
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
    
    # DM (Akele) aur Group ke liye alag-alag VIP message
    if message.chat.type == 'private':
        text = "👑 **welcome my Dear!**\nDaimond Batch Bot mein aapka swagat hai .\n\nNeeche button daba kar hamara official group join karein 👇"
        bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")
    else:
        text = f"👑 **Daimond Batch mein swagat hai {message.from_user.first_name}!**\n\nAap toh pehle se hamare khaas aadmi ho. Game khelo aur balance badhao!\n(Apne dosto ko lana ho toh neeche wala button bhejo aur khud bhi join ho jao group main 👇)"
        bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")

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

@bot.message_handler(commands=['imagine', 'photo'])
def generate_image(message):
    if "imagine" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    
    prompt = message.text.replace("/imagine", "").replace("/photo", "").strip()
    if not prompt:
        return bot.reply_to(message, "🎨 **Aise likho:**\n`/imagine ek udta hua ghoda`", parse_mode="Markdown")
    
    # ⏳ User ko wait karne ka message
    wait_msg = bot.reply_to(message, "⏳ *Jadoo ho raha hai... 10-15 second wait karo!*", parse_mode="Markdown")
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    safe_prompt = urllib.parse.quote(prompt)
    seed = random.randint(1, 1000000)
    
    # Naya aur fast API link
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
    
    try:
        # Telegram ko direct URL de do, wo khud download kar lega (100% fast aur safe)
        bot.send_photo(message.chat.id, photo=image_url, caption=f"🎨 **Yeh lijiye aapki photo!**\n📝 Prompt: {prompt}")
        bot.delete_message(message.chat.id, wait_msg.message_id) # Wait wala message hata do
    except Exception as e:
        # Agar URL se fail ho jaye toh purana Jugaad (Download karke bhejna)
        try:
            res = requests.get(image_url, timeout=30)
            if res.status_code == 200:
                bot.send_photo(message.chat.id, photo=res.content, caption=f"🎨 **Yeh lijiye aapki photo!**\n📝 Prompt: {prompt}")
                bot.delete_message(message.chat.id, wait_msg.message_id)
            else:
                bot.edit_message_text("❌ Server thoda aalsi ho gaya hai. Ek baar wapas likho sa!", message.chat.id, wait_msg.message_id)
        except Exception as e2:
            bot.edit_message_text("❌ Photo banne mein thodi dikkat hui. Prompt thoda chota ya alag likh kar dekho sa!", message.chat.id, wait_msg.message_id)

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

# 📜 GRAND LEGEND FEATURE: REALISTIC PAPER
FONT_MAPPING = {
    "1": "font1", "2": "font2", "3": "font3", "4": "font4", "5": "font5",
    "6": "font6", "7": "font7", "8": "font8", "9": "font1", "10": "font2"
}

from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import os
import requests

# 📜 GRAND LEGEND FEATURE: 30 VIP FONTS (KHUD KA REALISTIC PAPER)
FONTS_URL = {
    # 🔥 TOP 10: Ekdum 100% Asli aur Realistic Handwriting
    "1": "https://github.com/google/fonts/raw/main/ofl/caveat/Caveat-Regular.ttf", # Default: Perfect Pen Handwriting
    "2": "https://github.com/google/fonts/raw/main/ofl/patrickhand/PatrickHand-Regular.ttf", # Saaf aur natural
    "3": "https://github.com/google/fonts/raw/main/ofl/shadowsintolight/ShadowsIntoLight-Regular.ttf", # Thodi patli aur stylish
    "4": "https://github.com/google/fonts/raw/main/ofl/gochihand/GochiHand-Regular.ttf", # Teenager writing
    "5": "https://github.com/google/fonts/raw/main/ofl/indieflower/IndieFlower-Regular.ttf", # Bubbly aur cute
    "6": "https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Regular.ttf", # Desi/Indian style handwriting
    "7": "https://github.com/google/fonts/raw/main/ofl/reeniebeanie/ReenieBeanie.ttf", # Fast aur ghasit ke likhi hui
    "8": "https://github.com/google/fonts/raw/main/ofl/justanotherhand/JustAnotherHand-Regular.ttf", # Patli ink wali
    "9": "https://github.com/google/fonts/raw/main/ofl/mansalva/Mansalva-Regular.ttf", # Asli Doctor ki writing 🩺
    "10": "https://github.com/google/fonts/raw/main/ofl/nanumpenscript/NanumPenScript-Regular.ttf", # Gel pen se likhi hui
    
    # ✒️ 11-20: VIP Cursive, Signatures aur Calligraphy
    "11": "https://github.com/google/fonts/raw/main/ofl/dancingscript/DancingScript-Regular.ttf",
    "12": "https://github.com/google/fonts/raw/main/ofl/pacifico/Pacifico-Regular.ttf",
    "13": "https://github.com/google/fonts/raw/main/ofl/sacramento/Sacramento-Regular.ttf",
    "14": "https://github.com/google/fonts/raw/main/ofl/greatvibes/GreatVibes-Regular.ttf",
    "15": "https://github.com/google/fonts/raw/main/ofl/parisienne/Parisienne-Regular.ttf",
    "16": "https://github.com/google/fonts/raw/main/ofl/allura/Allura-Regular.ttf",
    "17": "https://github.com/google/fonts/raw/main/ofl/alexbrush/AlexBrush-Regular.ttf",
    "18": "https://github.com/google/fonts/raw/main/ofl/cookie/Cookie-Regular.ttf",
    "19": "https://github.com/google/fonts/raw/main/ofl/rochester/Rochester-Regular.ttf",
    "20": "https://github.com/google/fonts/raw/main/ofl/satisfy/Satisfy-Regular.ttf",

    # 🖌️ 21-30: Aesthetic, Marker, aur Clean Print
    "21": "https://github.com/google/fonts/raw/main/ofl/architectsdaughter/ArchitectsDaughter-Regular.ttf",
    "22": "https://github.com/google/fonts/raw/main/ofl/handlee/Handlee-Regular.ttf",
    "23": "https://github.com/google/fonts/raw/main/ofl/amaticsc/AmaticSC-Regular.ttf",
    "24": "https://github.com/google/fonts/raw/main/apache/permanentmarker/PermanentMarker-Regular.ttf", # Mota Marker
    "25": "https://github.com/google/fonts/raw/main/apache/rocksalt/RockSalt-Regular.ttf",
    "26": "https://github.com/google/fonts/raw/main/ofl/coveredbyyourgrace/CoveredByYourGrace.ttf",
    "27": "https://github.com/google/fonts/raw/main/ofl/gloriahallelujah/GloriaHallelujah.ttf",
    "28": "https://github.com/google/fonts/raw/main/apache/walterturncoat/WalterTurncoat-Regular.ttf",
    "29": "https://github.com/google/fonts/raw/main/ofl/neucha/Neucha-Regular.ttf",
    "30": "https://github.com/google/fonts/raw/main/ofl/badscript/BadScript-Regular.ttf"
}

if not os.path.exists('assets'):
    os.makedirs('assets')



    # Text ko kagaz par set karna
    lines = textwrap.wrap(text, width=35) 
    y_text = 100 - 45 
    
    for line in lines:
        draw.text((120, y_text), line, font=font, fill=(0, 0, 150)) # Blue ink
        y_text += line_spacing

    bio = io.BytesIO()
    bio.name = 'paper.jpg'
    img.save(bio, 'JPEG')
    bio.seek(0)
    return bio

@bot.message_handler(commands=['paper'])
def generate_paper(message):
    if "paper" in disabled_cmds and message.from_user.id != ADMIN_ID: 
        return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    
    parts = message.text.split(maxsplit=2)
    user_text = ""
    style = "1" # Default Realistic Handwriting
    
    if message.reply_to_message and message.reply_to_message.text:
        user_text = message.reply_to_message.text
        if len(parts) > 1 and parts[1].isdigit(): style = parts[1]
    else:
        if len(parts) > 1:
            if parts[1].isdigit(): 
                style = parts[1]
                if len(parts) > 2: user_text = parts[2]
            else: user_text = message.text.replace("/paper", "").strip()

    if not user_text:
        return bot.reply_to(message, "📝 **Aise likho:**\n`/paper text` ya `/paper 30 text`\n(1 se 30 tak koi bhi writing style chuno!)", parse_mode="Markdown")

    wait_msg = bot.reply_to(message, f"⏳ *Kagaz pe blue ink se likh raha hu (Style #{style})... 2 second ruk sa!*", parse_mode="Markdown")
    bot.send_chat_action(message.chatdef parse_paper_text(raw_text):
    # Multi-command ko todne ka logic
    parts = raw_text.split('/paper')
    segments = []
    for p in parts:
        p = p.strip()
        if not p: continue
        tokens = p.split(maxsplit=1)
        style = "1"
        text = p
        if tokens[0].isdigit():
            style = tokens[0]
            text = tokens[1] if len(tokens) > 1 else ""
        if text.strip():
            segments.append({"style": style, "text": text.strip()})
    return segments

def make_supreme_paper(segments, start_color_idx):
    img = Image.new('RGB', (800, 1100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    MARGIN_X = 120
    START_Y = 180  # 🔥 TOP MARGIN FIX (Upar jagah chhutegi)
    LINE_SPACING = 60

    # Red & Blue Lines
    draw.line([(MARGIN_X, 0), (MARGIN_X, 1100)], fill=(255, 100, 100), width=2)
    for y in range(START_Y, 1100, LINE_SPACING):
        draw.line([(0, y), (800, y)], fill=(150, 200, 255), width=2)

    y_text = START_Y - 50 # Text line ke theek upar baithega
    color_idx = start_color_idx

    for seg in segments:
        font_url = FONTS_URL.get(str(seg["style"]), FONTS_URL["1"])
        font_name = font_url.split('/')[-1]
        font_path = f"assets/{font_name}"

        if not os.path.exists(font_path):
            try:
                res = requests.get(font_url)
                with open(font_path, 'wb') as f: f.write(res.content)
            except: pass

        try: font = ImageFont.truetype(font_path, 50) # 🔥 SABKI SIZE BARABAR
        except: font = ImageFont.load_default()

        lines = textwrap.wrap(seg["text"], width=32)
        ink = INK_COLORS[COLOR_KEYS[color_idx]]["rgb"]

        for i, line in enumerate(lines):
            if y_text > 1050: break
            
            # 🔥 SMART SERIAL NUMBER DETECTION (Margin ke andar likhega)
            serial_match = re.match(r'^([A-Za-z0-9]+[\.\)])\s*(.*)', line)
            if serial_match and i == 0:
                serial = serial_match.group(1)
                rest_of_line = serial_match.group(2)
                draw.text((MARGIN_X - 80, y_text), serial, font=font, fill=ink) # Andar
                draw.text((MARGIN_X + 20, y_text), rest_of_line, font=font, fill=ink) # Bahar
            else:
                draw.text((MARGIN_X + 20, y_text), line, font=font, fill=ink)
            
            y_text += LINE_SPACING
        
        # 🔥 MULTI-COLOR LOGIC: Agle text ke liye color badal jayega
        color_idx = (color_idx + 1) % len(COLOR_KEYS)
        if y_text > 1050: break

    bio = io.BytesIO()
    bio.name = 'paper.jpg'
    img.save(bio, 'JPEG')
    bio.seek(0)
    return bio

@bot.message_handler(commands=['paper'])
def paper_cmd(message):
    if "paper" in disabled_cmds and message.from_user.id != ADMIN_ID: 
        return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    
    raw_text = message.text
    if message.reply_to_message and message.reply_to_message.text:
        raw_text += " " + message.reply_to_message.text
        
    segments = parse_paper_text(raw_text)
    if not segments:
        return bot.reply_to(message, "📝 **Aise likho:**\n`/paper 1 Hello` ya `/paper 2 Hii /paper 5 Bye`", parse_mode="Markdown")

    msg_id = str(message.message_id)
    pending_papers[msg_id] = {"chat_id": message.chat.id, "segments": segments}

    # 9 Buttons banana
    markup = InlineKeyboardMarkup(row_width=3)
    btns = [InlineKeyboardButton(c["name"], callback_data=f"pcolor_{msg_id}_{idx}") for idx, c in enumerate(INK_COLORS.values())]
    markup.add(*btns)
    
    bot.reply_to(message, "🎨 **Kagaz pe konsi INK se likhna hai?**\n*(Agar multiple fonts hain, toh baaki texts apne aap alag color me aayenge!)*", reply_markup=markup).id, 'upload_photo')
    
    try:
        photo_stream = make_paper_image(user_text, style)
        bot.send_photo(message.chat.id, photo=photo_stream, caption=f"📝 **Daimond Batch Official Document!**\n🖋️ Style: #{style}")
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Bhai pen ki ink sookh gayi thodi: {e}", message.chat.id, wait_msg.message_id)
@bot.message_handler(commands=['xo'])
def xo_start(message):
    if "xo" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
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
        _, msg_id, color_idx = d.split("_")
        if msg_id not in pending_papers:
            return bot.answer_callback_query(call.id, "Ye paper purana ho gaya sa!")
        
        data = pending_papers[msg_id]
        bot.edit_message_text("⏳ *Kagaz pe likha ja raha hai, 2 second ruk sa...*", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        
        try:
            photo_stream = make_supreme_paper(data["segments"], int(color_idx))
            bot.send_photo(call.message.chat.id, photo=photo_stream)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            del pending_papers[msg_id]
        except Exception as e:
            bot.edit_message_text(f"❌ Error aagya: {e}", call.message.chat.id, call.message.message_id)
    
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

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    # 🔥 AI ka switch (Agar Admin ne band kiya toh AI kuch nahi bolega)
    if "ai" in disabled_cmds and message.from_user.id != ADMIN_ID: return 
    
    is_prv = message.chat.type == 'private'
    if not is_prv: active_groups.add(message.chat.id)
    uid = message.from_user.id
    txt = message.text.lower()
    bot_uname = f"@{bot.get_me().username.lower()}"
    
    is_men = bot_uname in txt
    is_rep = message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id

    if is_prv or is_men or is_rep:
        # 🚨 YAHAN NAYA VIP BUTTON LAGA DIYA HAI 🚨
        if not is_prv and not check_membership(uid):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("💎 Join Daimond Batch", url="https://t.me/Daimondbatch"))
            return bot.reply_to(message, "⚠️ ** Bhai!**\n hamara official group join karo . Neeche button dabao 👇", reply_markup=markup, parse_mode="Markdown")
            
        bot.send_chat_action(message.chat.id, 'typing')
        clean = txt.replace(bot_uname, "").strip() if not is_prv else txt.strip()
        if clean: bot.reply_to(message, get_ai_response(clean))
if __name__ == "__main__":
    keep_alive()
    threading.Thread(target=background_monitor, daemon=True).start()
    bot.infinity_polling()
