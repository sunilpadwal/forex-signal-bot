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
            "⏳ Scanning OTC + forex pairs..."
        )

    elif signal_type == "2m":
        await query.edit_message_text(
            "⏱️ 2 Minute Signal Selected\n\n"
            "🔍 Logging into Quotex...\n"
            "⏳ Scanning OTC + forex pairs..."
        )

    else:
        await query.edit_message_text(
            "🔥 Best Signal Mode\n\n"
            "🔍 Logging into Quotex...\n"
            "⏳ Finding highest probability pair..."
        )

    # Debug check for environment variables
    email = os.getenv("QUOTEX_EMAIL")
    password = os.getenv("QUOTEX_PASSWORD")

    if not email or not password:
        await query.message.reply_text(
            "❌ Quotex credentials missing in Render Environment Variables"
        )
        return

    await query.message.reply_text(
        f"✅ Quotex credentials found\n📧 {email}"
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

    app.run_polling(drop_pending_updates=True)


# ==========================
# Run app
# ==========================

if __name__ == "__main__":
    main()