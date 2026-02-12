import telebot
import requests
import sqlite3
import os
import time
from flask import Flask
from threading import Thread
from telebot import types

# --- 1. SOZLAMALAR ---
TOKEN = '7985996255:AAFzCXx6gKmP4MlTDV18ZNa7TqaUsNikKgE'
API_KEY = '18e30f6d428a19f5136e989458f18076'
API_URL = "https://topsmm.uz/api/v2"
ADMIN_ID = 6873525547
KARTA = "9860 2466 0219 1073"
KARTA_EGASI = "Xayrullayev Bunyod"
REFERAL_BONUS = 500 

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@server.route("/")
def webhook(): return "Bot is online!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)

# --- 2. MA'LUMOTLAR BAZASI ---
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY, 
                    balance REAL DEFAULT 0,
                    referred_by INTEGER)''')
    conn.commit()
    conn.close()

def update_balance(uid, amount):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id, balance) VALUES (?, 0)", (uid,))
    c.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, uid))
    conn.commit()
    conn.close()

init_db()

# --- 3. START VA ASOSIY MENYU ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎁 Telegram Premium", "⭐️ Telegram Stars") 
    markup.add("💎 Xizmatlar", "💳 Balans To'ldirish")
    markup.add("👤 Profil", "💰 Pul Ishlash")
    
    if uid == ADMIN_ID:
        markup.add("⚙️ Admin Panel", "📊 Statistika")
        
    bot.send_message(message.chat.id, "Asosiy menyuga xush kelibsiz!", reply_markup=markup)

# --- 4. TUGMALARNI QAYTA ISHLASH ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    
    if message.text == "🎁 Telegram Premium":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🎁 Premium 1 oy — 50,000 so'm", callback_data="buy_PREM1_50000_1"),
            types.InlineKeyboardButton("🎁 Premium 3 oy — 165,000 so'm", callback_data="buy_PREM3_165000_1"),
            types.InlineKeyboardButton("🎁 Premium 6 oy — 225,000 so'm", callback_data="buy_PREM6_225000_1"),
            types.InlineKeyboardButton("🎁 Premium 1 yil — 310,000 so'm", callback_data="buy_PREM12_310000_1")
        )
        bot.send_message(message.chat.id, "🎁 **Telegram Premium (Gift) narxlari:**", reply_markup=markup, parse_mode="Markdown")

    elif message.text == "⭐️ Telegram Stars":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💎 50 Stars — 15,000 so'm", callback_data="buy_STARS50_15000_1"),
            types.InlineKeyboardButton("💎 100 Stars — 28,000 so'm", callback_data="buy_STARS100_28000_1"),
            types.InlineKeyboardButton("💎 250 Stars — 69,000 so'm", callback_data="buy_STARS250_69000_1"),
            types.InlineKeyboardButton("💎 500 Stars — 139,000 so'm", callback_data="buy_STARS500_139000_1")
        )
        bot.send_message(message.chat.id, "⭐️ **Telegram Stars narxlari:**", reply_markup=markup, parse_mode="Markdown")

    # 💎 Xizmatlar bo'limi yangilandi
    elif message.text == "💎 Xizmatlar":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🔹 Telegram Xizmatlari", callback_data="cat_tg_full"),
            types.InlineKeyboardButton("🔸 Instagram Xizmatlari", callback_data="cat_inst_full")
        )
        bot.send_message(message.chat.id, "Ijtimoiy tarmoqni tanlang:", reply_markup=markup)

    elif message.text == "👤 Profil":
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        res = c.execute("SELECT balance FROM users WHERE id=?", (uid,)).fetchone()
        bal = res[0] if res else 0; conn.close()
        bot.send_message(message.chat.id, f"👤 **Profilingiz:**\n🆔 ID: `{uid}`\n💰 Balans: {bal:,.0f} so'm", parse_mode="Markdown")

    elif message.text == "💳 Balans To'ldirish":
        bot.send_message(message.chat.id, f"💳 **Karta:** `{KARTA}`\n👤 **Egasi:** {KARTA_EGASI}\n\nTo'lovdan so'ng chekni @admin ga yuboring.")

    elif message.text == "⚙️ Admin Panel" and uid == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Reklama yuborish", callback_data="admin_broadcast"))
        bot.send_message(message.chat.id, "Admin paneli:", reply_markup=markup)

# --- 5. TOPSMM.UZ XIZMATLAR RO'YXATI ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def callback_categories(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # TELEGRAM TO'LIQ RO'YXAT
    if call.data == "cat_tg_full":
        markup.add(
            types.InlineKeyboardButton("👥 Obunachi (1571) — 8k", callback_data="buy_1571_8000_1000"),
            types.InlineKeyboardButton("🚀 Prem Obunachi (1516) — 65k", callback_data="buy_1516_65000_1000"),
            types.InlineKeyboardButton("🔄 Tiklashli (1576) — 13k", callback_data="buy_1576_13000_1000"),
            types.InlineKeyboardButton("👁 Ko'rishlar (1556) — 1k", callback_data="buy_1556_1000_1000"),
            types.InlineKeyboardButton("🔙 Orqaga", callback_data="cat_back")
        )
        bot.edit_message_text("🔹 **Telegram xizmatlari (1000 ta uchun):**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    # INSTAGRAM TO'LIQ RO'YXAT
    elif call.data == "cat_inst_full":
        markup.add(
            types.InlineKeyboardButton("👥 Obunachi (1577) — 10k", callback_data="buy_1577_10000_1000"),
            types.InlineKeyboardButton("💎 Sifatli (1581) — 16k", callback_data="buy_1581_16000_1000"),
            types.InlineKeyboardButton("❤️ Like (1580) — 5k", callback_data="buy_1580_5000_1000"),
            types.InlineKeyboardButton("🎬 Ko'rishlar (1582) — 2k", callback_data="buy_1582_2000_1000"),
            types.InlineKeyboardButton("🔙 Orqaga", callback_data="cat_back")
        )
        bot.edit_message_text("🔸 **Instagram xizmatlari (1000 ta uchun):**", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "cat_back":
        markup.add(
            types.InlineKeyboardButton("🔹 Telegram Xizmatlari", callback_data="cat_tg_full"),
            types.InlineKeyboardButton("🔸 Instagram Xizmatlari", callback_data="cat_inst_full")
        )
        bot.edit_message_text("Ijtimoiy tarmoqni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=markup)

# --- 6. BUYURTMA VA API (O'ZGARISHSIZ) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_start(call):
    _, s_id, price, qty = call.data.split("_")
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    res = c.execute("SELECT balance FROM users WHERE id=?", (call.from_user.id,)).fetchone()
    bal = res[0] if res else 0; conn.close()
    if bal >= float(price):
        msg = bot.send_message(call.message.chat.id, "Link yuboring (Masalan: https://t.me/kanal):")
        bot.register_next_step_handler(msg, make_order, s_id, float(price), int(qty))
    else: bot.answer_callback_query(call.id, "❌ Balans yetarli emas!", show_alert=True)

def make_order(message, s_id, price, qty):
    uid = message.from_user.id
    link = message.text
    update_balance(uid, -price)
    bot.send_message(uid, "✅ Buyurtma qabul qilindi!")
    if s_id.startswith("PREM") or s_id.startswith("STARS"):
        bot.send_message(ADMIN_ID, f"📢 **QO'LDA:**\nID: `{uid}`\nXizmat: {s_id}\nLink: {link}")
    else:
        res = requests.post(API_URL, data={'key': API_KEY, 'action': 'add', 'service': s_id, 'link': link, 'quantity': qty}).json()
        bot.send_message(uid, f"📦 Order ID: {res.get('order', 'Xato')}")

# --- ADMIN REKLAMA ---
@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast")
def broadcast_prompt(call):
    msg = bot.send_message(call.message.chat.id, "Xabarni yuboring:")
    bot.register_next_step_handler(msg, start_broadcasting)

def start_broadcasting(message):
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    users = c.execute("SELECT id FROM users").fetchall()
    conn.close()
    for user in users:
        try: bot.copy_message(user[0], message.chat.id, message.message_id); time.sleep(0.05)
        except: pass
    bot.send_message(ADMIN_ID, "✅ Reklama yuborildi!")

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot.infinity_polling()
