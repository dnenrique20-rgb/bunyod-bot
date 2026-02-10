import telebot
from telebot import types

# 1. SOZLAMALAR
TOKEN = '7985996255:AAFzCXx6gKmP4MlTDV18ZNa7TqaUsNikKgE' 
CHANNELS = ['@smm_premium_channel'] 
bot = telebot.TeleBot(TOKEN)

def check_sub(user_id):
    try:
        for channel in CHANNELS:
            status = bot.get_chat_member(chat_id=channel, user_id=user_id).status
            if status == 'left':
                return False
        return True
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn_phone = types.KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)
        markup.add(btn_phone)
        bot.send_message(message.chat.id, f"👋 Salom, {message.from_user.first_name}! Premium yutish uchun raqamingizni yuboring 👇", reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_sub = types.InlineKeyboardButton(text="Obuna bo'lish ➕", url="https://t.me/smm_premium_channel")
        btn_done = types.InlineKeyboardButton(text="Tekshirish ✅", callback_data="check")
        markup.add(btn_sub, btn_done)
        bot.send_message(message.chat.id, "❌ Botdan foydalanish uchun kanalga obuna bo'ling!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "Siz hali obuna bo'lmadingiz! ❌", show_alert=True)

@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    bot.send_message(message.chat.id, "✅ Raqamingiz qabul qilindi!")

bot.polling(none_stop=True)

