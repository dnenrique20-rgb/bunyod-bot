import telebot
from telebot import types

# BotFather'dan olgan tokenni mana shu qo'shtirnoq ichiga yozing
TOKEN = "7985996255:AAFzCXx6gKmP4MlTDV18ZNa7TqaUsNikKgE"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("Premium sotib olish")
    btn2 = types.KeyboardButton("Admin bilan bog'lanish")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, f"Salom {message.from_user.first_name}! Botga xush kelibsiz.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def messages(message):
    if message.text == "Premium sotib olish":
        bot.send_message(message.chat.id, "Premium narxlari:\n- 1 oylik: 50 000 so'm\n- 1 yillik: 400 000 so'm")
    elif message.text == "Admin bilan bog'lanish":
        bot.send_message(message.chat.id, "Admin: @Sizning_Usernamengiz")

bot.polling()
