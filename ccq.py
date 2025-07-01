import random
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# NEW IMPORTS
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 1. /gen command – Card generator
async def gen_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        bin_format = context.args[0]
        if len(bin_format) != 6 or not bin_format.isdigit():
            await update.message.reply_text("Usage: /gen <6-digit BIN>")
            return

        generated_cards = []
        for _ in range(10):
            cc = bin_format + ''.join(random.choices('0123456789', k=10))
            mm = str(random.randint(1, 12)).zfill(2)
            yy = str(random.randint(25, 30))
            cvv = ''.join(random.choices('0123456789', k=3))
            generated_cards.append(f"{cc}|{mm}|{yy}|{cvv}")

        # Creating the formatted message
message = f"""
CC Generated Successfully
------------------------------
Amount ➜ 10

{"\n".join(generated_cards)}

Info ➜ {brand} - {card_type} - STANDARD PREPAID GENERAL SPEND
Bank ➜ {user.first_name} LIMITED
Country ➜ {country} {emoji}
Time ➜ {generation_time} seconds
Checked By ➜ {username}
[ FREE ]
"""

# Send the message with the generated card details
await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text("Error generating cards.")

# 2. .chk command – BIN checker with simulated Approved/Declined result
async def chk_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message.text
        if not message.startswith(".chk"):
            return

        parts = message.split()
        if len(parts) != 2:
            await update.message.reply_text("Usage: .chk <cc|mm|yy|cvv>")
            return

        cc_details = parts[1].split("|")
        if len(cc_details) != 4:
            await update.message.reply_text("Invalid card format.")
            return

        cc, mm, yy, cvv = cc_details
        bin_number = cc[:6]
        headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get(f"https://lookup.binlist.net/{bin_number}", headers=headers)
print(f"DEBUG: BIN lookup status {r.status_code}, response: {r.text}")
        if r.status_code != 200:
            await update.message.reply_text("BIN not found.")
            return

        data = r.json()
        brand = data.get("scheme", "Unknown").upper()
        card_type = data.get("type", "Unknown").upper()
        category = "PREPAID" if data.get("prepaid", False) else "DEBIT"
        issuer = data.get("bank", {}).get("name", "Unknown")
        country = data.get("country", {}).get("name", "Unknown")
        country_code = data.get("country", {}).get("numeric", "000")
        emoji = data.get("country", {}).get("emoji", "")

        import random
        status = random.choice(["Approved ✅", "Declined ❌"])
        response = "Card added" if "Approved" in status else "Your card was declined"
        gateway = "Stripe"

        user = update.effective_user
        username = user.username or user.first_name

        msg = f"""
CC: {cc}|{mm}|20{yy}|{cvv}
Status: {status}
Response: {response}
Gateway: {gateway}
Bank: {issuer}
Category: {category}
Type: {card_type} {brand}
Country: {country.upper()} - {country_code}
Took: {round(random.uniform(6.0, 9.5), 2)}s
Checked by: {username}
"""

await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text("Error checking card.")
    
# 3. /bin command – Full BIN lookup
async def bin_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args or not args[0].isdigit() or len(args[0]) < 6:
            await update.message.reply_text("Usage: /bin <6-digit BIN>")
            return

        bin_number = args[0]
        user = update.effective_user

        # Try to get BIN data
        r = requests.get(f"https://lookup.binlist.net/{bin_number}")
        
        if r.status_code != 200:
            await update.message.reply_text("BIN not found.")
            return

        data = r.json()

        if "scheme" not in data:
            await update.message.reply_text("No valid BIN data found.")
            return

        brand = data.get("scheme", "Unknown").upper()
        card_type = data.get("type", "Unknown").upper()
        category = "PREPAID" if data.get("prepaid", False) else "DEBIT"
        issuer = data.get("bank", {}).get("name", "Unknown")
        country = data.get("country", {}).get("name", "Unknown")
        emoji = data.get("country", {}).get("emoji", "")

        message = f"""
⊗ Bin: {bin_number}
⊗ Info: {brand} - {card_type} - {category}
⊗ Issuer: {issuer}
⊗ Country: {country} {emoji}

⊗ Checked By ➜ ------{user.first_name.upper()} ☠️
"""
        await update.message.reply_text(message)
        
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# /start command – Welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Hey there, welcome to the Bot!\n\n"
        "I'm here to help you generate and check cards.\n"
        "Use /gen to generate cards, .chk to check them, or /bin to look up BIN info.\n\n"
        "Bot Owner: @RitikXyz099"
    )
    await update.message.reply_text(welcome_message)

# /help command – Show all available commands
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Here are the available commands:\n\n"
        "/start - Welcome message\n"
        "/help - Show this help message\n"
        "/gen <6-digit BIN> - Generate test cards using a BIN\n"
        ".chk <cc|mm|yy|cvv> - Check card with simulated result\n"
        "/bin <6-digit BIN> - Look up BIN information\n\n"
        "Bot Owner: @RitikXyz099"
    )
    await update.message.reply_text(help_text)

# Bot start
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("gen", gen_cards))
    app.add_handler(CommandHandler("bin", bin_lookup))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^\.chk "), chk_handler))

    print("Bot is running...")
    app.run_polling()