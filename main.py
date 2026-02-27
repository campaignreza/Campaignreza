import telebot
import requests
import time
import os
from flask import Flask
import threading

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
GEMINI_KEY = os.environ.get('GEMINI_KEY', '')

# لاگ برای دیباگ
print(f"🔑 GEMINI_KEY loaded: {GEMINI_KEY[:10]}..." if GEMINI_KEY else "❌ GEMINI_KEY is empty!")
print(f"🤖 TELEGRAM_TOKEN loaded: {TELEGRAM_TOKEN[:10]}..." if TELEGRAM_TOKEN else "❌ TELEGRAM_TOKEN is empty!")

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
user_history = {}
ACTIVE_MODEL = None

def get_available_model():
    models = [
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
    ]
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
            test_payload = {
                "contents": [{"role": "user", "parts": [{"text": "test"}]}]
            }
            r = requests.post(url, json=test_payload, timeout=15)
            print(f"Model {model}: status {r.status_code}")
            if r.status_code == 200:
                print(f"✅ Active model: {model}")
                return model
        except Exception as e:
            print(f"❌ Model {model} error: {e}")
    return None


def ask_gemini(user_id, user_message):
    global ACTIVE_MODEL
    if ACTIVE_MODEL is None:
        ACTIVE_MODEL = get_available_model()
        if ACTIVE_MODEL is None:
            return "❌ هیچ مدل Gemini در دسترس نیست. کلید API را چک کن."

    if user_id not in user_history:
        user_history[user_id] = []
        first_message = MASTER_INSTRUCTIONS + "\n\n" + user_message
        user_history[user_id].append({
            "role": "user",
            "parts": [{"text": first_message}]
        })
    else:
        user_history[user_id].append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

    payload = {
        "contents": user_history[user_id],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 2048
        }
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{ACTIVE_MODEL}:generateContent?key={GEMINI_KEY}"
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()

    data = response.json()
    reply = data['candidates'][0]['content']['parts'][0]['text']

    user_history[user_id].append({
        "role": "model",
        "parts": [{"text": reply}]
    })

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
        bot.reply_to(message, f"⚠️ خطا: {str(e)[:300]}")

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
