import telebot
import requests
from telebot import types

# --- 1. SOZLAMALAR ---
# BotFather'dan olingan oxirgi to'g'ri token
TOKEN = '7985996255:AAFzCXx6gKmP4MlTDV18ZNa7TqaUsNikKgE'
# Smmya.com dan olingan API kalit
SMM_API_KEY = 'ec9a1cab59539e3296c54e49559c9a96'
SMM_URL = "https://smmya.com/api/v2"

bot = telebot.TeleBot(TOKEN)

# --- 2. SMM PANEL BILAN ISHLASH ---
def get_smm_balance():
    """Smmya.com balansini tekshirish funksiyasi"""
    payload = {
        'key': SMM_API_KEY, 
        'action': 'balance'
    }
    try:
        r = requests.post(SMM_URL, data=payload, timeout=10)
        data = r.json()
        if 'balance' in data:
            return f"{data['balance']} {data.get('currency', 'UZS')}"
        else:
            return "Xatolik: API kalit noto'g'ri bo'lishi mumkin."
    except Exception as e:
        return f"Bog'lanishda xato yuz berdi."

# --- 3. BOT BUYRUQLARI ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💰 Panel Balansi")
    btn2 = types.KeyboardButton("💎 Telegram Premium")
    markup.add(btn1, btn2)
    
    welcome_text = (
        f"Assalomu alaykum, {message.from_user.first_name}!\n\n"
        f"🤖 @Bunyodpremium_bot tizimiga xush kelibsiz.\n"
        f"Pastdagi menyu orqali xizmatlarni tanlang."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "💰 Panel Balansi":
        # Panel balansini olish
        msg = bot.send_message(message.chat.id, "Kuting, ma'lumot olinmoqda...")
        balance = get_smm_balance()
        bot.edit_message_text(f"💳 SMM paneldagi joriy balansingiz: **{balance}**", message.chat.id, msg.message_id, parse_mode="Markdown")
    
    elif message.text == "💎 Telegram Premium":
        bot.send_message(message.chat.id, "🎁 Telegram Premium xizmatlari yaqin daqiqalarda qo'shiladi.")

# --- 4. BOTNI ISHGA TUSHIRISH ---
if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)
