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

# --- 2. MA'LUMOTLAR BAZASI (XATOLIKSIZ VERSIYA) ---
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY, 
                    balance REAL DEFAULT 0,
                    referred_by INTEGER)''')
    
    # Eski bazaga referred_by ustunini qo'shish (agar yo'q bo'lsa)
    try:
        c.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER")
    except sqlite3.OperationalError:
        pass # Ustun allaqachon mavjud bo'lsa xatoni e'tiborsiz qoldiramiz
        
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

# --- 3. ASOSIY KLAVIATURA VA START ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    args = message.text.split()
    
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    user_exists = c.execute("SELECT id FROM users WHERE id=?", (uid,)).fetchone()
    
    if not user_exists:
        referrer = None
        if len(args) > 1 and args[1].isdigit():
            referrer = int(args[1])
            if referrer != uid:
                update_balance(referrer, REFERAL_BONUS)
                try:
                    bot.send_message(referrer, f"🎉 Tabriklaymiz! Havolangiz orqali do'stingiz qo'shildi. Balansingizga {REFERAL_BONUS} so'm qo'shildi.")
                except: pass
        
        c.execute("INSERT INTO users (id, balance, referred_by) VALUES (?, 0, ?)", (uid, referrer))
        conn.commit()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💎 Xizmatlar", "💳 Balans To'ldirish", "👤 Profil", "💰 Pul Ishlash")
    bot.send_message(message.chat.id, "Xush kelibsiz! @Bunyodpremium_bot xizmatingizda.", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    if message.text == "💎 Xizmatlar":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🔹 Telegram", callback_data="cat_tg"),
            types.InlineKeyboardButton("🔸 Instagram", callback_data="cat_inst")
        )
        bot.send_message(message.chat.id, "Ijtimoiy tarmoqni tanlang:", reply_markup=markup)
    
    elif message.text == "💰 Pul Ishlash":
        bot_user = bot.get_me().username
        ref_link = f"https://t.me/{bot_user}?start={uid}"
        text = (f"💰 **Pul ishlash bo'limi**\n\n"
                f"Do'stlaringizni taklif qiling va har bir yangi do'stingiz uchun **{REFERAL_BONUS} so'm** bonus oling!\n\n"
                f"🔗 Sizning havolangiz:\n`{ref_link}`")
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

    elif message.text == "👤 Profil":
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        res = c.execute("SELECT balance FROM users WHERE id=?", (uid,)).fetchone()
        bal = res[0] if res else 0; conn.close()
        bot.send_message(message.chat.id, f"👤 **Profilingiz:**\n🆔 ID: `{uid}`\n💰 Balans: {bal:,.0f} so'm", parse_mode="Markdown")

    elif message.text == "💳 Balans To'ldirish":
        bot.send_message(message.chat.id, f"💳 **Balansni to'ldirish:**\n📍 Karta: `{KARTA}`\n👤 Egasi: {KARTA_EGASI}\n\nTo'lovdan so'ng chekni yuboring.")

# --- 4. XIZMATLAR ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_services(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    if call.data == "cat_tg":
        markup.add(
            types.InlineKeyboardButton("🎁 Premium 1 oy (Gift) - 55k", callback_data="buy_PREM1_55000_1"),
            types.InlineKeyboardButton("🎁 Premium 3 oy (Gift) - 155k", callback_data="buy_PREM3_155000_1"),
            types.InlineKeyboardButton("🎁 Premium 6 oy (Gift) - 210k", callback_data="buy_PREM6_210000_1"),
            types.InlineKeyboardButton("🎁 Premium 1 yil (Gift) - 390k", callback_data="buy_PREM12_390000_1"),
            types.InlineKeyboardButton("⭐️ 100 Stars (Gift) - 28k", callback_data="buy_STARS100_28000_1"),
            types.InlineKeyboardButton("⭐️ Prem Obunachi 7 kun - ID 1516 - 65k", callback_data="buy_1516_65000_1000"),
            types.InlineKeyboardButton("👥 TG Haqiqiy - ID 1571 - 8k", callback_data="buy_1571_8000_1000"),
            types.InlineKeyboardButton("👥 TG 365 kun tiklash - ID 1576 - 13k", callback_data="buy_1576_13000_1000"),
            types.InlineKeyboardButton("🔙 Orqaga", callback_data="cat_back")
        )
        bot.edit_message_text("🔹 Telegram bo'limi:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data == "cat_inst":
        markup.add(
            types.InlineKeyboardButton("👥 Insta (0%) - ID 1577 - 10k", callback_data="buy_1577_10000_1000"),
            types.InlineKeyboardButton("👥 Insta (365 kun) - ID 1581 - 16k", callback_data="buy_1581_16000_1000"),
            types.InlineKeyboardButton("❤️ Insta Like (1k) - ID 1580 - 5k", callback_data="buy_1580_5000_1000"),
            types.InlineKeyboardButton("🔙 Orqaga", callback_data="cat_back")
        )
        bot.edit_message_text("🔸 Instagram bo'limi:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data == "cat_back":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("🔹 Telegram", callback_data="cat_tg"), types.InlineKeyboardButton("🔸 Instagram", callback_data="cat_inst"))
        bot.edit_message_text("Ijtimoiy tarmoqni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=markup)

# --- 5. BUYURTMA ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def order_start(call):
    _, s_id, price, qty = call.data.split("_")
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    res = c.execute("SELECT balance FROM users WHERE id=?", (call.from_user.id,)).fetchone()
    bal = res[0] if res else 0; conn.close()
    
    if bal >= float(price):
        msg = bot.send_message(call.message.chat.id, "Havola yoki Username yuboring:")
        bot.register_next_step_handler(msg, make_order, s_id, float(price), int(qty))
    else: bot.answer_callback_query(call.id, "Mablag' yetarli emas!", show_alert=True)

def make_order(message, s_id, price, qty):
    uid = message.from_user.id
    link = message.text
    if s_id.startswith("PREM") or s_id.startswith("STARS"):
        update_balance(uid, -price)
        bot.send_message(uid, "✅ Buyurtmangiz qabul qilindi! Operator yaqin orada sovg'ani yuboradi.")
        bot.send_message(ADMIN_ID, f"📢 **QO'LDA:**\nUser ID: `{uid}`\nXizmat: {s_id}\nLink: {link}\nSumma: {price:,.0f} so'm")
    else:
        try:
            res = requests.post(API_URL, data={'key': API_KEY, 'action': 'add', 'service': s_id, 'link': link, 'quantity': qty}).json()
            if res and 'order' in res:
                update_balance(uid, -price)
                bot.send_message(uid, f"✅ Buyurtma ID: {res['order']} panelga yuborildi.")
            else: bot.send_message(uid, "❌ Xatolik! Panelda muammo.")
        except: bot.send_message(uid, "❌ API ulanishda xato.")

# --- 6. ADMIN ---
@bot.message_handler(commands=['pay'])
def admin_pay(message):
    if message.from_user.id == ADMIN_ID:
        try:
            _, tid, sum_val = message.text.split()
            update_balance(int(tid), float(sum_val))
            bot.send_message(int(tid), f"✅ Balansingiz {sum_val} so'mga to'ldirildi!")
            bot.send_message(ADMIN_ID, "Bajarildi!")
        except: bot.send_message(ADMIN_ID, "Xato! Format: /pay ID SUMMA")

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot.infinity_polling()
