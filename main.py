import telebot
import google.generativeai as genai
import time
import os
from flask import Flask
import threading

# --- [تنظیمات] ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8768715789:AAGgFiAByPexTWu6iyMIFYZC82bhpNm8Pqo')
GEMINI_KEY = os.environ.get('GEMINI_KEY', 'AIzaSyC4L121FsH2KGLCFnWCOxHhiXl-pS9rHlU')

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
   - ستون ۱ (محصول چیست؟): تعریف به عنوان "سیستم میان‌بر" و "ناجی"
   - ستون ۲ (ارزش واقعی): حمله به مشکل اصلی
   - ستون ۳ (مخاطب‌شناسی): حداقل ۱۵ درد شبانه + بلک لیست
   - ستون ۴ (نتایج ملموس): از زاویه تغییر هویت
   - ستون ۵ (انحصار): مزیت انحصاری + تشدیدکننده

۵. انفجار محتوا:
   - ۱۰۰ پوینت استراتژیک در دسته‌های میل، سادگی، اثبات، انحصار
   - نقشه IBS تلگرام با سناریوی وویس و پیام پین‌بند

لحن: مقتدر، رفیقانه و فنی. برای فروختن ساخته شده‌ای!
"""

# --- [Flask App] ---
app = Flask(__name__)

@app.route('/')
def health():
    return "Master Architect v7.0 is Live!", 200

@app.route('/health')
def health_check():
    return {"status": "ok", "bot": "MasterArchitect"}, 200

# --- [راه‌اندازی Gemini] ---
def setup_gemini():
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',  # ✅ فرمت صحیح
            system_instruction=MASTER_INSTRUCTIONS
        )
        return model
    except Exception as e:
        print(f"❌ Gemini Setup Error: {e}")
        return None

model = setup_gemini()
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- [مدیریت سشن مکالمه برای هر کاربر] ---
user_sessions = {}

def get_chat_session(user_id):
    """هر کاربر یک سشن جداگانه دارد تا context حفظ شود"""
    if user_id not in user_sessions:
        user_sessions[user_id] = model.start_chat(history=[])
    return user_sessions[user_id]

# --- [هندلرهای ربات] ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    # ریست سشن برای شروع مجدد
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    welcome = (
        "🏛 *معمارِ مستر v7.0 آنلاین است!*\n\n"
        "سیستم کالبدشکافی محصول با موتور Gemini فعال شد.\n\n"
        "🎯 *برای شروع بگو:*\n"
        "حوزه فعالیتت چیه و چه محصولی داری؟\n"
        "من تمام پتانسیل پنهانش رو بیرون می‌کشم! 💰"
    )
    bot.reply_to(message, welcome, parse_mode='Markdown')

@bot.message_handler(commands=['reset'])
def reset_session(message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
    bot.reply_to(message, "🔄 سشن ریست شد. دوباره شروع کن!")

@bot.message_handler(func=lambda m: True)
def handle(message):
    if model is None:
        bot.reply_to(message, "❌ خطا در اتصال به Gemini. با ادمین تماس بگیر.")
        return
    
    user_id = message.from_user.id
    
    # نشانگر تایپ
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        chat = get_chat_session(user_id)
        response = chat.send_message(message.text)
        
        reply_text = response.text
        
        # تقسیم پیام‌های بلند (حد تلگرام ۴۰۹۶ کاراکتر)
        if len(reply_text) > 4096:
            chunks = [reply_text[i:i+4096] for i in range(0, len(reply_text), 4096)]
            for chunk in chunks:
                bot.reply_to(message, chunk)
                time.sleep(0.5)
        else:
            bot.reply_to(message, reply_text)
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error for user {user_id}: {error_msg}")
        
        # ریست سشن در صورت خطا
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        bot.reply_to(message, f"⚠️ خطای موقت: {error_msg[:200]}\nدوباره تلاش کن.")

# --- [اجرای Polling در Thread جداگانه] ---
def run_polling():
    print("🤖 Bot polling started...")
    while True:
        try:
            bot.remove_webhook()
            time.sleep(1)
            bot.polling(
                none_stop=True,
                interval=0,
                timeout=60,
                long_polling_timeout=60
            )
        except Exception as e:
            print(f"⚠️ Polling error: {e}. Restarting in 5s...")
            time.sleep(5)

# --- [نقطه اجرا] ---
if __name__ == "__main__":
    print("🚀 Starting Master Architect...")
    
    # Thread ربات به عنوان daemon (با Flask زندگی و می‌میره)
    bot_thread = threading.Thread(target=run_polling, daemon=True)
    bot_thread.start()
    
    # Flask اصلی روی پورت Render
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
