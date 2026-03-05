import telebot
from telebot import types
import datetime
import secrets
import string
import os

# --- CONFIGURATION (Settings from Koyeb Env Vars) ---
API_TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID', '0')) 
PROOF_CHANNEL_ID = os.getenv('CHANNEL_ID')
# -----------------------------------------------------------

bot = telebot.TeleBot(API_TOKEN)

def generate_digits(length):
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def generate_mixed(length):
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))

@bot.message_handler(commands=['start', 'pay'])
def start_handler(message):
    if message.from_user.id != OWNER_ID:
        return 
    msg = bot.send_message(message.chat.id, "💰 <b>Step 1:</b> Enter the amount (e.g., 5.00):", parse_mode="HTML")
    bot.register_next_step_handler(msg, get_amount)

def get_amount(message):
    amount = message.text
    msg = bot.send_message(message.chat.id, "👤 <b>Step 2:</b> Enter Customer Name:", parse_mode="HTML")
    bot.register_next_step_handler(msg, get_name, amount)

def get_name(message, amount):
    name = message.text.upper()
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # 4 Bank Options with unique callback data
    markup.add(
        types.InlineKeyboardButton("ABA PayWay", callback_data=f"bk_ABA_{amount}_{name}"),
        types.InlineKeyboardButton("ACLEDA Bank", callback_data=f"bk_ACL_{amount}_{name}"),
        types.InlineKeyboardButton("TrueMoney", callback_data=f"bk_TRU_{amount}_{name}"),
        types.InlineKeyboardButton("Wing Bank", callback_data=f"bk_WNG_{amount}_{name}")
    )
    
    bot.send_message(message.chat.id, f"🏦 <b>Step 3:</b> Select Bank for {name}:", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith('bk_'))
def handle_finish(call):
    _, bank, amount, name = call.data.split('_')
    now = datetime.datetime.now()
    
    if bank == "ABA":
        # EXACT PayWay Style
        trx_id = generate_digits(15)
        apv = generate_digits(6)
        date_str = now.strftime('%b %d')
        time_str = now.strftime('%I:%M %p')
        short_time = now.strftime('%H:%M')
        
        res = (
            f"<b>PayWay by ABA</b>\n\n"
            f"<b>${amount}</b> paid by <b>{name}</b>\n\n"
            f"(*{generate_digits(3)}) on {date_str}, {time_str} "
            f"via <b>ABA PAY</b> at <b>AISI STORE</b>. "
            f"Trx. ID: <code>{trx_id}</code>, APV: <code>{apv}</code>.\n\n"
            f"{short_time}"
        )
    
    elif bank == "ACL":
        # ACLEDA 5.0 Style
        res = (
            f"📋 <b>ACLEDA Bank Receipt</b>\n"
            f"✅ <b>ប្រតិបត្តិការ ជោគជ័យ</b>\n"
            f"កាលបរិច្ឆេទ: {now.strftime('%d %b %Y @ %I:%M %p')}\n"
            f"លេខប្រតិបត្តិការ: <code>{generate_mixed(8)}</code>\n"
            f"---------------------------\n"
            f"👤 ពី: <b>{name}</b>\n"
            f"👤 ទៅ: <b>AISI STORE</b>\n"
            f"លេខយោង: <code>{secrets.token_hex(4)}</code>\n"
            f"---------------------------\n"
            f"💰 <b>ទឹកប្រាក់: USD {amount}</b>\n"
            f"---------------------------\n"
            f"🙏 Thank you for your purchase!"
        )

    elif bank == "TRU":
        # TrueMoney Notification Style
        res = (
            f"🔸 <b>TrueMoney Transfer</b>\n\n"
            f"Received <b>USD {amount}</b> from <b>{name}</b>\n"
            f"Ref ID: <code>{generate_digits(10)}</code>\n"
            f"Date: {now.strftime('%d/%m/%Y %H:%M')}\n"
            f"Status: <pre>SUCCESSFUL</pre>"
        )

    elif bank == "WNG":
        # Wing Money Style
        res = (
            f"💸 <b>Wing Money Received</b>\n\n"
            f"You have received <b>${amount}</b> from <b>{name}</b>.\n"
            f"Transaction ID: <code>{generate_digits(9)}</code>\n"
            f"Time: {now.strftime('%I:%M %p')}\n\n"
            f"AISI STORE - Wing Merchant"
        )

    try:
        bot.send_message(PROOF_CHANNEL_ID, res, parse_mode="HTML")
        bot.answer_callback_query(call.id, "✅ Posted to Channel")
        bot.edit_message_text("✅ Proof successfully sent to channel!", call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ <b>Error:</b>\n{e}", parse_mode="HTML")

print("Fake Payment Bot is running...")
bot.infinity_polling()
