import telebot
import requests
import sqlite3
import os
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
    try:
        c.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER")
    except: pass
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
    args = message.text.split()
    
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    user = c.execute("SELECT id FROM users WHERE id=?", (uid,)).fetchone()
    
    if not user:
        referrer = None
        if len(args) > 1 and args[1].isdigit():
            referrer = int(args[1])
            if referrer != uid:
                update_balance(referrer, REFERAL_BONUS)
                try: bot.send_message(referrer, f"🎉 Do'stingiz qo'shildi! Balansingizga {REFERAL_BONUS} so'm bonus berildi.")
                except: pass
        c.execute("INSERT INTO users (id, balance, referred_by) VALUES (?, 0, ?)", (uid, referrer))
        conn.commit()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💎 Xizmatlar", "💳 Balans To'ldirish", "👤 Profil", "💰 Pul Ishlash", "📊 Statistika")
    bot.send_message(message.chat.id, "Xush kelibsiz! @Bunyodpremium_bot xizmatingizda.", reply_markup=markup)

# --- 4. TUGMALAR ISHLOVCHI ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    
    if message.text == "💎 Xizmatlar":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("🔹 Telegram", callback_data="cat_tg"), 
                   types.InlineKeyboardButton("🔸 Instagram", callback_data="cat_inst"))
        bot.send_message(message.chat.id, "Ijtimoiy tarmoqni tanlang:", reply_markup=markup)

    elif message.text == "💰 Pul Ishlash":
        ref_link = f"https://t.me/{bot.get_me().username}?start={uid}"
        bot.send_message(message.chat.id, f"💰 **Har bir taklif uchun {REFERAL_BONUS} so'm oling!**\n\n🔗 Havolangiz:\n`{ref_link}`", parse_mode="Markdown")

    elif message.text == "👤 Profil":
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        res = c.execute("SELECT balance FROM users WHERE id=?", (uid,)).fetchone()
        bal = res[0] if res else 0; conn.close()
        bot.send_message(message.chat.id, f"👤 **Profilingiz:**\n🆔 ID: `{uid}`\n💰 Balans: {bal:,.0f} so'm", parse_mode="Markdown")

    elif message.text == "💳 Balans To'ldirish":
        bot.send_message(message.chat.id, f"💳 **Karta:** `{KARTA}`\n👤 **Egasi:** {KARTA_EGASI}\n\nTo'lovdan so'ng chekni @admin ga yuboring.")

    elif message.text == "📊 Statistika":
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        count = c.execute("SELECT COUNT(id) FROM users").fetchone()[0]
        conn.close()
        bot.send_message(message.chat.id, f"📊 **Bot obunachilari soni:** {count} ta")

