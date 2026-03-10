import telebot
from telebot.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
import time
import random
import requests
import os
from flask import Flask
import threading

app = Flask('')
@app.route('/')
def home(): return "Jodhpur King Bot Online!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive(): threading.Thread(target=run).start()

API_TOKEN = '8625875353:AAECoBaDSeZyLkX21ZNhhCdilnVWhYMLpAY'
GEMINI_API_KEY = 'AIzaSyBM2xs5jGDQHn8MfJDb3II3ijxOfLTaXeg'
ADMIN_ID = 7574760011 
GROUP_USERNAME = "@Daimondbatch" 
bot = telebot.TeleBot(API_TOKEN)

bot.set_my_commands([
    BotCommand("start", "Bot chalu karein"),
    BotCommand("bal", "Apna khaata aur level dekhein"),
    BotCommand("daily", "Har 24 ghante ka inam"),
    BotCommand("weekly", "Har 7 din mein 2000 Rs"),
    BotCommand("dart", "Kismat azmayein (/dart amount)"),
    BotCommand("shield", "500 Rs mein 24 ghante bachein (DM)"),
    BotCommand("give", "Kisi ko paise donate karein"),
    BotCommand("udhar", "Loan offer karein"),
    BotCommand("return", "Udhar wapas karein"),
    BotCommand("rob", "Dusre ke paise churayein"),
    BotCommand("kill", "Shikaar karein (500 Rs inam)"),
    BotCommand("revive", "Zinda karein (700 Rs lagenge)"),
    BotCommand("xo", "Tic-Tac-Toe khelein (/xo amount)"),
    BotCommand("ban", "👑 Group se nikalein"),
    BotCommand("mute", "👑 Chup karayein"),
    BotCommand("askpoll", "👑 Daily poll bhejein")
])

users = {}
active_groups = set()
pending_loans = {}
xo_games = {}
poll_voters = set()

def get_level(bal):
    if bal < 500: return "Noob 🪵"
    elif bal < 1500: return "Bronze 🥉"
    elif bal < 3000: return "Silver 🥈"
    elif bal < 4000: return "Gold 🥇"
    elif bal < 10000: return "Platinum 💎"
    elif bal < 50000: return "Diamond 💠"
    elif bal < 2000000: return "Heroic 🦸‍♂️"
    else: return "GOD LEVEL 👑"

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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": f"Tu Jodhpur King bot hai. Desi style mein chota jawab de: {user_text}"}]}], "safetySettings": [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]}
        res = requests.post(url, json=payload, timeout=10).json()
        if 'candidates' in res: return res['candidates'][0]['content']['parts'][0]['text']
        else: return "⚠️ AI Error"
    except: return "🔌 Network issue sa!"

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
    u = get_user(message.from_user)
    bot.reply_to(message, f"🏦 **ACCOUNT: {u['name']}**\n🏆 Level: {get_level(u['bal'])}\n💰 Balance: {u['bal']} Rs\n❤️ Status: {u['status']}")

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

@bot.message_handler(commands=['dart'])
def play_dart(message):
    u = get_user(message.from_user)
    if u['status'] == "Dead": return bot.reply_to(message, "Murde nahi khelte!")
    try:
        amt = int(message.text.split()[1])
        if u['bal'] < amt: return bot.reply_to(message, "Itne paise nahi hain!")
        if random.random() <= 0.60:
            u['bal'] += amt
            bot.reply_to(message, f"🎯 Bullseye! Aap {amt} Rs jeet gaye. Double paisa!")
        else:
            u['bal'] -= amt
            bot.reply_to(message, f"❌ Nishana chooka! Aap {amt} Rs haar gaye.")
    except: bot.reply_to(message, "Format: /dart 100")
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
    
    # 🛡️ Admin Unlimited Shield Check
    if t_obj.id == ADMIN_ID: 
        return bot.reply_to(message, "👑 **Aukaat mein reh!** Admin ke paas Unlimited Shield hai, use koi nahi loot sakta!")
        
    # Normal User Shield Check
    if time.time() < t['shield_until']: 
        return bot.reply_to(message, "🛡️ Target protected hai (Shield Active)!")
    
    # Paise check karna
    if t['bal'] < loot_amt: 
        return bot.reply_to(message, f"Arey iske paas itne paise hi nahi hain! Iske paas sirf {t['bal']} Rs bache hain.")
    
    # 50% chance, BINa POLICE FINE KE
    if random.choice([True, False]): 
        tax = int(loot_amt * 0.05) # 5% tax
        t['bal'] -= loot_amt
        r['bal'] += (loot_amt - tax)
        bot.reply_to(message, f"🥷 **ROB SUCCESS!**\nAapne {loot_amt} Rs loote. 5% Tax ({tax} Rs) cut hua, aapko mile {loot_amt - tax} Rs! 💰")
    else:
        # Koi fine nahi katega
        bot.reply_to(message, f"❌ **ROB FAILED!**\nChori nakam rahi! Target bach nikla. (Aap par koi fine nahi laga).")
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

@bot.message_handler(commands=['udhar'])
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
