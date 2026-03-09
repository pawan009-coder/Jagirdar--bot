import telebot
import time
import random
import requests

# --- CONFIGURATION ---
API_TOKEN = '8625875353:AAECoBaDSeZyLkX21ZNhhCdilnVWhYMLpAY'
GEMINI_API_KEY = 'AIzaSyBM2xs5jGDQHn8MfJDb3II3ijxOfLTaXeg'
ADMIN_ID = 7574760011 
GROUP_USERNAME = "@Daimondbatch" 
bot = telebot.TeleBot(API_TOKEN)

users = {}

# Saari badi gaaliyan yahan add kar di hain
BAD_WORDS = [
    "bc", "mc", "bsdk", "madrachod", "behenchod", "gandu", "chutiya", 
    "lodu", "kamine", "harami", "randi", "saala", "bkl", "mkb"
]

def get_user(uid):
    if uid not in users:
        users[uid] = {"bal": 1000, "status": "Alive", "last_daily": 0, "warns": 0}
    return users[uid]

def check_membership(uid):
    try:
        status = bot.get_chat_member(GROUP_USERNAME, uid).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- SMART AI FUNCTION ---
def get_ai_response(user_text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        # AI ko Instruction: Gaali pehchane aur Jodhpuri bole
        prompt = (f"Tu ek Jodhpuri AI Bot hai. Tera naam 'Jodhpur King' hai. "
                  f"Agar user ne gaali di hai ({user_text}), toh use daant aur mana kar. "
                  f"Nahi toh desi Jodhpuri style mein jawab de. User ne kaha: {user_text}")
        
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, headers=headers, json=data, timeout=5)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        # AI FAIL HONE PAR DEFAULT REPLIES
        return random.choice(["Khamma Ghani Hukum!", "Aur sunao sa, kya haal chaal?", "Jodhpur aao kabhi kachori khilayenge!"])

# --- ALL COMMANDS (Info, Kill, Gift, etc.) ---
@bot.message_handler(commands=['info'])
def info(message):
    try:
        tid = message.reply_to_message.from_user.id if message.reply_to_message else int(message.text.split()[1])
        u = get_user(tid)
        bot.reply_to(message, f"📑 **KHAATA REPORT**\n💰 Bal: {u['bal']}\n❤️ Status: {u['status']}\n⚠️ Warns: {u['warns']}")
    except: bot.reply_to(message, "Format: `/info [ID]`")

@bot.message_handler(commands=['kill'])
def kill(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        tid = int(message.text.split()[1])
        u, admin = get_user(tid), get_user(ADMIN_ID)
        tax = int(u['bal'] * 0.05)
        u['bal'] -= tax
        u['status'] = "Dead"
        admin['bal'] += 500
        bot.reply_to(message, f"☠️ **SHIKAAR!**\nID {tid} khatam. Admin ko 500 mile!")
    except: pass

@bot.message_handler(commands=['gift'])
def gift(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        args = message.text.split()
        tid, amt = int(args[1]), int(args[2])
        tax = int(amt * 0.15)
        final = amt - tax
        get_user(tid)['bal'] += final
        bot.reply_to(message, f"🎁 Gift bhej diya! (Tax: {tax})")
    except: pass

# --- MAIN HANDLER (Gaali & AI) ---
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    if not check_membership(message.from_user.id):
        bot.reply_to(message, f"❌ Pehle group join karo sa: {GROUP_USERNAME}")
        return

    uid = message.from_user.id
    text = message.text.lower()

    # 1. FIXED LIST GAALI CHECK
    if any(word in text for word in BAD_WORDS):
        u = get_user(uid)
        u['bal'] -= 500
        u['warns'] += 1
        bot.reply_to(message, f"🚨 **POLICE ALERT!**\nJodhpur group mein gaali nahi sa!\n💸 500 rs fine kata.\n⚠️ Warnings: {u['warns']}")
        return

    # 2. AI RESPONSE (Isme AI khud bhi gaali pehchan lega)
    bot.send_chat_action(message.chat.id, 'typing')
    response = get_ai_response(message.text)
    bot.reply_to(message, response
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Apne bot.infinity_polling() se upar ye line likho
keep_alive()
bot.infinity_polling()
