import telebot
import requests
import time
import os
from flask import Flask
import threading

# --- [خواندن توکن‌ها از تنظیمات رندر] ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# --- [دستورالعمل استراتژیک معمارِ مستر v15.0 - طبق فایل PDF] ---
MASTER_INSTRUCTIONS = """
هویت: تو "معمارِ مستر" هستی. استراتژیست ارشد مهندسی معکوس فروش (دوره ۱۸ ساعته).
وظیفه: کالبدشکافی محصول و پیدا کردن گنجینه‌های نهفته برای "مو به تن سیخ کردن" مخاطب.

پروتکل‌های حیاتی (بر اساس فایل شناخت محصول):
۱. تکمیل خودکار: اگر کاربر اطلاعات کمی داد، تو با دیتابیس خودت تمام دردهای پنهان آن حوزه را استخراج کن.
   - محصولات سلامتی (لاغری): روی تغییر هویت و زیبایی مانور بده.
   - محصولات روان (عزت نفس): روی آرامش و خوشبختی واقعی تمرکز کن.
   - محصولات مالی: روی خروج از ذلت مالی و رسیدن به ثروت در بازار فعلی تاکید کن.

۲. فیلترهای سه‌گانه: هر تحلیل باید از صافی "ثروت"، "قدرت" و "راحتی (سرعت)" عبور کند.
۳. متد IBS: خروجی باید برای پست‌ها، وویس‌ها و پیام‌های پین‌بند روز اول کمپین آماده باشد.
۴. خروجی ۵ ستونه: محصول چیست، ارزش واقعی، مخاطب‌شناسی (۱۵ درد)، نتایج ملموس (زاویه شیرین)، و انحصار.

لحن: مقتدر، فنی، رفیقانه و بازارساز.
"""

app = Flask(__name__)
@app.route('/')
def health(): return "Master Architect is Live and Linked!", 200

# چک کردن وجود توکن‌ها در لاگ رندر
if not TELEGRAM_TOKEN or not GEMINI_KEY:
    print("❌ خطا: توکن‌ها در Environment Variables پیدا نشدند!")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_gemini(user_message):
    # استفاده از متد Requests برای پایداری ۱۰۰٪ در محیط رندر
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{
            "role": "user", 
            "parts": [{"text": f"{MASTER_INSTRUCTIONS}\n\nپیام کاربر برای تحلیل: {user_message}"}]
        }]
    }
    response = requests.post(url, json=payload, timeout=40)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"❌ خطای ارتباط با هوش مصنوعی ({response.status_code}):\n{response.text}"

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🏛 معمارِ مستر با موفقیت به Environment Variables متصل شد!\n\nآماده کالبدشکافی محصول هستیم. حوزه فعالیت و محصولت چیه؟")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        reply = ask_gemini(message.text)
        # مدیریت پیام‌های خیلی طولانی تلگرام
        if len(reply) > 4000:
            for i in range(0, len(reply), 4000):
                bot.send_message(message.chat.id, reply[i:i+4000])
        else:
            bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"⚠️ خطای غیرمنتظره: {str(e)}")

def start_bot():
    bot.remove_webhook()
    time.sleep(1)
    print("🤖 Bot is polling...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    # استفاده از پورت پیش‌فرض رندر
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
