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

# --- 3. START VA ASOSIY MENYU (YANGILANGAN XABAR) ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    update_balance(uid, 0)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎁 Telegram Premium", "⭐️ Telegram Stars") 
    markup.add("💎 Xizmatlar", "💳 Balans To'ldirish")
    markup.add("👤 Profil", "💰 Pul Ishlash")
    
    if uid == ADMIN_ID:
        markup.add("⚙️ Admin Panel")
        
    # Siz aytgan yangi xabar
    bot.send_message(message.chat.id, "Assalomu alaykum telegram xizmatlar botiga xush kelibsiz!", reply_markup=markup)

# --- 4. ASOSIY TUGMALARNI QAYTA ISHLASH ---
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
            types.InlineKeyboardButton("💎 100 Stars — 28,000 so'm", callback_data="buy_STARS100_28000_1"),
            types.InlineKeyboardButton("💎 250 Stars — 69,000 so'm", callback_data="buy_STARS250_69000_1"),
            types.InlineKeyboardButton("💎 500 Stars — 139,000 so'm", callback_data="buy_STARS500_139000_1")
        )
        bot.send_message(message.chat.id, "⭐️ **Stars narxlari:**", reply_markup=markup, parse_mode="Markdown")

    elif message.text == "💎 Xizmatlar":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🔹 Telegram (Obunachi/Like)", callback_data="cat_tg_full"),
            types.InlineKeyboardButton("🔸 Instagram (Obunachi/Like)", callback_data="cat_inst_full")
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
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📢 Reklama yuborish", callback_data="adm_send"),
            types.InlineKeyboardButton("📊 Statistika", callback_data="adm_stats")
        )
        bot.send_message(message.chat.id, "🛠 **Boshqaruv paneli:**", reply_markup=markup)

# --- 5. CALLBACKLAR (KATEGORIYA VA BUYURTMA) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.from_user.id
    
    # Kategoriya - Telegram
    if call.data == "cat_tg_full":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("👥 Obunachi (1571) — 8k", callback_data="buy_1571_8000_1000"),
            types.InlineKeyboardButton("👁 Ko'rish (1556) — 1k", callback_data="buy_1556_1000_1000"),
            types.InlineKeyboardButton("🔙 Orqaga", callback_data="cat_back")
        )
        bot.edit_message_text("🔹 Telegram xizmatlari:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # Kategoriya - Instagram
    elif call.data == "cat_inst_full":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("👥 Obunachi (1577) — 10k", callback_data="buy_1577_10000_1000"),
            types.InlineKeyboardButton("❤️ Like (1580) — 5k", callback_data="buy_1580_5000_1000"),
            types.InlineKeyboardButton("🔙 Orqaga", callback_data="cat_back")
        )
        bot.edit_message_text("🔸 Instagram xizmatlari:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # Admin: Reklama
    elif call.data == "adm_send" and uid == ADMIN_ID:
        msg = bot.send_message(call.message.chat.id, "Reklamani yuboring:")
        bot.register_next_step_handler(msg, start_broadcast)

    # Admin: Statistika
    elif call.data == "adm_stats" and uid == ADMIN_ID:
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        count = c.execute("SELECT COUNT(id) FROM users").fetchone()[0]
        conn.close()
        bot.answer_callback_query(call.id, f"📊 Obunachilar: {count}", show_alert=True)

    # Buyurtma boshlash
    elif call.data.startswith("buy_"):
        _, sid, price, qty = call.data.split("_")
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        bal = c.execute("SELECT balance FROM users WHERE id=?", (uid,)).fetchone()[0]
        conn.close()
        if bal >= float(price):
            msg = bot.send_message(call.message.chat.id, "Link yuboring:")
            bot.register_next_step_handler(msg, finalize_order, sid, float(price), int(qty))
        else:
            bot.answer_callback_query(call.id, "❌ Mablag' yetarli emas!", show_alert=True)

# --- 6. FUNKSIYALAR ---
def finalize_order(message, sid, price, qty):
    uid = message.from_user.id
    update_balance(uid, -price)
    if sid.startswith("PREM") or sid.startswith("STARS"):
        bot.send_message(ADMIN_ID, f"🔔 **QO'LDA:**\nID: {uid}\nXizmat: {sid}\nLink: {message.text}")
        bot.send_message(uid, "✅ Qabul qilindi!")
    else:
        res = requests.post(API_URL, data={'key': API_KEY, 'action': 'add', 'service': sid, 'link': message.text, 'quantity': qty}).json()
        bot.send_message(uid, f"📦 Order ID: {res.get('order', 'Xato')}")

def start_broadcast(message):
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    ids = c.execute("SELECT id FROM users").fetchall()
    conn.close()
    for u_id in ids:
        try: bot.copy_message(u_id[0], message.chat.id, message.message_id); time.sleep(0.05)
        except: pass
    bot.send_message(ADMIN_ID, "✅ Reklama tarqatildi!")

# --- 7. ADMIN /PAY BUYRUG'I ---
@bot.message_handler(commands=['pay'])
def admin_pay(message):
    if message.from_user.id == ADMIN_ID:
        try:
            _, tid, sum_v = message.text.split()
            update_balance(int(tid), float(sum_v))
            bot.send_message(int(tid), f"✅ Balansingiz {sum_v} so'mga to'ldirildi!")
            bot.send_message(ADMIN_ID, "Bajarildi!")
        except: pass

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot.infinity_polling()
