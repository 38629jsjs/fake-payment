import telebot
from telebot import types
import datetime
import secrets
import string
import os

# --- CONFIGURATION (Use Environment Variables for Koyeb) ---
API_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID', '123456789')) 
PROOF_CHANNEL_ID = os.getenv('CHANNEL_ID', '-100xxxxxxxxx')
# -----------------------------------------------------------

bot = telebot.TeleBot(API_TOKEN)

def generate_random_id(length=8, digits_only=False):
    chars = string.digits if digits_only else string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

@bot.message_handler(commands=['start', 'pay'])
def start_handler(message):
    if message.from_user.id != OWNER_ID:
        return 
    msg = bot.send_message(message.chat.id, "💰 **Step 1:** Enter the amount (e.g., 5.00):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_amount)

def get_amount(message):
    amount = message.text
    msg = bot.send_message(message.chat.id, "👤 **Step 2:** Enter Customer Name:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_name, amount)

def get_name(message, amount):
    name = message.text.upper()
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # The 4 Bank Options
    markup.add(
        types.InlineKeyboardButton("ABA PayWay", callback_data=f"bank_ABA_{amount}_{name}"),
        types.InlineKeyboardButton("ACLEDA", callback_data=f"bank_ACLEDA_{amount}_{name}"),
        types.InlineKeyboardButton("TrueMoney", callback_data=f"bank_TRUEMONEY_{amount}_{name}"),
        types.InlineKeyboardButton("Wing Bank", callback_data=f"bank_WING_{amount}_{name}")
    )
    
    bot.send_message(message.chat.id, f"🏦 **Step 3:** Select Bank for {name}:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('bank_'))
def handle_finish(call):
    _, bank, amount, name = call.data.split('_')
    now = datetime.datetime.now()
    
    # Format choice logic
    if bank == "ABA":
        # PayWay Style
        res = (f"**PayWay by ABA**\n\n**${amount}** paid by **{name}**\n\n"
               f"(*{secrets.token_hex(2).upper()}) on {now.strftime('%b %d')}, {now.strftime('%I:%M %p')} "
               f"via **ABA PAY** at **AISI STORE**. Trx. ID: `{generate_random_id(15, True)}`, "
               f"APV: `{generate_random_id(6, True)}`.\n\n🕒 {now.strftime('%H:%M')}")
    else:
        # Standard Receipt Style for others
        res = (f"📋 **{bank} Receipt**\n✅ **Success**\n🕒 {now.strftime('%d %b %Y @ %I:%M %p')}\n"
               f"Ref: `{generate_random_id(8)}`\n---------------------------\n"
               f"👤 **From:** {name}\n💰 **Amount: USD {amount}**\n---------------------------\n"
               f"🙏 Thank you!")

    bot.send_message(PROOF_CHANNEL_ID, res, parse_mode="Markdown")
    bot.edit_message_text("✅ Proof sent to channel!", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
