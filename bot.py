import os
import time
import threading
import requests
from flask import Flask, request
import telebot

API_TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Alive!"

# Webhook Route
@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Bad Request', 403

# Simple Handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎉 Bot working hai bhai!")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"Tumne likha: {message.text}")

def set_webhook():
    bot.remove_webhook()
    time.sleep(1)
    # Render की असली URL एनवायरनमेंट से लेना
    render_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"
    webhook_url = f"{render_url}/{API_TOKEN}"
    bot.set_webhook(url=webhook_url)
    print(f"✅ Webhook set to {webhook_url}")

if __name__ == '__main__':
    set_webhook()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
