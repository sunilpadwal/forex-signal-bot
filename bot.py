import asyncio
from quotexpy import Quotex
from forex_pairs import FOREX_PAIRS
import os
from threading import Thread
from flask import Flask

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ==========================
# Flask app for Render
# ==========================

app_web = Flask(__name__)


@app_web.route("/")
def home():
    return "Bot is running!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)


# ==========================
# Telegram bot config
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")


# ==========================
# Start command
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🔥 Best Signal", callback_data="best")],
        [InlineKeyboardButton("⚡ 1 Minute", callback_data="1m")],
        [InlineKeyboardButton("⏱️ 2 Minute", callback_data="2m")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Choose signal mode:",
        reply_markup=reply_markup
    )


# ==========================
# Button click handler
# ==========================

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    signal_type = query.data

    if signal_type == "1m":
        await query.edit_message_text(
            "⚡ 1 Minute Signal Selected\n\n"
            "🔍 Logging into Quotex...\n"
            "⏳ Looking for fast setup..."
        )

    elif signal_type == "2m":
        await query.edit_message_text(
            "⏱️ 2 Minute Signal Selected\n\n"
            "🔍 Logging into Quotex...\n"
            "⏳ Looking for stronger setup..."
        )

    else:
        await query.edit_message_text(
            "🔥 Best Signal Mode\n\n"
            "🔍 Logging into Quotex...\n"
            "⏳ Finding highest probability pair..."
        )

    email = os.getenv("QUOTEX_EMAIL")
    password = os.getenv("QUOTEX_PASSWORD")

    if not email or not password:
        await query.message.reply_text(
            "❌ Quotex credentials missing"
        )
        return

    try:
        await query.message.reply_text(
            "🔐 Connecting to Quotex..."
        )

        client = Quotex(
            email=email,
            password=password
        )

        connected = await client.connect()

        if not connected:
            await query.message.reply_text(
                "❌ Quotex login failed"
            )
            return

        await query.message.reply_text(
            "✅ Logged into Quotex\n🔍 Fetching OTC + forex pairs..."
        )

        assets = await client.get_available_asset()

        total_pairs = len(assets)

        assets = await client.get_available_asset()

available_pairs = []

for pair in FOREX_PAIRS:
    try:
        if pair in str(assets):
            available_pairs.append(pair)
    except:
        pass

total_pairs = len(available_pairs)

message = "📊 Available Forex + OTC Pairs\n\n"

for pair in available_pairs[:30]:
    message += f"✅ {pair}\n"

message += f"\nTotal Found: {total_pairs}"

await query.message.reply_text(message)

    except Exception as e:
        await query.message.reply_text(
            f"❌ Error:\n{str(e)}"
        )


# ==========================
# Main bot runner
# ==========================

def main():

    # Start web server for Render
    Thread(target=run_web).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot started...")

    app.run_polling(
    drop_pending_updates=True,
    close_loop=False
)


# ==========================
# Run app
# ==========================

if __name__ == "__main__":
    main()