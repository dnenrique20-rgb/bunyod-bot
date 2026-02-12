import telebot
import requests
import sqlite3
from telebot import types

# --- 1. KONFIGURATSIYA ---
TOKEN = '7985996255:AAFzCXx6gKmP4MlTDV18ZNa7TqaUsNikKgE'
SMM_API_KEY = 'ec9a1cab59539e3296c54e49559c9a96'
SMM_URL = "https://smmya.com/api/v2"
ADMIN_ID = 6873525547
ADMIN_USER = "@khayrullayev_servise"
KARTA = "9860 2466 0219 1073"
KARTA_EGASI = "Xayrullayev Bunyod"

# Avtomatik narx hisoblagich uchun sozlamalar
DOLLAR_KURSI = 12850  # 1$ kursini shu yerda yangilab turasiz
USTAMA_FOIZI = 1.3    # 30% foyda qo'shish

bot = telebot.TeleBot(TOKEN)

# --- 2. BAZA (HISTORY VA STATISTIKA UCHUN) ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 user_id INTEGER, service_id TEXT, price REAL, link TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def update_db_balance(user_id, amount):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id, balance) VALUES (?, 0)", (user_id,))
    c.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def add_order_to_history(user_id, s_id, price, link):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (user_id, service_id, price, link, status) VALUES (?, ?, ?, ?, ?)",
              (user_id, s_id, price, link, "Bajarildi"))
    conn.commit()
    conn.close()

init_db()

# --- 3. YORDAMCHI FUNKSIYALAR ---
def get_converted_price(usd_price):
    """Dollardagi narxni so'mga o'girib, ustama qo'shadi"""
    return round(usd_price * DOLLAR_KURSI * USTAMA_FOIZI, -2) # Yuzlikkacha yaxlitlash

# --- 4. BOT BUYRUQLARI ---
@bot.message_handler(commands=['start'])
def start(message):
    update_db_balance(message.from_user.id, 0)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💎 Xizmatlar", "💳 Balans To'ldirish", "👤 Profil", "📜 Buyurtmalarim", "📊 Statistika")
    bot.send_message(message.chat.id, f"Salom! @Bunyodpremium_bot xizmatingizda.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    uid = message.from_user.id
    
    if message.text == "👤 Profil":
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE id=?", (uid,)); res = c.fetchone()
        bal = res[0] if res else 0; conn.close()
        bot.send_message(message.chat.id, f"👤 **Sizning Profilingiz:**\n\n🆔 ID: `{uid}`\n💰 Balans: {bal:,.0f} so'm", parse_mode="Markdown")

    elif message.text == "📜 Buyurtmalarim":
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        c.execute("SELECT service_id, price, status FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 5", (uid,))
        rows = c.fetchall(); conn.close()
        if not rows:
            bot.send_message(message.chat.id, "Sizda hali buyurtmalar yo'q.")
        else:
            text = "📜 **Oxirgi buyurtmalaringiz:**\n\n"
            for r in rows: text += f"🔹 ID: {r[0]} | Summa: {r[1]:,.0f} so'm | {r[2]}\n"
            bot.send_message(message.chat.id, text, parse_mode="Markdown")

    elif message.text == "📊 Statistika" and uid == ADMIN_ID:
        conn = sqlite3.connect('users.db'); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users"); users_count = c.fetchone()[0]
        c.execute("SELECT SUM(balance) FROM users"); total_bal = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM orders"); orders_count = c.fetchone()[0]
        conn.close()
        bot.send_message(message.chat.id, f"📊 **Bot Statistikasi:**\n\n👥 Azolar: {users_count}\n💳 Jami foydalanuvchi balanslari: {total_bal:,.0f} so'm\n📦 Jami buyurtmalar: {orders_count}")

    elif message.text == "💎 Xizmatlar":
        # Avto-narx hisoblash namunalari
        p3 = get_converted_price(9.3) # Smmya'da 9.3$ bo'lsa
        p6 = get_converted_price(12.5) 
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"⭐️ Premium 3 oy - {p3:,.0f} so'm", callback_data=f"buy_468_{p3}"))
        markup.add(types.InlineKeyboardButton(f"⭐️ Premium 6 oy - {p6:,.0f} so'm", callback_data=f"buy_469_{p6}"))
        bot.send_message(message.chat.id, "Xizmatni tanlang (Narxlar avtomatik yangilangan):", reply_markup=markup)

    elif message.text == "💳 Balans To'ldirish":
        bot.send_message(message.chat.id, f"💳 **Balans to'ldirish:**\n\n📍 Karta: `{KARTA}`\n👤 Egasi: {KARTA_EGASI}\n\nChekni yuboring.")

# --- ADMIN BUYRUG'I: /pay ID SUMMA ---
@bot.message_handler(commands=['pay'])
def add_money(message):
    if message.from_user.id == ADMIN_ID:
        try:
            _, u_id, amount = message.text.split()
            update_db_balance(int(u_id), float(amount))
            bot.send_message(int(u_id), f"✅ Balansingiz {float(amount):,.0f} so'mga to'ldirildi!")
            bot.send_message(ADMIN_ID, "Bajarildi!")
        except: bot.send_message(ADMIN_ID, "Format: /pay ID SUMMA")

# --- BUYURTMA JARAYONI ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    _, s_id, price = call.data.split("_")
    conn = sqlite3.connect('users.db'); c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id=?", (call.from_user.id,))
    user_bal = c.fetchone()[0]; conn.close()
    
    if user_bal >= float(price):
        msg = bot.send_message(call.message.chat.id, "Link yuboring:")
        bot.register_next_step_handler(msg, process_order, s_id, float(price))
    else: bot.answer_callback_query(call.id, "Mablag' yetarli emas!", show_alert=True)

def process_order(message, s_id, price):
    # SMM Panelga yuborish
    res = requests.post(SMM_URL, data={'key': SMM_API_KEY, 'action': 'add', 'service': s_id, 'link': message.text, 'quantity': 1}).json()
    
    if res and 'order' in res:
        update_db_balance(message.from_user.id, -price)
        add_order_to_history(message.from_user.id, s_id, price, message.text)
        bot.send_message(message.chat.id, f"✅ Buyurtma ID: {res['order']}. Balansdan {price:,.0f} so'm yechildi.")
    else: bot.send_message(message.chat.id, "❌ Panelda xatolik!")

bot.polling(none_stop=True)
