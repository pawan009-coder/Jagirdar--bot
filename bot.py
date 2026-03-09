import telebot
import time
import random
import requests
import os
from flask import Flask
import threading

# ==========================================
# 1. RENDER KEEP-ALIVE (SERVER SETUP)
# ==========================================
app = Flask('')
@app.route('/')
def home(): return "Jodhpur King Bot is 100% Online!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# ==========================================
# 2. BOT & KEYS CONFIGURATION
# ==========================================
API_TOKEN = '8625875353:AAECoBaDSeZyLkX21ZNhhCdilnVWhYMLpAY'
GEMINI_API_KEY = 'AIzaSyBM2xs5jGDQHn8MfJDb3II3ijxOfLTaXeg'
ADMIN_ID = 7574760011 
GROUP_USERNAME = "@Daimondbatch" 
bot = telebot.TeleBot(API_TOKEN)

# ==========================================
# 3. ADVANCED DATABASE & ARRAYS
# ==========================================
users = {}
active_groups = set() # Shaming ke liye groups track karega

BAD_WORDS = [
    "bc", "mc", "bsdk", "madrachod", "behenchod", "gandu", 
    "chutiya", "lodu", "kamine", "harami", "randi", "saala", "bkl", "mkb", "suar"
]

def get_user(user_obj):
    uid = user_obj.id
    if uid not in users:
        users[uid] = {
            "name": user_obj.first_name,
            "bal": 1000, 
            "status": "Alive", 
            "last_daily": 0, 
            "warns": 0, 
            "shield_until": 0,
            "shield_alerted": False,
            "loan": {"active": False, "lender_id": 0, "amount": 0, "due_time": 0}
        }
    else:
        users[uid]["name"] = user_obj.first_name # Update name
    return users[uid]

def get_rank(uid):
    sorted_users = sorted(users.items(), key=lambda x: x[1]['bal'], reverse=True)
    for rank, (user_id, data) in enumerate(sorted_users, 1):
        if user_id == uid:
            return rank
    return "N/A"

def check_membership(uid):
    try:
        status = bot.get_chat_member(GROUP_USERNAME, uid).status
        return status in ['member', 'administrator', 'creator']
    except: 
        return False

