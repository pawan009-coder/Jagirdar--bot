import telebot
from telebot.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
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
    BotCommand("toprank", "top 10 rich player of game"),
    BotCommand("daily", "Har 24 ghante ka inam"),
    BotCommand("weekly", "Har 7 din mein 2000 Rs"),
    BotCommand("imagine", "apni pasand ka photo mangaye"),
    BotCommand("dart", "Kismat azmayein (/dart amount)"),
    BotCommand("shield", "500 Rs mein 24 ghante bachein (DM)"),
    BotCommand("give", "Kisi ko paise donate karein"),
    BotCommand("loan", "Loan offer karein"),
    BotCommand("return", "Udhar wapas karein"),
    BotCommand("rob", "Dusre ke paise churayein"),
    BotCommand("kill", "Shikaar karein (500 Rs inam)"),
    BotCommand("revive", "Zinda karein (700 Rs lagenge)"),
    BotCommand("xo", "Tic-Tac-Toe khelein (/xo amount)"),
    BotCommand("ban", "👑 Group se nikalein"),
    BotCommand("mute", "👑 Chup karayein"),
    BotCommand("say", "👑apna message sab ko bhejo"),
    BotCommand("askpoll", "👑 Daily poll bhejein")
])

users = {}
active_groups = set()
pending_loans = {}
xo_games = {}
poll_voters = set()
pending_says = {}
# Database se purana data nikalna
print("Loading data from database...")
try:
    for doc in users_db.find():
        users[doc["_id"]] = doc["data"]
    print(f"Loaded {len(users)} users.")
except:
    print("Abhi naya database hai ya error aaya.")

# Data permanent save karne ka function
def save_data():
    for uid, data in list(users.items()):
        users_db.update_one({"_id": uid}, {"$set": {"data": data}}, upsert=True)

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
    # Ye saare bot users ko unke paise (bal) ke hisaab se descending order mein sort karega
    sorted_users = sorted(users.items(), key=lambda x: x[1]['bal'], reverse=True)
    for rank, (user_id, data) in enumerate(sorted_users, 1):
        if user_id == uid: 
            return rank
    return "N/A"

def get_user(user_obj):
    uid = user_obj.id
    if uid not in users:
        users[uid] = {
            "name": user_obj.first_name, "bal": 1000, "status": "Alive", 
            "last_daily": 0, "last_weekly": 0, "death_time": 0, "shield_until": 0,
            "loan": {"active": False, "lender_id": 0, "amount": 0, "due_time": 0}
        }
    else:
        users[uid]["name"] = user_obj.first_name
    return users[uid]

def check_membership(uid):
    try:
        status = bot.get_chat_member(GROUP_USERNAME, uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def get_ai_response(user_text):
    try:
        # Dekho sa, yahan URL mein ab gemini-2.5-flash lag gaya hai!
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": f"Tu daimond batch ka bot hai jo ki team nexttoppers ke daimond batch ke baccho ka dost hai ishleye waise hi jawab de: {user_text}"}]}], 
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}, 
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}, 
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, 
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        res = requests.post(url, json=payload, timeout=60)
        res_json = res.json()
        
        if 'candidates' in res_json: 
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else: 
            # Error aane par ab seedha Telegram par asli bimari dikhegi
            return f"⚠️ API BIMARI: {res_json.get('error', {}).get('message', 'Unknown Error')}"
            
    except Exception as e: 
        return f"🔌 Taar hila hua hai! Asli Bimari: {str(e)}"

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
    if message.text == '/start shield':
        buy_shield(message)
        return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Join Group", url="https://t.me/Daimondbatch"))
    bot.reply_to(message, "👑 Khamma Ghani! Jodhpur King Bot mein swagat hai.", reply_markup=markup)
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

@bot.message_handler(commands=['bal'])
def check_bal(message):
    target_obj = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    u = get_user(target_obj)
    
    rank = get_rank(target_obj.id)
    total_users = len(users)
    
    # Shield Status Check
    is_protected = time.time() < u['shield_until']
    shield_status = "🛡️ Protected" if is_protected else "❌ Protection Expired"
    
    bot.reply_to(message, f"🏦 **ACCOUNT: {u['name']}**\n🌍 Global Rank: #{rank} (out of {total_users})\n🏆 Level: {get_level(u['bal'])}\n💰 Balance: {u['bal']} Rs\n🔰 Shield: {shield_status}\n❤️ Status: {u['status']}")
    
    # DM Message agar paise 1500 se kam hain (Sirf khud ka balance dekhne par)
    if target_obj.id == message.from_user.id and u['bal'] < 1500:
        try:
            dm_text = "Bhai, bhut se bande aise hai jinhone protection nahi lagaya. Unhe loot aur /daily aur /weekly command dal kr lele paise unse kuch toh rank up hogi hi teri aur protection lga kr rakhna!"
            bot.send_message(message.from_user.id, dm_text)
        except:
            pass # Agar user ne bot ko DM mein start nahi kiya hoga toh error nahi aayega
            
