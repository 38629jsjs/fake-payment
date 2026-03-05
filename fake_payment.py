import telebot
from telebot import types
from datetime import datetime, timedelta
import secrets
import string
import os

# --- CONFIGURATION ---
API_TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID', '0')) 
PROOF_CHANNEL_ID = os.getenv('CHANNEL_ID')
STORE_NAME = "Vinzy Store"
RECEIVER_NAME = "Aysi Sovan"
# ---------------------

bot = telebot.TeleBot(API_TOKEN)

def generate_digits(length):
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def generate_mixed(length):
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))

@bot.message_handler(commands=['start', 'pay'])
def start_handler(message):
    if message.from_user.id != OWNER_ID:
        return 
    msg = bot.send_message(message.chat.id, "💰 <b>Step 1:</b> Enter the amount (e.g., 1.25):", parse_mode="HTML")
    bot.register_next_step_handler(msg, get_amount)

def get_amount(message):
    amount = message.text
    msg = bot.send_message(message.chat.id, "👤 <b>Step 2:</b> Enter Customer Name:", parse_mode="HTML")
    bot.register_next_step_handler(msg, get_name, amount)

def get_name(message, amount):
    name = message.text.upper()
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Using '|' as a safe separator
    markup.add(
        types.InlineKeyboardButton("ABA PayWay", callback_data=f"bk|ABA|{amount}|{name}"),
        types.InlineKeyboardButton("ACLEDA Bank", callback_data=f"bk|ACL|{amount}|{name}"),
        types.InlineKeyboardButton("TrueMoney", callback_data=f"bk|TRU|{amount}|{name}"),
        types.InlineKeyboardButton("Wing Bank", callback_data=f"bk|WNG|{amount}|{name}")
    )
    
    bot.send_message(message.chat.id, f"🏦 <b>Step 3:</b> Select Bank for {name}:", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith('bk|'))
def handle_finish(call):
    _, bank, amount, name = call.data.split('|')
    
    # PHNOM PENH TIMEZONE FIX (UTC+7)
    now = datetime.utcnow() + timedelta(hours=7)
    
    if bank == "ABA":
        # THE EXACT ABA STYLE
        trx_id = generate_digits(15)
        apv = generate_digits(6)
        last_three = generate_digits(3)
        
        res = (
            f"PayWay by ABA\n\n"
            f"${amount} paid by {name}\n\n"
            f"(*{last_three}) on {now.strftime('%b %d')}, {now.strftime('%I:%M %p')} "
            f"via ABA PAY at {STORE_NAME}. "
            f"Trx. ID: {trx_id}, APV: {apv}.\n\n"
            f"{now.strftime('%H:%M')}"
        )
    
    elif bank == "ACL":
        res = (
            f"📋 <b>ACLEDA Bank Receipt</b>\n"
            f"✅ <b>ប្រតិបត្តិការ ជោគជ័យ</b>\n"
            f"កាលបរិច្ឆេទ: {now.strftime('%d %b %Y @ %I:%M %p')}\n"
            f"លេខប្រតិបត្តិការ: <code>{generate_mixed(8)}</code>\n"
            f"---------------------------\n"
            f"ពី: <b>{name}</b>\n"
            f"ទៅ: <b>{RECEIVER_NAME}</b>\n"
            f"លេខយោង: <code>{generate_mixed(8)}</code>\n"
            f"---------------------------\n"
            f"💰 <b>ទឹកប្រាក់: USD {amount}</b>\n"
            f"---------------------------\n"
            f"🙏 Thank you for your purchase!"
        )

    elif bank == "TRU":
        res = (
            f"🔸 <b>TrueMoney Transfer</b>\n\n"
            f"Received <b>USD {amount}</b> from <b>{name}</b>\n"
            f"Ref ID: <code>{generate_digits(10)}</code>\n"
            f"Date: {now.strftime('%d/%m/%Y %H:%M')}\n"
            f"Status: SUCCESSFUL"
        )

    elif bank == "WNG":
        res = (
            f"💸 <b>Wing Money Received</b>\n\n"
            f"You have received <b>${amount}</b> from <b>{name}</b>.\n"
            f"Transaction ID: <code>{generate_digits(9)}</code>\n"
            f"Time: {now.strftime('%I:%M %p')}\n\n"
            f"{STORE_NAME} - Wing Merchant"
        )

    try:
        bot.send_message(PROOF_CHANNEL_ID, res, parse_mode="HTML")
        bot.edit_message_text("✅ Receipt posted to channel!", call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Error: {e}")

bot.infinity_polling()

