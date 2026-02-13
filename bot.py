import telebot
import requests
import sqlite3
import os
import time
from flask import Flask
from threading import Thread
from telebot import types

# --- SOZLAMALAR ---
TOKEN = '7985996255:AAFzCXx6gKmP4MlTDV18ZNa7TqaUsNikKgE'
API_KEY = '18e30f6d428a19f5136e989458f18076'
API_URL = "https://topsmm.uz/api/v2"
ADMIN_ID = 6873525547
KARTA = "9860 2466 0219 1073"
KARTA_EGASI = "Xayrullayev Bunyod"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Bot status: Active", 200

# Bot uzilib qolmasligi uchun Ping funksiyasi
def keep_alive():
    while True:
        try:
            # Render linkini bura yozing (masalan: https://botingiz.onrender.com)
            requests.get(f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}.onrender.com")
        except:
            pass
        time.sleep(600) # Har 10 daqiqada uyg'otadi

def run_web_server():
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)

# --- BAZA ---
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)''')
    conn.commit()
    conn.close()

def get_balance(uid):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    res = c.execute("SELECT balance FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return res[0] if res else 0

def update_balance(uid, amount):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id, balance) VALUES (?, 0)", (uid,))
    c.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, uid))
    conn.commit()
    conn.close()

init_db()

# --- MENYULAR ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    update_balance(uid, 0)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎁 Telegram Premium", "⭐️ Telegram Stars")
    markup.add("💎 Xizmatlar", "💳 Balans To'ldirish")
    markup.add("👤 Profil", "💰 Pul Ishlash")
    if uid == ADMIN_ID: markup.add("⚙️ Admin Panel")
    bot.send_message(message.chat.id, "Assalomu alaykum telegram xizmatlar botiga xush kelibsiz!", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    
    if message.text == "🎁 Telegram Premium":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🎁 1 oy — 50,000 so'm", callback_data="buy_PREM1_50000_1"),
            types.InlineKeyboardButton("🎁 3 oy — 165,000 so'm", callback_data="buy_PREM3_165000_1"),
            types.InlineKeyboardButton("🎁 6 oy — 225,000 so'm", callback_data="buy_PREM6_225000_1"),
            types.InlineKeyboardButton("🎁 1 yil — 310,000 so'm", callback_data="buy_PREM12_310000_1")
        )
        bot.send_message(message.chat.id, "🎁 **Telegram Premium narxlari:**", reply_markup=markup, parse_mode="Markdown")

    elif message.text == "⭐️ Telegram Stars":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💎 50 Stars — 15,000 so'm", callback_data="buy_STARS50_15000_1"),
            types.InlineKeyboardButton("💎 100 Stars — 28,000 so'm", callback_data="buy_STARS100_28000_1")
        )
        bot.send_message(message.chat.id, "⭐️ **Stars narxlari:**", reply_markup=markup, parse_mode="Markdown")

    elif message.text == "👤 Profil":
        bal = get_balance(uid)
        bot.send_message(message.chat.id, f"👤 **Profilingiz:**\n🆔 ID: `{uid}`\n💰 Balans: {bal:,.0f} so'm", parse_mode="Markdown")

    elif message.text == "⚙️ Admin Panel" and uid == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Reklama", callback_data="adm_reklama"),
                   types.InlineKeyboardButton("📊 Statistika", callback_data="adm_stat"))
        bot.send_message(message.chat.id, "🛠 Admin Paneli:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def calls(call):
    uid = call.from_user.id
    if call.data.startswith("buy_"):
        _, sid, price, qty = call.data.split("_")
        bal = get_balance(uid)
        if bal >= float(price):
            msg = bot.send_message(call.message.chat.id, "Link yuboring:")
            bot.register_next_step_handler(msg, finish_order, sid, float(price), int(qty))
        else:
            bot.answer_callback_query(call.id, "❌ Balans yetarli emas!", show_alert=True)
    
    elif call.data == "adm_stat":
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        count = c.execute("SELECT COUNT(id) FROM users").fetchone()[0]
        bot.answer_callback_query(call.id, f"Foydalanuvchilar: {count} ta", show_alert=True)

def finish_order(message, sid, price, qty):
    uid = message.from_user.id
    update_balance(uid, -price)
    if sid.startswith("PREM") or sid.startswith("STARS"):
        bot.send_message(ADMIN_ID, f"🔔 Buyurtma: {sid}\nID: {uid}\nLink: {message.text}")
    else:
        requests.post(API_URL, data={'key': API_KEY, 'action': 'add', 'service': sid, 'link': message.text, 'quantity': qty})
    bot.send_message(uid, "✅ Buyurtma qabul qilindi!")

if __name__ == "__main__":
    init_db()
    Thread(target=run_web_server).start()
    Thread(target=keep_alive).start() # Uyg'otuvchi tizim ishga tushadi
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
