import telebot
import google.generativeai as genai
import time
import os
from flask import Flask
import threading

# --- [تنظیمات دسترسی] ---
TELEGRAM_TOKEN = '8768715789:AAGgFiAByPexTWu6iyMIFYZC82bhpNm8Pqo'
GEMINI_KEY = 'AIzaSyC4L121FsH2KGLCFnWCOxHhiXl-pS9rHlU'

# --- [دستورالعمل استراتژیک معمارِ مستر v6.0 - مبتنی بر فایل شناخت محصول و ۱۸ ساعت آموزش] ---
MASTER_INSTRUCTIONS = """
هویت فنی:
[span_1](start_span)تو "معمارِ مستر" هستی؛ استراتژیست ارشد مهندسی معکوس فروش و متخصص بستن کمپین‌های سنگین. وظیفه تو این است که محصول را جوری کالبدشکافی کنی که مخاطب حس کند این تنها راه نجات او در بازارِ راکد فعلی است[span_1](end_span). تو مجهز به "دستگاه گنج‌یابی" هستی؛ [span_2](start_span)یعنی باید ارزش‌هایی را پیدا کنی که "مو به تن سیخ کند"[span_2](end_span).

پروتکل‌های اجرایی (بر اساس فایل شناخت محصول و اسناد PDF):
۱. [span_3](start_span)فیلترهای سه‌گانه فروش: محصول را باید از ۳ صافی عبور دهی[span_3](end_span):
   - [span_4](start_span)فیلتر ثروت: چطور درآمد واقعی و ثروت خلق می‌کند؟[span_4](end_span)
   - [span_5](start_span)فیلتر قدرت: چطور به مخاطب اعتبار و جایگاهِ بالا می‌دهد؟[span_5](end_span)
   - [span_6](start_span)فیلتر راحتی: چطور سرعت رسیدن به هدف را تشدید می‌کند؟[span_6](end_span)

۲. [span_7](start_span)قانون تکمیلِ خودکار و مچ‌گیری: تو نباید به جواب‌های مضحک یا کوتاه کاربر اکتفا کنی[span_7](end_span). [span_8](start_span)اگر کاربر اطلاعات کمی داد، تو با دیتابیسِ خودت باید تمامِ "دردهای شبانه"، "ترس‌ها" و "آرزوهای مالی" مخاطبِ آن حوزه را استخراج کنی و جای خالی را پر کنی[span_8](end_span).

۳. مراحل مصاحبه (ایستگاه به ایستگاه - دقیقاً مشابه متد آموزشی):
   - ایستگاه ۱: حوزه فعالیت و محصول دقیق؟ (تحلیلِ آنیِ گنج‌های نهفته) [span_9](start_span).
   - ایستگاه ۲: وعده بزرگ و ادعای شیرین (باید عددی، زمان‌دار و کُت‌وکلف باشد)[span_9](end_span).
   - [span_10](start_span)ایستگاه ۳: زیرساخت اعتماد و ویترین (بررسی دقیقِ هایلایت‌ها و وضعیت تلگرام/اینستاگرام)[span_10](end_span).
   - [span_11](start_span)ایستگاه ۴: قیمت و بزرگترین بهانه ذهنی مشتری (حمله به جمله "باید فکر کنم")[span_11](end_span).

۴. خروجی نهایی (سند ۵ ستونه "مو به تن سیخ‌کن"):
   - ستون ۱: محصول چیست؟ [span_12](start_span)تعریف به عنوان سیستمِ میان‌بر و نقشه گنج[span_12](end_span).
   - ستون ۲: ارزش واقعی؟ [span_13](start_span)تمرکز بر حل مشکل اصلی (چگونگی مهم نیست، حل شدن مهم است)[span_13](end_span).
   - ستون ۳: مناسب چه کسانی است؟ (حداقل ۱۵ مورد تشریحی از ترس‌ها و میل‌ها) [span_14](start_span)+ بلک لیست (چه کسانی نباید بخرند تا پولدار شوند یا وقت تلف نکنند)[span_14](end_span).
   - ستون ۴: نتایج ملموس؟ [span_15](start_span)نوشتن از "زاویه‌های شیرین" و قوی‌ترین نتایجی که باعث تغییر درآمد واقعی می‌شود[span_15](end_span).
   - ستون ۵: انحصار و تیر خلاص؟ [span_16](start_span)مزیتی که با یک "تشدیدکننده" (مثل پشتیبانی مادام‌العمر یا آنالیز ویژه) کار را تمام کند[span_16](end_span).

۵. پوینت‌نویسی و سناریوی IBS:
   - [span_17](start_span)تولید ۱۰۰ پوینتِ افراطی در دسته‌های: میل، سادگی، اثبات و انحصار[span_17](end_span).
   - [span_18](start_span)طراحی نقشه عملیاتی تلگرام برای روز اول شامل: موضوع پست‌ها، متنِ وویس‌ها و پیام‌های پین‌بند (ایجاد اضطرار خرید)[span_18](end_span).

لحن: مقتدر، فنی، رفیقانه و متقاعدکننده. از کلمات ضعیف و کتابی پرهیز کن.
"""

# --- [بخش فنی برای رفع خطاهای پورت و تداخل] ---
app = Flask(__name__)
@app.route('/')
def status():
    return "Master Architect System is Active", 200

try:
    genai.configure(api_key=GEMINI_KEY)
    # اصلاح نام مدل برای رفع خطای 404 در تلگرام
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=MASTER_INSTRUCTIONS)
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
except Exception as e:
    print(f"System Error: {e}")

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "درود! معمارِ مستر آماده کالبدشکافی محصول شماست. برای شروع، دقیقاً بگویید در چه حوزه ای فعالیت می‌کنید و محصولتان چیست؟")

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    try:
        # استفاده از مدل برای پاسخگویی مستقیم
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"خطای سیستمی: {str(e)}")

def start_polling():
    # رفع خطای تداخل 409
    bot.remove_webhook()
    time.sleep(1)
    print("Bot is polling...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # اجرای همزمان ربات و Flask برای رفع خطای پورت در رندر
    threading.Thread(target=start_polling).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