# --- 5. XIZMATLAR (AJRATILGAN VA YANGI NARXLAR) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_services(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    if call.data == "cat_tg":
        # Guruh 1: Premium
        markup.add(types.InlineKeyboardButton("➖➖ PREMIUM (GIFT) ➖➖", callback_data="none"))
        markup.add(
            types.InlineKeyboardButton("🎁 Premium 1 oy — 50,000 so'm", callback_data="buy_PREM1_50000_1"),
            types.InlineKeyboardButton("🎁 Premium 3 oy — 165,000 so'm", callback_data="buy_PREM3_165000_1"),
            types.InlineKeyboardButton("🎁 Premium 6 oy — 225,000 so'm", callback_data="buy_PREM6_225000_1"),
            types.InlineKeyboardButton("🎁 Premium 1 yil — 310,000 so'm", callback_data="buy_PREM12_310000_1")
        )
        # Guruh 2: Stars
        markup.add(types.InlineKeyboardButton("➖➖ TELEGRAM STARS ➖➖", callback_data="none"))
        markup.add(
            types.InlineKeyboardButton("💎 50 Stars — 15,000 so'm", callback_data="buy_STARS50_15000_1"),
            types.InlineKeyboardButton("💎 100 Stars — 28,000 so'm", callback_data="buy_STARS100_28000_1"),
            types.InlineKeyboardButton("💎 250 Stars — 69,000 so'm", callback_data="buy_STARS250_69000_1"),
            types.InlineKeyboardButton("💎 500 Stars — 139,000 so'm", callback_data="buy_STARS500_139000_1")
        )
        # Guruh 3: Obunachilar
        markup.add(types.InlineKeyboardButton("➖➖ OBUNACHILAR (ID) ➖➖", callback_data="none"))
        markup.add(
            types.InlineKeyboardButton("⭐ Prem Obunachi 7 kun (1516) — 65k", callback_data="buy_1516_65000_1000"),
            types.InlineKeyboardButton("👥 TG Haqiqiy (1571) — 8k", callback_data="buy_1571_8000_1000"),
            types.InlineKeyboardButton("🔙 Orqaga", callback_data="cat_back")
        )
        bot.edit_message_text("🔹 Telegram bo'limi (Yangi narxlar):", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "cat_inst":
        markup.add(types.InlineKeyboardButton("➖➖ INSTAGRAM ➖➖", callback_data="none"))
        markup.add(
            types.InlineKeyboardButton("👥 Insta (1577) — 10k", callback_data="buy_1577_10000_1000"),
            types.InlineKeyboardButton("👥 Insta (1581) — 16k", callback_data="buy_1581_16000_1000"),
            types.InlineKeyboardButton("❤️ Insta Like (1580) — 5k", callback_data="buy_1580_5000_1000"),
            types.InlineKeyboardButton("🔙 Orqaga", callback_data="cat_back")
        )
        bot.edit_message_text("🔸 Instagram bo'limi:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "cat_back":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("🔹 Telegram", callback_data="cat_tg"), 
                   types.InlineKeyboardButton("🔸 Instagram", callback_data="cat_inst"))
        bot.edit_message_text("Ijtimoiy tarmoqni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=markup)

# --- 6. BUYURTMA VA ADMIN PAY ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_start(call):
    if call.data == "none": return
    _, s_id, price, qty = call.data.split("_")
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    res = c.execute("SELECT balance FROM users WHERE id=?", (call.from_user.id,)).fetchone()
    bal = res[0] if res else 0; conn.close()
    
    if bal >= float(price):
        msg = bot.send_message(call.message.chat.id, "Link yoki @username yuboring:")
        bot.register_next_step_handler(msg, make_order, s_id, float(price), int(qty))
    else: bot.answer_callback_query(call.id, "Mablag' yetarli emas!", show_alert=True)

def make_order(message, s_id, price, qty):
    uid = message.from_user.id
    link = message.text
    if s_id.startswith("PREM") or s_id.startswith("STARS"):
        update_balance(uid, -price)
        bot.send_message(uid, "✅ Qabul qilindi! Operator yaqin orada yuboradi.")
        bot.send_message(ADMIN_ID, f"📢 **QO'LDA:**\nID: `{uid}`\nXizmat: {s_id}\nLink: {link}\nSumma: {price}")
    else:
        res = requests.post(API_URL, data={'key': API_KEY, 'action': 'add', 'service': s_id, 'link': link, 'quantity': qty}).json()
        if res and 'order' in res:
            update_balance(uid, -price)
            bot.send_message(uid, f"✅ Yuborildi! Order ID: {res['order']}")
        else: bot.send_message(uid, "❌ Xatolik!")

@bot.message_handler(commands=['pay'])
def admin_pay(message):
    if message.from_user.id == ADMIN_ID:
        try:
            _, tid, sum_v = message.text.split()
            update_balance(int(tid), float(sum_v))
            bot.send_message(int(tid), f"✅ Balansingiz {sum_v} so'mga to'ldirildi!")
            bot.send_message(ADMIN_ID, "OK!")
        except: bot.send_message(ADMIN_ID, "/pay ID SUMMA")

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot.infinity_polling()
