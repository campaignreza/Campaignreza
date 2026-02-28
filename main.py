import telebot
import google.generativeai as genai
import time
import os
from flask import Flask
import threading

# --- [تنظیمات دسترسی از محیط سرور] ---
# در پنل Render، این دو نام را در بخش Environment Variables تعریف کن
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# --- [ایستگاه‌های مصاحبه استراتژیک معمار مستر] ---
STEPS = {
    0: "🔥 درود! معمارِ مستر بیدار شد. برای تبدیل محصولت به الماس، اول بگو: **حوزه فعالیتت چیه و دقیقاً چه محصولی رو می‌خوایم کالبدشکافی کنیم؟**",
    1: "🚀 عالیه. حالا بگو **وعده بزرگ و ادعای شیرین این محصول چیه؟** (عددی و خیره‌کننده بگو!)",
    2: "💎 بسیار خب. وضعیت **ویترین و اعتمادسازیت** چطوره؟ (کجا می‌فروشی و چطور اعتماد جلب می‌کنی؟)",
    3: "💰 سوال آخر: **قیمت چنده و مشتری‌ها معمولاً چه بهانه‌ای برای نخریدن میارن؟**",
    4: "⏳ معمارِ مستر در حال شخم زدن صنعت شماست... لطفا شکیبا باشید."
}

MASTER_INSTRUCTIONS = """
تو "معمارِ مستر" هستی. متخصص مهندسی معکوس فروش.
خروجی نهایی تو باید شامل: فیلترهای سه‌گانه، سند ۵ ستونه (ناجی، ارزش، دردها، تغییر هویت، تیر خلاص) و ۱۰۰ پوینت استراتژیک باشد.
لحن: مقتدر، لاتی، فنی و رفیقانه.
"""

# --- [بخش وب‌سرور برای زنده ماندن در رندر] ---
app = Flask(__name__)
@app.route('/')
def health(): return "Master Architect v7.0 is Live!", 200

user_sessions = {}

try:
    genai.configure(api_key=GEMINI_KEY)
    # انتخاب خودکار مدل فعال
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model = genai.GenerativeModel(available_models[0], system_instruction=MASTER_INSTRUCTIONS)
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
except Exception as e:
    print(f"Setup Error: {e}")

@bot.message_handler(func=lambda m: True)
def handle_logic(message):
    chat_id = message.chat.id
    text = message.text

    if text.lower() in ['سلام', '/start', 'درود']:
        user_sessions[chat_id] = {'step': 0, 'answers': []}
        bot.send_message(chat_id, STEPS[0], parse_mode='Markdown')
        return

    if chat_id in user_sessions:
        current_step = user_sessions[chat_id]['step']
        user_sessions[chat_id]['answers'].append(text)
        next_step = current_step + 1
        user_sessions[chat_id]['step'] = next_step

        if next_step in STEPS:
            bot.send_message(chat_id, STEPS[next_step], parse_mode='Markdown')
            if next_step == 4:
                bot.send_chat_action(chat_id, 'typing')
                context = "\n".join(user_sessions[chat_id]['answers'])
                try:
                    response = model.generate_content(f"تحلیل ایستگاه به ایستگاه:\n{context}")
                    full_text = response.text
                    for i in range(0, len(full_text), 4000):
                        bot.send_message(chat_id, full_text[i:i+4000])
                    del user_sessions[chat_id]
                except Exception as e:
                    bot.reply_to(message, f"خطای هوش مصنوعی: {str(e)}")
        else:
            bot.reply_to(message, "بنویس 'سلام' تا دوباره شروع کنیم.")

def run_polling():
    bot.remove_webhook()
    bot.infinity_polling(timeout=60, long_polling_timeout=30)

if __name__ == "__main__":
    threading.Thread(target=run_polling).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