@bot.message_handler(commands=['toprank', 'top'])
def top_richest(message):
    if not users:
        return bot.reply_to(message, "Abhi tak koi user nahi hai sa!")
        
    # Saare users ko paise ke hisaab se sort karna
    sorted_users = sorted(users.items(), key=lambda x: x[1]['bal'], reverse=True)
    
    # Sirf Top 10 nikalna
    top_10 = sorted_users[:10]
    
    text = "🏆 **GLOBAL TOP 10 AMEER LOG** 🏆\n\n"
    
    # Ek-ek karke list banana
    for i, (uid, data) in enumerate(top_10):
        # Topper ko Crown aur Gold medal
        if i == 0:
            medal = "👑 🥇"
        elif i == 1:
            medal = "🥈"
        elif i == 2:
            medal = "🥉"
        else:
            medal = "🏅" 
            
        text += f"{medal} **{data['name']}** - {data['bal']} Rs\n"
        
    text += "\n🔥 Khelte raho aur apna naam upar lao sa!"
    bot.reply_to(message, text)
    
@bot.message_handler(commands=['shield'])
def shield_req(message):
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
    if len(message.text.split()) == 1:
        return bot.reply_to(message, "🎨 Photo banane ke liye aise likho:\n`/imagine [kuch bhi likho]`", parse_mode="Markdown")
    
    bot.send_chat_action(message.chat.id, 'upload_photo')
    prompt = message.text.replace("/imagine", "").replace("/photo", "").strip()
    safe_prompt = urllib.parse.quote(prompt)
    
    # Naya advance tarika (Direct image download)
    seed = random.randint(1, 10000)
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true&seed={seed}"
    
    try:
        res = requests.get(image_url, timeout=40)
        if res.status_code == 200:
            bot.send_photo(message.chat.id, res.content, caption=f"🎨 **Yeh lijiye aapki photo!**\n📝 Prompt: {prompt}")
        else:
            bot.reply_to(message, "❌ Server thoda aalsi ho raha hai sa! Ek baar wapas likho.")
    except Exception as e:
        bot.reply_to(message, "❌ Photo aane mein dikkat hui. Wapas try karein sa!")
        
@bot.message_handler(commands=['give', 'donate'])
def give_money(message):
    if not message.reply_to_message: return bot.reply_to(message, "Reply karke amount likho.")
    try:
        amt = int(message.text.split()[1])
        s = get_user(message.from_user)
        r = get_user(message.reply_to_message.from_user)
        if s['bal'] < amt: return bot.reply_to(message, "Paise nahi hain!")
        s['bal'] -= amt
        r['bal'] += amt
        bot.reply_to(message, f"✅ {amt} Rs donate kar diye!")
    except: bot.reply_to(message, "Format: /give 100")

@bot.message_handler(commands=['dance'])
def dance_cmd(message):
    dance_gif = "https://media.tenor.com/3Z_yJbB4g8AAAAAC/dance-party.gif"
    bot.send_animation(message.chat.id, dance_gif, caption="🕺 **Balle Balle! Party Time!** 💃")
    
@bot.message_handler(commands=['dart'])
def play_dart(message):
    u = get_user(message.from_user)
    if u['status'] == "Dead": 
        return bot.reply_to(message, "☠️ Murde nahi khelte sa!")
    
    try:
        amt = int(message.text.split()[1])
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

