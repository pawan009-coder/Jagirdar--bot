import telebot
import time
import random
import requests
import os
from flask import Flask
from threading import Thread

# --- STEP 1: RENDER KE LIYE SERVER SETUP (Bina iske bot band ho jayega) ---
app = Flask('')

@app.route('/')
def home():
    return "Jodhpur King Bot is Online and Running!"

def run():
    # Render ke liye port setup
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- STEP 2: BOT CONFIGURATION ---
API_TOKEN = '8625875353:AAECoBaDSeZyLkX21ZNhhCdilnVWhYMLpAY'
GEMINI_API_KEY = 'AIzaSyBM2xs5jGDQHn8MfJDb3II3ijxOfLTaXeg'
ADMIN_ID = 7574760011 
GROUP_USERNAME = "@Daimondbatch" 
bot = telebot.TeleBot(API_TOKEN)

# Temporary Database
users = {}

# Gaaliyon ki badi list
BAD_WORDS = [
    "bc", "mc", "bsdk", "madrachod", "behenchod", "gandu", "chutiya", 
    "lodu", "kamine", "harami", "randi", "saala", "bkl", "mkb", "suar"
]

# Helper Function
def get_user(uid):
    if uid not in users:
        users[uid] = {"bal": 1000, "status": "Alive", "last_daily": 0, "warns": 0}
    return users[uid]

def check_membership(uid):
    try:
        status = bot.get_chat_member(GROUP_USERNAME, uid).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# --- STEP 3: ASLI AI LOGIC (GEMINI) ---
def get_ai_response(user_text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        prompt = (f"Tu ek Jodhpuri AI Bot hai jiska naam 'Jodhpur King' hai. "
                  f"User ne kaha: {user_text}. Tu hamesha desi Jodhpuri dhang se baat kar "
                  f"aur chote-mazedaar jawab de. Agar user gaali de toh use sharam dila.")
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, headers=headers, json=data, timeout=5)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return random.choice(["Khamma Ghani Hukum!", "Aur sunao sa, kya haal chaal?", "Jodhpur ki kachori khaoge?"])

# --- STEP 4: COMMANDS (INFO, KILL, GIFT, DAILY, DART) ---

@bot.message_handler(commands=['start'])
def start_msg(message):
    uid = message.from_user.id
    get_user(uid)
    bot.reply_to(message, "👑 **Khamma Ghani Hukum!**\nMain hoon Jodhpur King Bot. Game khelne aur baat karne ke liye taiyar ho jao sa!\n\nCommands: /info, /daily, /dart, /gift, /kill")

@bot.message_handler(commands=['info'])
def check_info(message):
    try:
        if message.reply_to_message:
            target_id = message.reply_to_message.from_user.id
        else:
            target_id = int(message.text.split()[1])
        u = get_user(target_id)
        bot.reply_to(message, f"📑 **KHAATA REPORT (ID: {target_id})**\n💰 Balance: {u['bal']} rs\n❤️ Status: {u['status']}\n⚠️ Warnings: {u['warns']}\n📅 Status: Zinda", parse_mode="Markdown")
    except:
        bot.reply_to(message, "Format: `/info [User_ID]` ya reply karke `/info` likho.")

@bot.message_handler(commands=['kill'])
def kill_user(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        target_id = int(message.text.split()[1])
        u = get_user(target_id)
        admin = get_user(ADMIN_ID)
        if u['status'] == "Dead":
            bot.reply_to(message, "Hukum, wo pehle se mara hua hai.")
            return
        tax = int(u['bal'] * 0.05)
        u['bal'] -= tax
        u['status'] = "Dead"
        admin['bal'] += 500  # Admin Reward
        bot.send_message(message.chat.id, f"☠️ **SHIKAAR!**\nID {target_id} ko kill kar diya.\n💸 5% Tax kata: {tax}\n💰 Admin ko 500 rs reward mila!")
    except:
        bot.reply_to(message, "Format: `/kill [ID]`")

@bot.message_handler(commands=['gift'])
def gift_money(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        args = message.text.split()
        target_id, amount = int(args[1]), int(args[2])
        tax = int(amount * 0.15)
        final = amount - tax
        get_user(target_id)['bal'] += final
        bot.reply_to(message, f"🎁 **GIFT BHEJA!**\nID: {target_id}\nAmount: {amount}\n📉 Tax (15%): {tax}\n✅ Received: {final}")
    except:
        bot.reply_to(message, "Format: `/gift [ID] [Amount]`")

@bot.message_handler(commands=['daily'])
def daily_reward(message):
    u = get_user(message.from_user.id)
    if time.time() - u['last_daily'] < 86400:
        bot.reply_to(message, "Sabar rakho sa! Daily reward har 24 ghante mein milta hai.")
    else:
        u['bal'] += 200
        u['last_daily'] = time.time()
        bot.reply_to(message, "🎁 Lo sa, 200 rs Jodhpur ki taraf se bhent!")

@bot.message_handler(commands=['dart'])
def play_dart(message):
    u = get_user(message.from_user.id)
    if u['status'] == "Dead":
        bot.reply_to(message, "☠️ Mare huye log game nahi khel sakte sa!")
        return
    res = bot.send_dice(message.chat.id, emoji='🎯')
    if res.dice.value >= 4:
        u['bal'] += 100
        bot.reply_to(message, "🎯 Bullseye! 100 rs munaafa.")
    else:
        u['bal'] -= 50
        bot.reply_to(message, "❌ Nishana chooka, 50 rs nuksaan!")

# --- STEP 5: POLICE & AI CHAT HANDLER ---

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    # Force Join Check
    if not check_membership(message.from_user.id):
        bot.reply_to(message, f"🙏 Khamma Ghani! Pehle hamara group join karo sa tabhi entry milegi.\nJoin: {GROUP_USERNAME}")
        return

    uid = message.from_user.id
    text = message.text.lower()

    # 1. Police/Gaali Check
    if any(word in text for word in BAD_WORDS):
        u = get_user(uid)
        u['bal'] -= 500
        u['warns'] += 1
        bot.reply_to(message, f"🚨 **POLICE ALERT!** 🚨\nBadtameezi ke liye 500 rs fine kata!\n⚠️ Total Warnings: {u['warns']}")
        return

    # 2. AI Conversation
    bot.send_chat_action(message.chat.id, 'typing')
    ai_msg = get_ai_response(message.text)
    bot.reply_to(message, ai_msg)

# --- STEP 6: EXECUTION ---
if __name__ == "__main__":
    keep_alive()  # Start Flask server
    print("Jodhpur King Bot is starting...")
    bot.infinity_polling()
    