# ==========================================
# 4. GEMINI AI (FIXED 404 ERROR & SAFETY BLOCKS OFF)
# ==========================================
def get_ai_response(user_text):
    try:
        # '-latest' lagaya taaki 404 error na aaye
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": f"Tu Jodhpur King bot hai. Desi Jodhpuri style mein chota jawab de: {user_text}"}]}],
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        res = requests.post(url, json=payload, timeout=10).json()
        if 'candidates' in res:
            return res['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"⚠️ AI Error: {res.get('error', {}).get('message', 'Unknown AI Error')}"
    except Exception as e:
        return "🔌 Network issue sa! Abhi AI thak gaya hai."

# ==========================================
# 5. 24/7 BACKGROUND MONITOR (SHIELD ALERT & LOAN SHAMING)
# ==========================================
def background_monitor():
    while True:
        try:
            current_time = time.time()
            for uid, data in list(users.items()):
                
                # A. SHIELD RENEWAL ALERT (1 Hour Before)
                time_left = data['shield_until'] - current_time
                if 0 < time_left <= 3600 and not data['shield_alerted']:
                    try:
                        bot.send_message(uid, f"🛡️ **SHIELD ALERT!**\nAapki protection sirf 1 ghante mein khatam hone wali hai! Turant group mein aakar `/shield` lagao warna log loot lenge!")
                    except: pass 
                    data['shield_alerted'] = True

                # B. LOAN AUTO-CUT & SHAMING (After 24 Hours)
                if data['loan']['active'] and current_time > data['loan']['due_time']:
                    lender_id = data['loan']['lender_id']
                    due_amount = data['loan']['amount']
                    fine = 500
                    total_cut = due_amount + fine

                    data['bal'] -= total_cut
                    if lender_id in users:
                        users[lender_id]['bal'] += total_cut
                    
                    data['loan']['active'] = False # Loan is now cleared
                    
                    shame_msg = (f"🚨 **MAHA-GAREEB ALERT!** 🚨\n\n"
                                 f"Ek mahan garib user jiska naam **{data['name']}** hai, isne paise udhar liye the aur wapas nahi diye.\n"
                                 f"Ye itna zyada garib hai ki isey paise rakhne ka koi haq nahi hai! "
                                 f"Niyam ke anusaar, iske account se 24 ghante baad apne aap {total_cut} rs (Capital + Interest + 500 Fine) kaat kar jisne paise diye the, use de diye gaye hain! 💸😂")
                    
                    for group_id in list(active_groups):
                        try: bot.send_message(group_id, shame_msg)
                        except: active_groups.remove(group_id)

        except Exception as e: print("Monitor Error:", e)
        time.sleep(60) # Har 1 min me check karega

# ==========================================
# 6. ALL USER COMMANDS (/bal, /info, /shield, /udhar, /rob)
# ==========================================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    get_user(message.from_user)
    bot.reply_to(message, "👑 **Khamma Ghani!** Jodhpur King Bot mein swagat hai.\nBaat karne ke liye mujhe tag karein ya mere message par reply karein.")

@bot.message_handler(commands=['bal', 'info'])
def check_bal(message):
    target_obj = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    u = get_user(target_obj)
    rank = get_rank(target_obj.id)
    time_left = u['shield_until'] - time.time()
    
    if time_left > 0:
        h = int(time_left // 3600)
        m = int((time_left % 3600) // 60)
        shield_status = f"Active 🛡️ ({h}h {m}m left)"
    else:
        shield_status = "Nahi Hai ❌"

    loan_status = f"{u['loan']['amount']} Rs Baaki hain!" if u['loan']['active'] else "Koi Udhar nahi."

    text = (f"🏦 **ACCOUNT INFO: {u['name']}**\n"
            f"🌍 Global Rank: #{rank}\n"
            f"💰 Balance: {u['bal']} Rs\n"
            f"❤️ Status: {u['status']}\n"
            f"🛡️ Protection: {shield_status}\n"
            f"💳 Loan: {loan_status}\n"
            f"⚠️ Warnings: {u['warns']}")
    bot.reply_to(message, text)

@bot.message_handler(commands=['shield'])
def buy_shield(message):
    u = get_user(message.from_user)
    if u['bal'] < 500:
        bot.reply_to(message, "❌ Shield lene ke liye 500 rs chahiye!")
        return
    
    time_left = u['shield_until'] - time.time()
    if time_left > 3600:
        bot.reply_to(message, "⚠️ Aapki pehli shield abhi chal rahi hai! Jab 1 ghanta bachega tabhi nayi shield laga sakte ho.")
        return

    u['bal'] -= 500
    u['shield_until'] = time.time() + 86400  # 24 Hours
    u['shield_alerted'] = False
    bot.reply_to(message, "🛡️ **SHIELD ACTIVATED!**\n500 rs cut gaye. Agle 24 ghante tak koi chori nahi kar payega. (1 ghante pehle DM bhejunga!)")

@bot.message_handler(commands=['udhar'])
def give_loan(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Udhar dene ke liye receiver ke message par reply karke likho: `/udhar [amount]`")
        return
    
    try:
        amount = int(message.text.split()[1])
        lender = get_user(message.from_user)
        borrower_obj = message.reply_to_message.from_user
        borrower = get_user(borrower_obj)
        
        if message.from_user.id == borrower_obj.id: return

        if lender['bal'] < amount:
            bot.reply_to(message, "❌ Aapke khud ke paas itne paise nahi hain sa!")
            return
        if borrower['loan']['active']:
            bot.reply_to(message, "❌ Is bande par pehle se udhar chada hai, aur mat do warna dub jayenge!")
            return

        # 10% Interest
        interest = int(amount * 0.10)
        total_due = amount + interest

        lender['bal'] -= amount
        borrower['bal'] += amount
        borrower['loan'] = {
            "active": True, "lender_id": message.from_user.id, 
            "amount": total_due, "due_time": time.time() + 86400 # 24 Hours
        }
        
        bot.reply_to(message, f"💸 **UDHAR PASS!**\n{lender['name']} ne {borrower['name']} ko {amount} Rs udhar diye.\n"
                              f"Chukana hoga: {total_due} Rs (10% Interest).\n"
                              f"⏳ Time: 24 Ghante! Warna public mein bezzati aur 500 fine lagega!")
    except: bot.reply_to(message, "Format: `/udhar 500`")

@bot.message_handler(commands=['rob'])
def rob_cmd(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Chori karne ke liye target ke message par reply karke /rob likho!")
        return
    
    r_user = get_user(message.from_user)
    t_user = get_user(message.reply_to_message.from_user)
    t_name = t_user['name']

    if message.from_user.id == message.reply_to_message.from_user.id:
        bot.reply_to(message, "Arey shaane, khud ki jeb katega kya?")
        return

    if r_user['status'] == "Dead" or t_user['status'] == "Dead":
        bot.reply_to(message, "☠️ Murdon ke beech chori nahi hoti sa!")
        return

    if time.time() < t_user['shield_until']:
        r_user['bal'] -= 200
        bot.reply_to(message, f"⚡ **CURRENT LAGA!**\n{t_name} ke paas 🛡️ Shield hai! Aapke 200 rs fine lag gaya.")
        return

    if t_user['bal'] < 200:
        bot.reply_to(message, f"Arey chhod de garib ko! Ye {t_name} bahut garib hai, iske paas bas {t_user['bal']} rs bache hain. 😭")
        return

    if random.choice([True, False]): # 50% Chance
        loot = int(t_user['bal'] * random.uniform(0.1, 0.25))
        t_user['bal'] -= loot
        r_user['bal'] += loot
        bot.reply_to(message, f"🥷 **CHORI SUCCESS!**\nAapne {t_name} ki jeb kaat li aur {loot} rs loot liye! 💰")
    else:
        r_user['bal'] -= 100
        bot.reply_to(message, "🚨 **PAKDE GAYE!**\nChori nakam rahi aur 100 rs fine laga!")

@bot.message_handler(commands=['daily', 'dart'])
def play_games(message):
    u = get_user(message.from_user)
    cmd = message.text.split()[0].lower()
    
    if cmd == '/daily':
        if time.time() - u['last_daily'] > 86400:
            u['bal'] += 200; u['last_daily'] = time.time(); bot.reply_to(message, "🎁 200 rs mile!")
        else: bot.reply_to(message, "❌ Aaj ka mil gaya sa, kal aana!")
            
    elif cmd == '/dart':
        if u['status'] == "Dead":
            bot.reply_to(message, "☠️ Mare huye log game nahi khel sakte!")
            return
        res = bot.send_dice(message.chat.id, emoji='🎯')
        if res.dice.value >= 4:
            u['bal'] += 100; bot.reply_to(message, "🎯 Bullseye! 100 rs jeete.")
        else:
            u['bal'] -= 50; bot.reply_to(message, "❌ Nishana chooka, 50 rs haare.")

    # REMINDER SYSTEM
    if u['loan']['active'] and u['bal'] >= u['loan']['amount']:
        try: bot.send_message(message.from_user.id, f"🔔 **REMINDER!**\nAapke paas paise aa gaye hain! Apna {u['loan']['amount']} rs ka udhar jaldi chukao!")
        except: pass

# ==========================================
# 7. ADMIN COMMANDS (/kill, /gift)
# ==========================================
@bot.message_handler(commands=['kill'])
def kill_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Reply karke /kill likho!")
        return
    
    t_obj = message.reply_to_message.from_user
    u, admin = get_user(t_obj), get_user(ADMIN_ID)
    
    if u['status'] == "Dead": return
    tax = int(u['bal'] * 0.05)
    u['bal'] -= tax
    u['status'] = "Dead"
    admin['bal'] += 500 
    bot.reply_to(message, f"☠️ **SHIKAAR DONE!**\nAdmin ko 500 rs mile. Target ka 5% ({tax} rs) tax kata!")

@bot.message_handler(commands=['gift'])
def gift_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    if not message.reply_to_message: return
    try:
        amount = int(message.text.split()[1])
        t_obj = message.reply_to_message.from_user
        tax = int(amount * 0.15)
        final = amount - tax
        get_user(t_obj)['bal'] += final
        bot.reply_to(message, f"🎁 **GIFT SENT!**\n📉 Tax (15%): {tax} rs\n✅ Received: {final} rs")
    except: 
        bot.reply_to(message, "❌ Sahi format: /gift 100")

# ==========================================
# 8. MASTER HANDLER (POLICE + AI)
# ==========================================
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    if message.chat.type in ['group', 'supergroup']:
        active_groups.add(message.chat.id)
        
    uid = message.from_user.id
    text = message.text.lower()
    u = get_user(message.from_user)
    
    # POLICE ABUSE DETECTOR
    if any(word in text for word in BAD_WORDS):
        u['bal'] -= 500
        u['warns'] += 1
        bot.reply_to(message, f"🚨 **POLICE ALERT!**\nGaali dene par 500 rs fine laga!\n⚠️ Total Warnings: {u['warns']}")
        return

    # AI RESPONSE
    bot_info = bot.get_me()
    bot_uname = f"@{bot_info.username.lower()}"
    
    if bot_uname in text or (message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id):
        if not check_membership(uid):
            bot.reply_to(message, "🙏 Pehle group join karo sa!")
            return
            
        bot.send_chat_action(message.chat.id, 'typing')
        clean_text = text.replace(bot_uname, "").strip()
        if clean_text: bot.reply_to(message, get_ai_response(clean_text))

# ==========================================
# 9. EXECUTION
# ==========================================
if __name__ == "__main__":
    keep_alive()
    threading.Thread(target=background_monitor, daemon=True).start()
    print("Maha-Bot chalu ho gaya sa!")
    bot.infinity_polling()
    
