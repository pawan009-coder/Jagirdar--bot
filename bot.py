import telebot
from telebot.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
import re
import feedparser
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import yt_dlp
from PIL import Image, ImageDraw, ImageFont
import io
from deep_translator import GoogleTranslator
import textwrap
import time
import random
import requests
import os
import subprocess
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
# 🚀 HUGGING FACE PRIVATE API ENGINE LINK
HF_API = "https://singhp08-daimond-batch.hf.space"
# 🌐 RENDER DUMMY SERVER (Iske bina Render crash karega)
app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 Daimond Batch Bot is LIVE and Makkhan! 🔥"

def run_server():
    # Render jo port dega uspar chalega, warna 10000 par
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

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
        
    wait_msg = bot.reply_to(message, "⏳ *Daimond Batch ka Maha-Granth (Help Menu) khol raha hu...*", parse_mode="Markdown")
    bot.send_chat_action(message.chat.id, 'typing')

    # ==========================================
    # 📜 PART 1: ECONOMY, CRIME & CASINO
    # ==========================================
    help_text_1 = """
👑 **DAIMOND BATCH - THE SUPREME GUIDE (PART 1)** 👑
Dhyan se suno dosto! Ye koi aam bot nahi hai, ye ek poori virtual duniya hai jahan aap ameer ban sakte ho, mafia ban sakte ho, aur AI ke maje le sakte ho. Yahan har command ka ek deep secret hai. Niche saari details deeply samjhayi gayi hain:

🏦 **BANK AUR ECONOMY (Paisa Hi Paisa)** 💸
🔹 `/bal` : Ye aapka personal bank khata hai. Isse aapko pata chalega ki aapka Global Rank kya hai, aapke paas kitna cash (Rs) hai, aapne kitne khoon (kills) kiye hain, aapke jhole (inventory) mein kya-kya samaan hai, aur aapki Shield active hai ya nahi.
🔹 `/daily` : Har 24 ghante mein aao aur free ke 200 Rs claim karo. Agar aapne Chor Bazaar se "Don Taj" pehna hai, toh ye rakam double (400 Rs) ho jayegi!
🔹 `/weekly` : Har 7 din mein ek baar bada inam! Isey lagane par seedha 2000 Rs milte hain. Don Taj walo ko 4000 Rs milte hain!
🔹 `/give [amount]` : Apne dosto ko paise donate karne ka tarika. Kisi ke bhi message par reply karke likho `/give 500` aur aapke bank se paise uske bank me chale jayenge. Asli bhaichara!
🔹 `/loan [amount]` : Agar dost ko udhar dena hai toh uske message par reply karke `/loan 1000` likho. Us bande ke paas ek button aayega accept karne ka. Dhyan rahe, 24 ghante mein udhar wapas nahi kiya toh bot automatically uske account se paise aur 500 Rs fine kaat kar aapko de dega! Max limit 4000 Rs hai.
🔹 `/return` : Apne sir se karza utarne ke liye ye command lagao. Jiska udhar liya hai, usko apne aap paise chale jayenge.
🔹 `/shield` : 500 Rs dekar 24 ghante ke liye "Kavach" khareedo. Iske baad koi bhi aapko loot (rob) ya maar (kill) nahi payega.

🔪 **UNDERWORLD AUR MAFIA (Crime City)** 🩸
🔹 `/shop` (ya `/bazaar`) : Ye sabse khatarnak jagah hai! Yahan se aap apne paise se hathiyar aur security khareed sakte ho:
   - 🔪 *Chakku (1500 Rs)*: Chori karne par 200 Rs ka extra bonus.
   - 🔫 *Desi Katta (8000 Rs)*: Khoon karne ka inam 500 se badhkar 1500 Rs.
   - 🦺 *Bulletproof Jacket (15000 Rs)*: Ek baar goli lagne se bachayegi.
   - 🐕 *Khufiya Kutta (30000 Rs)*: Koi rob karega toh 30% chance hai kutta usey kaat lega aur chori fail ho jayegi!
   - 💣 *AK-47 (100000 Rs)*: Har khoon par seedha 5000 Rs ka heavy inam!
   - 👑 *Don Taj (500000 Rs)*: Daily aur Weekly inam hamesha ke liye Double!
🔹 `/rob [amount]` : Kisi ka paisa churana ho toh uske message par reply karke `/rob 1000` likho. Par yaad rakhna, agar uske paas kutta hua ya shield hui, toh aapka plan fail ho sakta hai. Aur chori ka 5% tax bot kaat leta hai!
🔹 `/kill` : Dushmani nikalne ka best tarika. Reply karke `/kill` likho. Target "Dead" ho jayega. Murda insaan koi game nahi khel sakta. Kill ka inam aapke hathiyar par depend karta hai.
🔹 `/revive` : Agar aapka dost mara gaya hai, toh aap uske message par reply karke 700 Rs dekar usko wapas zinda kar sakte ho (Sanjeevani Booti).
🔹 `/toprank` : Pure group mein sabse ameer Top 10 logo ki list dekhne ke liye.
🔹 `/topkills` : Group ke sabse khatarnak Top 10 Serial Killers ki list!

🎰 **CASINO AUR GAMES (Kismat Ka Khel)** 🎲
🔹 `/dice [amount]` : Apna paisa lagao aur Ludo ka dice feko. Agar dice par number '6' aata hai, toh aapka lagaya hua paisa seedha 3 Guna (3x) ho jayega! Warna haar jaoge.
🔹 `/spin [amount]` : Casino ki slot machine. Agar teen '777' (Jackpot) match ho gaye, toh paisa 10 GUNA! Agar koi normal teeno image match hui toh 3 GUNA paisa!
🔹 `/dart [amount]` : Teerandaazi! Agar teer center ke bilkul kareeb (Score 4, 5, ya 6) laga, toh paisa Double (2x).
🔹 `/xo [amount]` : Apne dosto ke sath Tic-Tac-Toe khelo aur unka paisa jeeto.
🔹 `/sps [amount]` : Stone, Paper, Scissors! Asli multiplayer game jisme 2 log bet lagate hain aur jo jeet ta hai wo poore paise le jata hai!
"""

    # ==========================================
    # 🤖 PART 2: AI & GOD-LEVEL TOOLS
    # ==========================================
    help_text_2 = """
🤖 **AI AUR GOD-LEVEL TOOLS (Future is Here)** 🚀
Daimond Batch ka bot duniya ke sabse advanced AI models se connected hai. Ye saari commands free mein aapko premium features deti hain:

🔹 `/ask [question]` : Humara apna 'Jarvis' AI. Ye duniya ke sabse fast LLaMA-3 model par chalta hai. Aap isse kuch bhi pucho (jaise `/ask Duniya ka sabse ameer aadmi kon hai?`), aur ye aapko type karke nahi, balki apni asli AI Awaaz (Voice Note) mein jawab bol kar sunayega!
🔹 `/roast` : Kisi dost ke message par reply karke `/roast` likho. Bot usko ek desi underground rapper ki tarah bhayanak tareeqe se voice note mein diss karega. (Caution: Boss se panga liya toh bot ulta aapko hi dho dalega!)
🔹 `/reel [topic]` (ya `/video`) : Apne channel ke liye automatic cinematic video banayein! Bas `/reel hard work` likho. Bot FLUX AI se ek HD cinematic photo banayega, aur uspe ek heavy Hindi motivational shayari khud likh kar aur voice mein record karke group mein bhej dega. Ek second mein poora studio ka kaam!
🔹 `/photo` (Background Remover) : Kisi bhi photo par reply karke `/photo` likho. Bot server par apne AI se us photo ka pichla hissa (background) mita kar usko ek transparent HD PNG file bana kar bhej dega, jise aap kisi bhi editing me use kar sakte ho.
🔹 `/imagine [prompt]` : Duniya ka sabse latest FLUX.1-schnell model. Aap likho `/imagine ek udta hua cyberpunk ghoda`, aur bot 15 second mein ekdum real aur HD photo bana kar aapke samne rakh dega.
🔹 `/dl [link]` (ya `/insta`, `/yt`) : The Universal Downloader! Aap kisi bhi Instagram Reel, YouTube Short ya Twitter video ka link do. Bot usko background mein chup-chap download karke bina kisi watermark ke Telegram par upload kar dega.
🔹 `/read` (ya `/ocr`) : Kitabo ka Hacker! Kisi lambe English notes ya kitab ke page ki photo kheench kar uspar `/read` reply karo. Bot photo ke andar likha hua poora text padh lega aur usko Hindi mein translate karke aapko bhej dega.
🔹 `/sketch` : Apni kisi photo par reply karke `/sketch` lagao. Bot OpenCV library ka use karke aapki photo ko ek realistic hand-drawn pencil sketch mein badal dega.
🔹 `/speak [text]` (ya `/bolo`) : Bot ki zubaan! Aap jo bhi text likhoge, bot usko ekdam saaf aur Madhur awaaz mein bol kar Voice note bhejega.
🔹 `/paper [font_number] [text]` : Apna text ek realistic notebook ke kagaz par likhwayein! Humare paas 30 VIP cursive fonts hain. Jaise `/paper 1 Hello jodhpur`. Bot aapse ink ka color poochega aur ekdum asli handwriting wali image dega!
🔹 `/dance` : Group mein mahol banane ke liye Balle-Balle wala party GIF

*Agar bot pasand aaye, toh apne sabhi Telegram groups mein isko add karo aur Daimond Batch ka jalwa dikhao!*
"""

    try:
        # Message 1 bhejna
        bot.send_message(message.chat.id, help_text_1, parse_mode="Markdown")
        # 1 second rukna taaki Telegram spam detect na kare
        time.sleep(1)
        # Message 2 bhejna
        bot.send_message(message.chat.id, help_text_2, parse_mode="Markdown")
        
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Panna phat gaya sa! Error: {e}", message.chat.id, wait_msg.message_id)

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
    if message.from_user.id != ADMIN_ID or message.chat.type != 'private': return
    
    header = "📋 **DAIMOND BATCH USERS** 📋\n━━━━━━━━━━━━━━━━━━━\n"
    text = header
    
    for i, (uid, data) in enumerate(users.items(), 1):
        status = "🚫 BLOCKED" if data.get('blocked', False) else "✅ Active"
        line = f"{i}. {data['name']} (ID: `{uid}`) - {status}\n"
        
        # Agar agla line jodne se message 4000 se bada ho raha hai, toh pehle itna bhej do
        if len(text) + len(line) > 4000:
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
            text = line # Naya message is line se shuru karo
        else:
            text += line
            
    # Jo aakhiri bacha hua text hai, wo bhej do
    if text and text != header:
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
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
    if target_id == ADMIN_ID: return bot.reply_to(message, "❌ Boss! Khud ko block nahi kar sakte!")
        
    if cmd == '/block':
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
    markup.add(InlineKeyboardButton("▶️ Subscribe Freemind Coding", url="https://youtube.com/@freemind_coding?si=MCcJkwA1wuywfFMC"))
    
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

        # 4. 🚨 FIXED: HF API se Rap Record Karna
        safe_reply = ai_reply.replace('"', '').replace("'", "")
        res_tts = requests.post(f"{HF_API}/tts", data={"text": safe_reply, "rate": "+10%"})
        
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
    # Lock Check
    if "dl" in disabled_cmds and message.from_user.id != ADMIN_ID: 
        return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
        
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(message, "📥 **Aise likho:**\n`/dl [Video ka Link]`\n*(Instagram, YouTube, Twitter kuch bhi chalega sa!)*", parse_mode="Markdown")
        
    link = parts[1].strip()
    wait_msg = bot.reply_to(message, "⏳ *Khufiya tarike se video chura raha hu, 5-10 second ruk sa...*", parse_mode="Markdown")
    bot.send_chat_action(message.chat.id, 'record_video')
    
    file_name = f"video_{message.message_id}.mp4"
    
    # ⚙️ yt-dlp ki VIP Settings
    ydl_opts = {
        'outtmpl': file_name,
        'format': 'best[ext=mp4]/best', # Telegram ko MP4 pasand hai
        'noplaylist': True,
        'quiet': True,
        'max_filesize': 45000000 # 🚨 Telegram bot API ki limit 50MB hoti hai, isliye 45MB max rakha hai
    }
    
    try:
        # 1. Background mein video download karna
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
            
        # 2. Telegram par wapas bhejna
        with open(file_name, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, caption="📥 **Daimond Batch Downloader**\n✅ *Ye lijiye sa aapka video!*")
            
        # 3. Kachra saaf karna
        bot.delete_message(message.chat.id, wait_msg.message_id)
        os.remove(file_name)
        
    except Exception as e:
        error_msg = str(e).lower()
        if "max_filesize" in error_msg or "too large" in error_msg:
            bot.edit_message_text("❌ Video bahut bada hai sa! Telegram par max 50MB hi bhej sakte hain (Shorts/Reels try karo).", message.chat.id, wait_msg.message_id)
        elif "private" in error_msg or "unsupported" in error_msg:
            bot.edit_message_text("❌ Video private hai ya link galat hai sa!", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ Video churane mein fail ho gaya sa! Wapas try karo.", message.chat.id, wait_msg.message_id)
            
        # Agar error ke baad file ban gayi ho toh delete kar do
        if os.path.exists(file_name):
            os.remove(file_name)
            
# ==========================================
# 📰 THE AI NEWS ANCHOR (Subah 8 aur Raat 8)
# ==========================================
def auto_news_broadcast():
    # Agar bot kisi group mein nahi hai, toh news kisko dega?
    if not active_groups:
        return

    # Render ki tijori se Hugging Face ki chaabi nikalna
    HF_KEY = os.environ.get('H')
    if not HF_KEY: 
        print("HF Key nahi mili!")
        return

    try:
        # 1. Google News India (Hindi) se taaza khabarein churana
        # feedparser direct internet se real-time news nikalta hai
        feed = feedparser.parse("https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi")
        headlines = [entry.title for entry in feed.entries[:3]] # Top 3 news

        if not headlines: return

        # Anchor ki Script tayyar karna
        script = f"नमस्कार! डायमंड बैच न्यूज़ में आपका स्वागत है। आज की सबसे बड़ी खबरें इस प्रकार हैं... पहली खबर: {headlines[0]}. दूसरी खबर: {headlines[1]}. तीसरी खबर: {headlines[2]}. ताज़ा खबरों के लिए जुड़े रहें, आपका समय शुभ हो!"

        # 🚨 FIXED: HF API se News Anchor ki Voice Record karna
        res_tts = requests.post(f"{HF_API}/tts", data={"text": script, "rate": "+0%"})

        # FLUX AI se TV Studio Background Banana
        flux_url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
        headers_hf = {"Authorization": f"Bearer {HF_KEY}"}
        img_prompt = "Professional TV news anchor studio desk with BREAKING NEWS graphics, cinematic lighting, 8k resolution, highly detailed"
        res_img = requests.post(flux_url, headers=headers_hf, json={"inputs": img_prompt}, timeout=60)

        # Sabhi Active Groups mein Blast Karna!
        if res_tts.status_code == 200 and res_img.status_code == 200:
            from io import BytesIO
            for gid in list(active_groups):
                try:
                    bot.send_photo(gid, photo=res_img.content, caption="📰 **DAIMOND BATCH LIVE NEWS** 📰\n*(Powered by AI Anchor)*")
                    
                    audio_bytes = BytesIO(res_tts.content)
                    audio_bytes.name = "news.ogg"
                    bot.send_voice(gid, audio_bytes, caption="🎙️ *Aaj Ki Taaza Khabar sunne ke liye Play karein!*")
                except Exception as e:
                    print(f"Group {gid} mein bhejne me error: {e}")

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
@bot.message_handler(commands=['imagine', 'img'])
def generate_image(message):
    # Lock Check
    if "imagine" in disabled_cmds and message.from_user.id != ADMIN_ID: 
        return bot.reply_to(message, "🚫 Ye command abhi Admin ne band kar rakhi hai!")
    
    prompt = message.text.replace("/imagine", "").replace("/photo", "").strip()
    if not prompt:
        return bot.reply_to(message, "🎨 **Aise likho:**\n`/imagine ek udta hua ghoda aur Jodhpur ka qila`", parse_mode="Markdown")
    
    # 🚨 Render ki tijori se HF ki chaabi nikalna (Aapne naam 'H' rakha hai)
    HF_KEY = os.environ.get('H')
    if not HF_KEY:
        return bot.reply_to(message, "❌ Boss! a hi nahi hua!")

    wait_msg = bot.reply_to(message, "⏳ *photo banha raha hu, 10-20 second wait karo sa...*", parse_mode="Markdown")
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {HF_KEY}"}
    payload = {"inputs": prompt}
    
    try:
        # Timeout lamba rakha hai taaki heavy photo aaram se aa sake
        res = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if res.status_code == 200:
            bot.send_photo(message.chat.id, photo=res.content, caption=f"🎨 **Yeh lijiye aapki AI Photo!**\n📝 Prompt: {prompt}")
            bot.delete_message(message.chat.id, wait_msg.message_id)
        elif res.status_code == 503:
            # Jab model pehli baar load hota hai toh 503 error aata hai
            bot.edit_message_text("⏳ Model abhi neend se jaag raha hai sa! Bas 20-30 second baad wapas command dalo, ekdum chal padega.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text(f"❌ Kuch gadbad hui sa! Error Code: {res.status_code}", message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ Photo banne mein thodi dikkat hui. Wapas try karein sa!", message.chat.id, wait_msg.message_id)

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
def make_sketch(message):
    if "sketch" in disabled_cmds and message.from_user.id != ADMIN_ID: return
    if not message.reply_to_message or not message.reply_to_message.photo:
        return bot.reply_to(message, "🎨 Kisi photo par reply karke `/sketch` likho sa!")
        
    wait_msg = bot.reply_to(message, "⏳ *Engine sketch bana raha hai...*")
    try:
        file_info = bot.get_file(message.reply_to_message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        res = requests.post(f"{HF_API}/sketch", files={"image": downloaded_file})
        if res.status_code == 200:
            bot.send_photo(message.chat.id, res.content, caption="🎨 **Daimond Batch Artist**\n✏️ Ye rahi Pencil Sketch!")
            bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, wait_msg.message_id)

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

@bot.message_handler(commands=['photo'])
def remove_background_cmd(message):
    if "photo" in disabled_cmds and message.from_user.id != ADMIN_ID: return
    if not message.reply_to_message or not message.reply_to_message.photo:
        return bot.reply_to(message, "📸 **Aise likho:**\nKisi photo par reply karke `/photo` likho sa!", parse_mode="Markdown")
        
    wait_msg = bot.reply_to(message, "⏳ *background mita raha hu...*")
    try:
        file_info = bot.get_file(message.reply_to_message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        res = requests.post(f"{HF_API}/bg-remove", files={"image": downloaded_file})
        if res.status_code == 200:
            from io import BytesIO
            final_png = BytesIO(res.content)
            final_png.name = "transparent.png"
            bot.send_document(message.chat.id, final_png, caption="📸 **Daimond Batch BG Remover**")
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ Engine ne nakhre kiye sa!", message.chat.id, wait_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, wait_msg.message_id)
            
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
    if "xo" in disabled_cmds and message.from_user.id != ADMIN_ID: return bot.reply_to(...)
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
    # Admin Lock Check
    if "hd" in disabled_cmds and message.from_user.id != ADMIN_ID: return
    
    if not message.reply_to_message or not message.reply_to_message.photo:
        return bot.reply_to(message, "📸 **Aise likho:**\nKisi blur ya purani photo par reply karke `/hd` likho sa!", parse_mode="Markdown")
        
    wait_msg = bot.reply_to(message, "⏳ *Engine photo ko 4K HD bana raha hai, thoda time lagega ruk sa...*", parse_mode="Markdown")
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    try:
        # 1. Telegram se purani photo download karna
        file_info = bot.get_file(message.reply_to_message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # 2. HF API par bhej kar Enhance (HD) karwana
        res = requests.post(f"{HF_API}/enhance", files={"image": downloaded_file}, timeout=60)
        
     if res.status_code == 200:
            # --- WATERMARK ENGINE (Gemini/Meta AI Style) ---
            img = Image.open(io.BytesIO(res.content)).convert("RGBA")
            make_canvas = Image.new('RGBA', img.size, (0,0,0,0))
            draw = ImageDraw.Draw(make_canvas)

            # Font size photo ke hisaab se (thoda chota aur elegant)
            font_size = max(20, int(img.height * 0.03)) 
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            text = "jagirdar pawan"

            # Text ka size nikalna
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]

            # Position: Bottom Right Corner (Thoda sa margin chhod kar)
            x = img.width - tw - 40
            y = img.height - th - 40

            # White color with transparency (Halka dikhne ke liye 160)
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 160))

            # Dono images ko merge karna
            final_img = Image.alpha_composite(img, make_canvas).convert("RGB")

            # --- FINAL SENDING ---
            output = io.BytesIO()
            final_img.save(output, format="JPEG", quality=100)
            output.seek(0)
            output.name = "HD_Photo.jpg"
            
            bot.send_photo(message.chat.id, output, caption="📸 **DAIMOND BATCH HD STUDIO**\n✨ *Photo ekdum 4K Makkhan ho gayi sa!*")
            bot.delete_message(message.chat.id, wait_msg.message_id)
            
        else:
            bot.edit_message_text("❌ Engine ne nakhre kiye sa! Wapas try karo.", message.chat.id, wait_msg.message_id)
            
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

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    # 🔥 AI ka switch (Agar Admin ne band kiya toh AI kuch nahi bolega)
    if "ai" in disabled_cmds and message.from_user.id != ADMIN_ID: return 
    
    is_prv = message.chat.type == 'private'
    if not is_prv: active_groups.add(message.chat.id)
    uid = message.from_user.id
    txt = message.text.lower()
    
    # 🛑 SPAM & PORN TEXT FILTER
    bad_words = ["pornhub.com", "xvideos.com", "xnxx.com", "xxx", "nude", "sex video", "brazzers"]
    if any(word in txt for word in bad_words) and uid != ADMIN_ID:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f"🚫 **Link Blocked!**\n{message.from_user.first_name}, yahan ye sab kachra link mat bhej!")
            return # Aage AI ko reply karne se rok dega
        except: pass
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
    
    # 🚨 NAYA: NEWS ANCHOR SCHEDULER (India Time ke hisaab se)
    # Ye background mein chup-chap time dekhta rahega
    scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Kolkata"))
    # Subah 8:00 AM ke liye
    scheduler.add_job(auto_news_broadcast, 'cron', hour=8, minute=0)
    # Raat 8:00 PM (20:00) ke liye
    scheduler.add_job(auto_news_broadcast, 'cron', hour=20, minute=0)
    scheduler.start()
    
    # Bot ko lagatar chalane ke liye
    bot.infinity_polling()
