import telebot
import requests
import os
import time
from flask import Flask
import threading

# --- [دریافت توکن‌ها از Environment رندر] ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# دستورالعمل گنج‌یابی ۱۸ ساعته
MASTER_INSTRUCTIONS = "تو معمارِ مستر هستی. بر اساس فیلترهای ثروت، قدرت و راحتی، گنج‌های محصول را استخراج کن."

# --- [بخش وب برای زنده نگه داشتن سرور] ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Running!", 200

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_gemini(user_message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": f"{MASTER_INSTRUCTIONS}\n\nتحلیل کن: {user_message}"}]}]}
    try:
        response = requests.post(url, json=payload, timeout=30)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "❌ خطا در اتصال به هوش مصنوعی."

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🏛 معمارِ مستر آنلاین شد! محصولت چیه؟")

@bot.message_handler(func=lambda m: True)
def handle(message):
    bot.send_chat_action(message.chat.id, 'typing')
    reply = ask_gemini(message.text)
    bot.reply_to(message, reply)

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling()

if __name__ == "__main__":
    # اجرای ربات در یک رشته جداگانه
    threading.Thread(target=run_bot).start()
    # اجرای Flask روی پورت رندر
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
