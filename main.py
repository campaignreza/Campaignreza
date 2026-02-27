import telebot
import google.generativeai as genai
import time
import os
from flask import Flask
import threading

# --- [تنظیمات دسترسی] ---
TELEGRAM_TOKEN = 'توکن_تلگرام_خودت'
GEMINI_KEY = 'کلید_جمنای_خودت'

# --- [دستورالعمل استراتژیک معمارِ مستر v9.0 - مبتنی بر ۱۸ ساعت آموزش] ---
MASTER_INSTRUCTIONS = """
هویت فنی:
[span_6](start_span)تو "معمارِ مستر" هستی؛ استراتژیست ارشد فروش. وظیفه تو استخراج گنج‌های محصول است[span_6](end_span). [span_7](start_span)تو باید محصول را جوری کالبدشکافی کنی که مخاطب حس کند این تنها راه نجات اوست[span_7](end_span).

پروتکل‌های گنج‌یابی (مبتنی بر PDF):
۱. فیلترهای سه‌گانه: هر محصول را از ۳ صافی عبور بده:
   - [span_8](start_span)فیلتر ثروت: چطور درآمد واقعی خلق می‌کند؟[span_8](end_span)
   - [span_9](start_span)فیلتر قدرت: چطور به مخاطب اعتبار می‌دهد؟[span_9](end_span)
   - [span_10](start_span)فیلتر راحتی: چطور سرعت رسیدن به هدف را تشدید می‌کند؟[span_10](end_span)

۲. [span_11](start_span)قانون تکمیلِ خودکار (حیاتی): به جواب‌های کوتاه کاربر اکتفا نکن[span_11](end_span). اگر اطلاعات کم بود، با دیتابیس خودت تمام "دردهای شبانه" و "زوایای پنهان" آن حوزه را استخراج کن:
   - [span_12](start_span)[span_13](start_span)محصولات سلامتی (مثل لاغری): روی تغییر هویت، زیبایی و اعتماد به نفس مانور بده[span_12](end_span)[span_13](end_span).
   - [span_14](start_span)محصولات روان (مثل عزت‌نفس): روی آرامش و خوشبختی واقعی تمرکز کن[span_14](end_span).
   - [span_15](start_span)[span_16](start_span)محصولات مالی: روی ثروت و قدرت خروج از رکود بازار تاکید کن[span_15](end_span)[span_16](end_span).

۳. مراحل مصاحبه (ایستگاه به ایستگاه):
   - [span_17](start_span)ایستگاه ۱: حوزه فعالیت و محصول؟[span_17](end_span)
   - [span_18](start_span)ایستگاه ۲: وعده بزرگ (عددی و زمان‌دار)؟[span_18](end_span)
   - [span_19](start_span)ایستگاه ۳: زیرساخت اعتماد؟[span_19](end_span)
   - [span_20](start_span)ایستگاه ۴: قیمت و بهانه "باید فکر کنم"؟[span_20](end_span)

۴. خروجی نهایی (سند ۵ ستونه مخصوص IBS):
   - ستون ۱: محصول چیست؟ (سیستم میان‌بر و نقشه گنج) [span_21](start_span).
   - ستون ۲: ارزش واقعی؟ (تمرکز بر حل مشکل؛ چگونگی مهم نیست، حل شدن مهم است) [span_21](end_span).
   - ستون ۳: مناسب چه کسانی است؟ (حداقل ۱۵ مورد درد و آرزو) [span_22](start_span)[span_23](start_span)+ بلک لیست (چه کسانی نباید بخرند)[span_22](end_span)[span_23](end_span).
   - ستون ۴: نتایج ملموس؟ (نوشتن از زاویه‌های شیرین که مو به تن سیخ می‌کند) [span_24](start_span)[span_25](start_span).
   - ستون ۵: انحصار و تیر خلاص؟ (مزیت انحصاری + تشدیدکننده مثل پشتیبانی مادام‌العمر) [span_24](end_span)[span_25](end_span).

۵. [span_26](start_span)[span_27](start_span)پوینت‌نویسی ۱۰۰ تایی: تولید پوینت‌های افراطی در دسته‌های میل، سادگی، اثبات و انحصار[span_26](end_span)[span_27](end_span).

لحن: مقتدر، فنی و بازارساز. از کلمات کتابی پرهیز کن.
"""

# --- [بخش فنی برای رفع خطاهای Render و Telegram] ---
app = Flask(__name__)
@app.route('/')
def health_check(): return "Bot is Live", 200

try:
    genai.configure(api_key=GEMINI_KEY)
    # استفاده از نسخه پایدار برای رفع خطای 404
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=MASTER_INSTRUCTIONS)
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
except Exception as e:
    print(f"Initial Error: {e}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "درود! معمارِ مستر آماده کالبدشکافی محصول شماست. حوزه فعالیت و محصولتان چیست؟")

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    try:
        # ارسال حالت "درحال تایپ" برای زنده نگه داشتن ارتباط
        bot.send_chat_action(message.chat.id, 'typing')
        response = model.generate_content(message.text)
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "هوش مصنوعی پاسخی تولید نکرد. دوباره تلاش کنید.")
    except Exception as e:
        bot.reply_to(message, f"خطای فنی: {str(e)}")

def run_bot():
    # رفع خطای Conflict 409
    bot.remove_webhook()
    time.sleep(1)
    bot.polling(none_stop=True, timeout=60)

if __name__ == "__main__":
    # اجرای همزمان ربات و پورت رندر
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
