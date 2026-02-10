import telebot
from telebot import types

# 1. SOZLAMALAR
TOKEN = '7985996255:AAFzCXx6gKmP4MlTDV18ZNa7TqaUsNikKgE' 
CHANNELS = ['@smm_premium_channel'] 
bot = telebot.TeleBot(TOKEN)

# Obunani tekshirish funksiyasi
def check_sub(user_id):
    try:
        for channel in CHANNELS:
            status = bot.get_chat_member(chat_id=channel, user_id=user_id).status
            if status in ['member', 'administrator', 'creator']:
                return True
        return False
    except:
        return False

# Asosiy Inline Menyusi (Tugmalar rasmda ko'rsatilgan tartibda)
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton(text="🌟 Premium Olish", callback_data="p_olish")
    btn2 = types.InlineKeyboardButton(text="TOP foydalanuvchilar", callback_data="top_users")
    btn3 = types.InlineKeyboardButton(text="💸 Premium Narxlari", callback_data="prices")
    btn4 = types.InlineKeyboardButton(text="💳 Mening Hisobim", callback_data="my_account")
    btn5 = types.InlineKeyboardButton(text="🎁 Bonus olish", callback_data="get_bonus")
    btn6 = types.InlineKeyboardButton(text="📝 Qo'llanma", callback_data="guide")
    btn7 = types.InlineKeyboardButton(text="🧑‍💻 Administrator", url="https://t.me/Bunyod_admin") 
    btn8 = types.InlineKeyboardButton(text="🌟 Stars olish", callback_data="get_stars")
    
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.row(btn5)
    markup.add(btn6, btn7)
    markup.row(btn8)
    return markup

# Start buyrug'i
@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn_phone = types.KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)
        markup.add(btn_phone)
        bot.send_message(message.chat.id, f"👋 Salom, {message.from_user.first_name}!\n\n🎁 Telegram Premium yutib olish uchun raqamingizni tasdiqlang 👇", reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_sub = types.InlineKeyboardButton(text="Obuna bo'lish ➕", url="https://t.me/smm_premium_channel")
        btn_done = types.InlineKeyboardButton(text="Tekshirish ✅", callback_data="check_sub")
        markup.add(btn_sub, btn_done)
        bot.send_message(message.chat.id, "❌ Botdan foydalanish uchun kanalimizga obuna bo'ling!", reply_markup=markup)

# RAQAM YUBORILGANDA ISHLAYDIGAN QISM (Eng muhim joyi!)
@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    # Raqamni olgandan keyin pastdagi katta tugmani o'chirish
    remove_keyboard = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "✅ Raqamingiz muvaffaqiyatli qabul qilindi!", reply_markup=remove_keyboard)
    
    # Asosiy menyuni darhol yuborish
    msg_text = (
        "<b>Batafsil >> https://t.me/smm_premium_channel</b>\n"
        "Tepadagi LINK ustiga bosing 👆\n\n"
        "Marhamat, kerakli bo'limni tanlang:"
    )
    bot.send_message(message.chat.id, msg_text, parse_mode="HTML", reply_markup=main_menu())

# Tugmalar bosilganda ishlaydigan qismlar
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "check_sub":
        if check_sub(call.from_user.id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "Siz hali obuna bo'lmadingiz! ❌", show_alert=True)

    elif call.data == "prices":
        prices_text = (
            "🌟 <b>Telegram Premium Narxlari:</b>\n\n"
            "⭐ 1 oylik — 50.000 so'm\n"
            "🎁 3 oylik — 185.000 so'm\n"
            "💎 6 oylik — 240.000 so'm\n"
            "👑 1 yillik — 315.000 so'm\n\n"
            "Sotib olish uchun Administratorga yozing."
        )
        bot.send_message(call.message.chat.id, prices_text, parse_mode="HTML")

    elif call.data == "get_stars":
        stars_text = (
            "🌟 <b>Telegram Stars Narxlari:</b>\n\n"
            "🔸 50 ta stars — 23.000 so'm\n"
            "🔸 100 ta stars — 45.000 so'm\n\n"
            "Xarid qilish uchun Administratorga murojaat qiling."
        )
        bot.send_message(call.message.chat.id, stars_text, parse_mode="HTML")

    elif call.data == "my_account":
        bot.send_message(call.message.chat.id, f"👤 <b>Sizning hisobingiz:</b>\n\n🆔 ID: <code>{call.from_user.id}</code>\n👤 Ism: {call.from_user.first_name}\n💰 Balans: 0 so'm", parse_mode="HTML")

bot.polling(none_stop=True)

