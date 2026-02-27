import telebot
import google.generativeai as genai
import time
import os
from flask import Flask
import threading

# --- [تنظیمات دسترسی - توکن‌های خودت را اینجا بگذار] ---
TELEGRAM_TOKEN = '8768715789:AAGgFiAByPexTWu6iyMIFYZC82bhpNm8Pqo'
GEMINI_KEY = 'AIzaSyC4L121FsH2KGLCFnWCOxHhiXl-pS9rHlU'

# --- [دستورالعمل استراتژیک معمارِ مستر v12.0 - مبتنی بر PDF] ---
MASTER_INSTRUCTIONS = """
هویت: تو "معمارِ مستر" هستی؛ استراتژیست ارشد مهندسی معکوس فروش.
رسالت: تو باید محصول را کالبدشکافی کنی تا "گنج" آن پیدا شود. اگر گنج نداشت، در روند تحلیل برایش گنج بساز.

قوانین تحلیل (بر اساس فایل شناخت محصول):
1. تکمیل خودکار: به جواب‌های کوتاه اکتفا نکن. با دیتابیس خودت تمام دردهای پنهان حوزه را بیرون بکش.
   - سلامتی (لاغری): روی تغییر هویت و اعتماد به نفس متمرکز شو.
   - ثروت: روی درآمد بالا در وضع فعلی بازار مانور بده.
   - روابط (عزت نفس): روی آرامش و خوشبختی واقعی متمرکز شو.
2. فیلترهای سه‌گانه: محصول را از ۳ صافی "ثروت"، "قدرت" و "راحتی (سرعت)" عبور بده.
3. چگونگی مهم نیست، حل شدن مهم است: روی نتیجه نهایی و حل مشکل اصلی مخاطب تمرکز کن.

خروجی نهایی (سند 5 ستونه IBS):
- ستون ۱: محصول چیست (سیستم میان‌بر).
- ستون ۲: ارزش واقعی (حل مشکل اصلی).
- ستون ۳: مناسب چه کسانی است (حداقل ۱۵ مورد درد و آرزو) + بلک لیست (چه کسانی نباید بخرند).
- ستون ۴: نتایج ملموس (زاویه‌های شیرین که مو به تن سیخ می‌کند).
- ستون ۵: انحصار (مزیت + تشدیدکننده مثل پشتیبانی مادام‌العمر).

POINT نویسی: تولید ۱۰۰ پوینت در دسته‌های میل، سادگی، اثبات و انحصار.
"""

app = Flask(__name__)
@app.route('/')
def status(): return "Master Architect System is LIVE!", 200

# جلوگیری از خطاهای احتمالی در تعریف ربات
try:
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    genai.configure(api_key=GEMINI_KEY)
    # رفع خطای 404 با استفاده از نسخه پایدار
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=MASTER_INSTRUCTIONS)
except Exception as e:
    print(f"Error in setup: {e}")

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "درود! معمارِ مستر آماده کالبدشکافی محصول شماست. حوزه فعالیت و محصولتان چیست؟")

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"خطای سیستمی: {str(e)}")

def start_polling():
    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=start_polling).start()
    # استفاده از پورت پیش‌فرض رندر
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
