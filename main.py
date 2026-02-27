import telebot
import requests
import time
import os
from flask import Flask
import threading

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
GEMINI_KEY = os.environ.get('GEMINI_KEY', '')
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

MASTER_INSTRUCTIONS = """
هویت و رسالت:
تو "معمارِ مستر" هستی؛ یک متفکر استراتژیک و مهندسِ معکوسِ کمپین‌های فروش سنگین.
وظیفه تو استخراج "گنجینه" از دل محصولاتی است که دیگران معمولی می‌بینند.
تو باید محصول را به گونه‌ای بازتعریف کنی که مخاطب احساس کند این تنها راه فرار از رکود
و رسیدن به خوشبختی، سلامتی یا ثروت است.

لایه‌های تحلیلی اجباری:

۱. دستگاه گنج‌یابی:
   - در محصولات مالی (فارکس، سرمایه‌گذاری): روی ثروت، قدرت و خروج از ذلت مالی تمرکز کن.
   - در محصولات سلامتی و زیبایی (لاغری، پوست): روی تغییر هویت و اعتماد به نفس تمرکز کن.
   - در محصولات روابط و روان (عزت نفس): روی آرامش و کیفیت زندگی مانور بده.

۲. فیلترهای سه‌گانه (اجباری):
   - فیلتر ثروت: چطور باعث رشد مالی یا صرفه‌جویی عظیم می‌شود؟
   - فیلتر قدرت: چطور جایگاه اجتماعی فرد را بالا می‌برد؟
   - فیلتر راحتی: چطور سختی‌ها را حذف می‌کند؟

۳. پروتکل مصاحبه (ایستگاه به ایستگاه):
   - ایستگاه ۱: حوزه فعالیت و محصول؟
   - ایستگاه ۲: وعده بزرگ و ادعای شیرین؟ (عددی و خیره‌کننده)
   - ایستگاه ۳: ویترین و اعتمادسازی؟
   - ایستگاه ۴: قیمت و بهانه "باید فکر کنم"؟

۴. خروجی نهایی - سند ۵ ستونه:
   - ستون ۱: تعریف محصول به عنوان "سیستم میان‌بر" و "ناجی"
   - ستون ۲: حمله به مشکل اصلی
   - ستون ۳: مخاطب‌شناسی - حداقل ۱۵ درد شبانه + بلک لیست
   - ستون ۴: نتایج ملموس از زاویه تغییر هویت
   - ستون ۵: مزیت انحصاری + تشدیدکننده

۵. انفجار محتوا:
   - ۱۰۰ پوینت استراتژیک در دسته‌های میل، سادگی، اثبات، انحصار
   - نقشه IBS تلگرام با سناریوی وویس و پیام پین‌بند

لحن: مقتدر، رفیقانه و فنی. برای فروختن ساخته شده‌ای!
"""

app = Flask(__name__)

@app.route('/')
def health():
    return "Master Architect v7.0 is Live!", 200

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# تاریخچه مکالمه هر کاربر
user_history = {}

def ask_gemini(user_id, user_message):
    """ارسال پیام به Gemini API با REST مستقیم"""
    if user_id not in user_history:
        user_history[user_id] = []
    
    user_history[user_id].append({
        "role": "user",
        "parts": [{"text": user_message}]
    })
    
    payload = {
        "system_instruction": {
            "parts": [{"text": MASTER_INSTRUCTIONS}]
        },
        "contents": user_history[user_id],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 8192
        }
    }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    
    data = response.json()
    reply = data['candidates'][0]['content']['parts'][0]['text']
    
    user_history[user_id].append({
        "role": "model",
        "parts": [{"text": reply}]
    })
    
    # حفظ حداکثر ۲۰ پیام آخر
    if len(user_history[user_id]) > 20:
        user_history[user_id] = user_history[user_id][-20:]
    
    return reply

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_history.pop(user_id, None)
    bot.reply_to(message,
        "🏛 *معمارِ مستر v7.0 آنلاین است!*\n\n"
        "سیستم کالبدشکافی محصول فعال شد.\n\n"
        "🎯 حوزه فعالیتت چیه و چه محصولی داری؟\n"
        "من تمام پتانسیل پنهانش رو بیرون می‌کشم! 💰",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['reset'])
def reset(message):
    user_history.pop(message.from_user.id, None)
    bot.reply_to(message, "🔄 سشن ریست شد!")

@bot.message_handler(func=lambda m: True)
def handle(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        reply = ask_gemini(message.from_user.id, message.text)
        if len(reply) > 4096:
            for i in range(0, len(reply), 4096):
                bot.reply_to(message, reply[i:i+4096])
                time.sleep(0.3)
        else:
            bot.reply_to(message, reply)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, f"⚠️ خطا: {str(e)[:200]}")

def run_polling():
    print("🤖 Bot started...")
    while True:
        try:
            bot.remove_webhook()
            time.sleep(1)
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_polling, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
