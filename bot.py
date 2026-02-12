import telebot
import requests
from telebot import types

# Bot token va SMM API kalitlar
TOKEN = '8229610175:AAH_oRU1S73oQfwDYz4cVRigADRwC2u-0oA'
SMM_API_KEY = 'ec9a1cab59539e3296c54e49559c9a96'
SMM_URL = "https://smmya.com/api/v2"

bot = telebot.TeleBot(TOKEN)

# Smmya.com balansini tekshirish funksiyasi
def get_smm_balance():
    payload = {'key': SMM_API_KEY, 'action': 'balance'}
    try:
        r = requests.post(SMM_URL, data=payload)
        data = r.json()
        return f"{data.get('balance', '0')} {data.get('currency', 'UZS')}"
    except:
        return "Xato yuz berdi"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💰 Panel Balansi")
    btn2 = types.KeyboardButton("💎 Premium Narxlari")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, 
                     "Assalomu alaykum! @bunyodpremium_bot xizmatingizda.\n"
                     "Pastdagi tugmalar orqali xizmatlarni boshqarishingiz mumkin.", 
                     reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "💰 Panel Balansi":
        balance = get_smm_balance()
        bot.send_message(message.chat.id, f"SMM paneldagi joriy balansingiz: {balance}")
    
    elif message.text == "💎 Premium Narxlari":
        bot.send_message(message.chat.id, "Xizmatlar tez kunda qo'shiladi...")

# Botni uzluksiz ishlatish
if __name__ == "__main__":
    bot.polling(none_stop=True)
