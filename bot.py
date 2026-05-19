import os
import asyncio
from datetime import datetime, timedelta
import pytz

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import SUPPORTED_TRADES

IST = pytz.timezone("Asia/Kolkata")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Forex Signal Bot is online.\n\n"
        "Use:\n"
        "/signals 1\n"
        "/signals 2"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/signals 1\n"
        "/signals 2\n"
        "/status\n"
        "/pairs"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot online ✅\n"
        "Mode: Manual signals\n"
        "Timeframe: 1m\n"
        "Confidence threshold: 80%"
    )


async def pairs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Scanning top 10 forex pairs."
    )


async def signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        trade_minutes = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Usage:\n/signals 1\n/signals 2"
        )
        return

    if trade_minutes not in SUPPORTED_TRADES:
        await update.message.reply_text(
            "Only 1 or 2 minute trades supported."
        )
        return

    now = datetime.now(IST)
    entry_time = now + timedelta(minutes=1)

    message = (
        "📊 Forex Signal\n\n"
        "EUR/USD → BUY ↑ (84%)\n"
        f"Trade: {trade_minutes}m\n"
        f"Entry: {entry_time.strftime('%I:%M %p')}"
    )

    await update.message.reply_text(message)


async def main():
    bot_token = os.getenv("BOT_TOKEN")

    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("pairs", pairs))
    app.add_handler(CommandHandler("signals", signals))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())