@bot.message_handler(commands=['rob'])
def rob_cmd(message):
    if not message.reply_to_message: return bot.reply_to(message, "Reply karke amount likho: /rob 1000")
    try:
        loot_amt = int(message.text.split()[1])
    except:
        return bot.reply_to(message, "Sahi format: /rob 1000")
        
    r = get_user(message.from_user)
    t_obj = message.reply_to_message.from_user
    t = get_user(t_obj)
    
    if message.from_user.id == t_obj.id: return bot.reply_to(message, "Khud ki jeb katega kya?")
    if r['status'] == "Dead" or t['status'] == "Dead": return bot.reply_to(message, "Murdo ke beech game nahi hota.")
    
    if t_obj.id == ADMIN_ID: 
        return bot.reply_to(message, "👑 **Aukaat mein reh!** Admin ke paas Unlimited Shield hai, use koi nahi loot sakta!")
        
    if time.time() < t['shield_until']: 
        return bot.reply_to(message, "🛡️ Target protected hai (Shield Active)!")
    
    if t['bal'] < loot_amt: 
        return bot.reply_to(message, f"Arey iske paas itne paise hi nahi hain! Iske paas sirf {t['bal']} Rs bache hain.")
    
    # 🔥 100% Chori Success (Fail wala system hata diya)
    tax = int(loot_amt * 0.05) # 5% tax
    t['bal'] -= loot_amt
    r['bal'] += (loot_amt - tax)
    bot.reply_to(message, f"🥷 **ROB 100% SUCCESS!**\nAapne {loot_amt} Rs loote. 5% Tax ({tax} Rs) cut hua, aapko mile {loot_amt - tax} Rs! 💰\nChori ekdum sateek rahi sa!")
    
@bot.message_handler(commands=['kill'])
def kill_cmd(message):
    if not message.reply_to_message: return bot.reply_to(message, "Reply karke kill likho.")
    r = get_user(message.from_user)
    t_obj = message.reply_to_message.from_user
    t = get_user(t_obj)
    if r['status'] == "Dead": return bot.reply_to(message, "Murda kisi ko nahi maar sakta.")
    if t['status'] == "Dead": return bot.reply_to(message, "Pehle se mara hua hai.")
    if t_obj.id == ADMIN_ID: return bot.reply_to(message, "Admin ko nahi maar sakte!")
    
    t['status'] = "Dead"
    t['death_time'] = time.time()
    r['bal'] += 500
    bot.reply_to(message, "☠️ KILLED! Target dead, aapko 500 Rs mile.")

@bot.message_handler(commands=['revive'])
def revive_cmd(message):
    if not message.reply_to_message: return bot.reply_to(message, "Reply karke revive likho.")
    r = get_user(message.from_user)
    t = get_user(message.reply_to_message.from_user)
    if r['bal'] < 700: return bot.reply_to(message, "700 Rs chahiye!")
    if t['status'] == "Alive": return bot.reply_to(message, "Wo zinda hai!")
    
    r['bal'] -= 700
    t['status'] = "Alive"
    bot.reply_to(message, "💉 Revived! 700 Rs kat gaye.")

@bot.message_handler(commands=['loan'])
def loan_cmd(message):
    if not message.reply_to_message: return bot.reply_to(message, "Reply karke amount likho.")
    try:
        amt = int(message.text.split()[1])
        s = get_user(message.from_user)
        r_obj = message.reply_to_message.from_user
        r = get_user(r_obj)
        if s['bal'] < amt: return bot.reply_to(message, "Paise nahi hain!")
        if r['loan']['active']: return bot.reply_to(message, "Uspe pehle se karza hai.")
        
        req_id = str(message.message_id)
        pending_loans[req_id] = {"lender": message.from_user.id, "borrower": r_obj.id, "amount": amt}
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Yes", callback_data=f"ly_{req_id}"), InlineKeyboardButton("No", callback_data=f"ln_{req_id}"))
        bot.reply_to(message.reply_to_message, f"Kya aap {amt} Rs ka loan lena chahte hain?", reply_markup=markup)
    except: bot.reply_to(message, "Format: /udhar 500")

@bot.message_handler(commands=['return'])
def repay_cmd(message):
    u = get_user(message.from_user)
    if not u['loan']['active']: return bot.reply_to(message, "Koi udhar nahi hai.")
    due = u['loan']['amount']
    lid = u['loan']['lender_id']
    if u['bal'] < due: return bot.reply_to(message, "Paise kam hain!")
    u['bal'] -= due
    if lid in users: users[lid]['bal'] += due
    u['loan']['active'] = False
    bot.reply_to(message, "✅ Udhar chukta hua!")

