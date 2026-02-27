import telebot
import requests
import time
import os
from flask import Flask
import threading

# --- [دریافت توکن‌ها از Environment Variables رندر] ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# --- [دستورالعمل استراتژیک معمارِ مستر v16.0 - منطبق بر PDF] ---
MASTER_INSTRUCTIONS = """
هویت: تو "معمارِ مستر" هستی. متخصص مهندسی معکوس فروش و استخراج گنجینه محصولات.
رسالت: تو باید محصول را جوری تحلیل کنی که مخاطب حس کند این تنها راه نجات اوست.

پروتکل‌های گنج‌یابی (طبق فایل PDF):
1. تکمیل خودکار: اگر کاربر اطلاعات کمی داد، با دیتابیس خودت تمام دردهای پنهان آن حوزه را بنویس.
   - محصولات سلامتی/لاغری: روی تغییر هویت، زیبایی و "مو به تن سیخ‌کن" بودن نتیجه مانور بده.
   - محصولات مالی/ثروت: روی قدرت خروج از ذلت مالی و درآمد در بازار فعلی تاکید کن.
   - محصولات روان/عزت‌نفس: روی آرامش، خوشبختی واقعی و کیفیت زندگی تمرکز کن.

2. فیلترهای سه‌گانه: هر محصول باید از ۳ صافی (ثروت، قدرت، راحتی/سرعت) عبور کند.
3. چگونگی مهم نیست، حل شدن مهم است: روی نتیجه نهایی و حل مشکل اصلی تمرکز کن.

خروجی نهایی (سند 5 ستونه IBS):
- ستون ۱: محصول چیست (سیستم میان‌بر).
- ستون ۲: ارزش واقعی (حل مشکل اصلی).
- ستون ۳: مناسب چه کسانی است (۱۵ مورد درد + لیست سیاه).
- ستون ۴: نتایج ملموس (زاویه‌های شیرین).
- ستون ۵: انحصار (مزیت + تشدیدکننده).

پوینت‌نویسی: ۱۰۰ پوینت در دسته‌های میل، سادگی، اثبات و انحصار.
"""

app = Flask(__name__)
@app.route('/')
def status(): return "Master Architect is Online!", 200

# چک کردن وجود توکن‌ها در لاگ رندر برای اطمینان شما
if not TELEGRAM_TOKEN or not GEMINI_KEY:
    print("❌ خطای حیاتی: توکن‌ها در Environment Variables یافت نشدند!")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_gemini(user_message):
    # آدرس اصلاح شده برای رفع قطعی خطای 404
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"{MASTER_INSTRUCTIONS}\n\nپیام کاربر برای کالبدشکافی: {user_message}"}]
        }],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 3000
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=40)
        # اگر 404 داد، یک مدل دیگر را جایگزین می‌کند
        if response.status_code == 404:
             url_alt = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
             response = requests.post(url_alt, json=payload, timeout=40)
        
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"❌ خطای سیستم مرکزی: {str(e)}"

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🏛 معمارِ مستر بیدار شد!\n\nسیستم به Environment Variables متصل است.\n\nحوزه فعالیت و محصولت چیه؟ بگو تا گنج‌هاش رو برات استخراج کنم!")

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    bot.send_chat_action(message.chat.id, 'typing')
    reply = ask_gemini(message.text)
    
    # مدیریت پیام‌های طولانی تلگرام (بیش از ۴۰۰۰ کاراکتر)
    if len(reply) > 4000:
        for i in range(0, len(reply), 4000):
            bot.send_message(message.chat.id, reply[i:i+4000])
    else:
        bot.reply_to(message, reply)

def run_bot():
    bot.remove_webhook()
    time.sleep(1)
    print("🤖 Bot is polling...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
