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
app = Flask('')

# Render uchun asosiy sahifa (Ping qilish uchun)
@app.route('/')
def home():
    return "Bot is running 24/7!", 200

def run_web_server():
    # Render avtomatik beradigan PORT ni o'qish
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

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

# --- 3. START VA ASOSIY MENYU ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    args = message.text.split()
    
    init_db()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user = c.execute("SELECT id FROM users WHERE id=?", (uid,)).fetchone()
    
    if not user:
        referrer = None
        if len(args) > 1 and args[1].isdigit():
            referrer = int(args[1])
            if referrer != uid:
                update_balance(referrer, REFERAL_BONUS)
                try: bot.send_message(referrer, f"🎉 Do'stingiz qo'shildi! +{REFERAL_BONUS} so'm bonus.")
                except: pass
        c.execute("INSERT INTO users (id, balance, referred_by) VALUES (?, 0, ?)", (uid, referrer))
        conn.commit()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎁 Telegram Premium", "⭐️ Telegram Stars") 
    markup.add("💎 Xizmatlar", "💳 Balans To'ldirish")
    markup.add("👤 Profil", "💰 Pul Ishlash")
    
    if uid == ADMIN_ID:
        markup.add("⚙️ Admin Panel", "📊 Statistika")
        
    bot.send_message(message.chat.id, "Xush kelibsiz! Kerakli bo'limni tanlang:", reply_markup=markup)

# --- 4. TUGMALARNI QAYTA ISHLASH ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    uid = message.from_user.id
    
    if message.text == "🎁 Telegram Premium" or message.text == "⭐️ Telegram Stars":
        # Ikkala tugma ham Telegram bo'limini ochadi
        dummy_call = types.CallbackQuery(id='0', from_user=message.from_user, chat_instance='0', message=message, data='cat_tg')
        show_services(dummy_call)

    elif message.text == "💎 Xizmatlar":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("🔹 Telegram", callback_data="cat_tg"), 
                   types.InlineKeyboardButton("🔸 Instagram", callback_data="cat_inst"))
        bot.send_message(message.chat.id, "Ijtimoiy tarmoqni tanlang:", reply_markup=markup)

    elif message.text == "👤 Profil":
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        res = c.execute("SELECT balance FROM users WHERE id=?", (uid,)).fetchone()
        bal = res[0] if res else 0; conn.close()
        bot.send_message(message.chat.id, f"👤 **Profilingiz:**\n🆔 ID: `{uid}`\n💰 Balans: {bal:,.0f} so'm", parse_mode="Markdown")

    elif message.text == "💳 Balans To'ldirish":
        bot.send_message(message.chat.id, f"💳 **Karta:** `{KARTA}`\n👤 **Egasi:** {KARTA_EGASI}\n\nTo'lovdan so'ng chekni @admin ga yuboring.")

    elif message.text == "💰 Pul Ishlash":
        ref_link = f"https://t.me/{bot.get_me().username}?start={uid}"
        bot.send_message(message.chat.id, f"💰 **Taklif qiling va pul ishlang!**\nHar bir do'st uchun: {REFERAL_BONUS} so'm\n\n🔗 `{ref_link}`", parse_mode="Markdown")

    elif message.text == "📊 Statistika" and uid == ADMIN_ID:
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        count = c.execute("SELECT COUNT(id) FROM users").fetchone()[0]
        conn.close()
        bot.send_message(message.chat.id, f"📊 **Jami obunachilar:** {count} ta")

# --- 5. XIZMATLAR RO'YXATI ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_services(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    if call.data == "cat_tg":
        markup.add(types.InlineKeyboardButton("➖➖ PREMIUM (GIFT) ➖➖", callback_data="none"))
        markup.add(
            types.InlineKeyboardButton("🎁 Premium 1 oy — 50,000 so'm", callback_data="buy_PREM1_50000_1"),
            types.InlineKeyboardButton("🎁 Premium 3 oy — 165,000 so'm", callback_data="buy_PREM3_165000_1"),
            types.InlineKeyboardButton("🎁 Premium 6 oy — 225,000 so'm", callback_data="buy_PREM6_225000_1"),
            types.InlineKeyboardButton("🎁 Premium 1 yil — 310,000 so'm", callback_data="buy_PREM12_310000_1")
        )
        markup.add(types.InlineKeyboardButton("➖➖ TELEGRAM STARS ➖➖", callback_data="none"))
        markup.add(
            types.InlineKeyboardButton("💎 50 Stars — 15,000 so'm", callback_data="buy_STARS50_15000_1"),
            types.InlineKeyboardButton("💎 100 Stars — 28,000 so'm", callback_data="buy_STARS100_28000_1")
        )
        markup.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="cat_back"))
        
        if call.id == '0':
            bot.send_message(call.message.chat.id, "🔹 Telegram xizmatlari:", reply_markup=markup)
        else:
            bot.edit_message_text("🔹 Telegram xizmatlari:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data == "cat_back":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("🔹 Telegram", callback_data="cat_tg"), 
                   types.InlineKeyboardButton("🔸 Instagram", callback_data="cat_inst"))
        bot.edit_message_text("Ijtimoiy tarmoqni tanlang:", call.message.chat.id, call.message.message_id, reply_markup=markup)

# --- 6. BUYURTMA QISMI ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_start(call):
    if call.data == "none": return
    _, s_id, price, qty = call.data.split("_")
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    res = c.execute("SELECT balance FROM users WHERE id=?", (call.from_user.id,)).fetchone()
    bal = res[0] if res else 0; conn.close()
    
    if bal >= float(price):
        msg = bot.send_message(call.message.chat.id, "Link yoki username yuboring:")
        bot.register_next_step_handler(msg, make_order, s_id, float(price), int(qty))
    else: bot.answer_callback_query(call.id, "Mablag' yetarli emas!", show_alert=True)

def make_order(message, s_id, price, qty):
    uid = message.from_user.id
    link = message.text
    update_balance(uid, -price)
    bot.send_message(uid, "✅ Buyurtma qabul qilindi!")
    
    if s_id.startswith("PREM") or s_id.startswith("STARS"):
        bot.send_message(ADMIN_ID, f"📢 **YANGI BUYURTMA:**\nID: `{uid}`\nXizmat: {s_id}\nLink: {link}")
    else:
        try:
            res = requests.post(API_URL, data={'key': API_KEY, 'action': 'add', 'service': s_id, 'link': link, 'quantity': qty}).json()
            bot.send_message(uid, f"📦 Order ID: {res.get('order', 'Xato')}")
        except: pass

# --- 7. ISHGA TUSHIRISH ---
if __name__ == "__main__":
    init_db()
    # Web serverni alohida oqimda ishga tushirish (Render uchun)
    t = Thread(target=run_web_server)
    t.start()
    
    print("Bot Render-da muvaffaqiyatli ishga tushdi!")
    bot.infinity_polling()