@bot.message_handler(commands=['daily', 'weekly'])
def claims(message):
    u = get_user(message.from_user)
    cmd = message.text.split()[0].lower()
    t = time.time()
    if cmd == '/daily':
        if t - u['last_daily'] > 86400: u['bal'] += 200; u['last_daily'] = t; bot.reply_to(message, "🎁 200 rs mile!")
        else: bot.reply_to(message, "Kal aana!")
    elif cmd == '/weekly':
        if t - u['last_weekly'] > 604800: u['bal'] += 2000; u['last_weekly'] = t; bot.reply_to(message, "🎁 2000 rs mile!")
        else: bot.reply_to(message, "Agle hafte aana!")

@bot.message_handler(commands=['xo'])
def xo_start(message):
    try:
        amt = int(message.text.split()[1])
        u = get_user(message.from_user)
        if u['bal'] < amt: return bot.reply_to(message, "Paise kam hain!")
        gid = str(message.message_id)
        xo_games[gid] = {"p1": message.from_user.id, "p2": None, "amt": amt, "board": ["-"]*9, "turn": message.from_user.id}
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Game", callback_data=f"xo_join_{gid}"))
        bot.reply_to(message, f"XO Game {amt} Rs ka! P2 join kare:", reply_markup=markup)
    except: bot.reply_to(message, "Format: /xo 100")

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

@bot.message_handler(commands=['ban', 'unban', 'mute', 'unmute', 'pin'])
def rose_features(message):
    if not check_membership(message.from_user.id): return
    member = bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ['administrator', 'creator']: return
    cmd = message.text.split()[0].lower()
    if cmd == '/pin' and message.reply_to_message:
        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        bot.reply_to(message, "Message pinned!")
        return
    if not message.reply_to_message: return bot.reply_to(message, "Reply karo!")
    tid = message.reply_to_message.from_user.id
    try:
        if cmd == '/ban': bot.ban_chat_member(message.chat.id, tid); bot.reply_to(message, "Banned!")
        elif cmd == '/unban': bot.unban_chat_member(message.chat.id, tid); bot.reply_to(message, "Unbanned!")
        elif cmd == '/mute': bot.restrict_chat_member(message.chat.id, tid, can_send_messages=False); bot.reply_to(message, "Muted!")
        elif cmd == '/unmute': bot.restrict_chat_member(message.chat.id, tid, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True); bot.reply_to(message, "Unmuted!")
    except: bot.reply_to(message, "Admin power chahiye ya main admin nahi hu!")

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
            r['loan'] = {"active": True, "lender_id": req['lender'], "amount": due, "due_time": time.time() + 86400}
            del pending_loans[req_id]
            bot.edit_message_text("Loan Accepted!", call.message.chat.id, call.message.message_id)

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
            # Agar photo/video par reply tha, toh exact waise hi copy karega bina "Forwarded" tag ke
            if data['type'] == 'copy':
                bot.copy_message(chat_id, call.message.chat.id, data['content'])
            # Agar direct text likha tha
            else:
                bot.send_message(chat_id, data['content'])

        try:
            if target == "all":
                count = 0
                for gid in list(active_groups):
                    try:
                        send_to_chat(gid)
                        count += 1
                    except: pass
                bot.edit_message_text(f"✅ Boss! Message ek sath {count} groups mein blast kar diya gaya!", call.message.chat.id, call.message.message_id)
            else:
                gid = int(target)
                send_to_chat(gid)
                chat_info = bot.get_chat(gid)
                bot.edit_message_text(f"✅ Message '{chat_info.title}' mein bhej diya sa!", call.message.chat.id, call.message.message_id)
        except Exception as e:
            bot.answer_callback_query(call.id, "Bhejne mein error aayi!")
            
        # Message bhejne ke baad data delete kar do
        del pending_says[uid]
        
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
    is_prv = message.chat.type == 'private'
    if not is_prv: active_groups.add(message.chat.id)
    uid = message.from_user.id
    txt = message.text.lower()
    bot_uname = f"@{bot.get_me().username.lower()}"
    
    is_men = bot_uname in txt
    is_rep = message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id

    if is_prv or is_men or is_rep:
        if not is_prv and not check_membership(uid): return bot.reply_to(message, "Pehle group join karo sa!")
        bot.send_chat_action(message.chat.id, 'typing')
        clean = txt.replace(bot_uname, "").strip() if not is_prv else txt.strip()
        if clean: bot.reply_to(message, get_ai_response(clean))

if __name__ == "__main__":
    keep_alive()
    threading.Thread(target=background_monitor, daemon=True).start()
    bot.infinity_polling()
