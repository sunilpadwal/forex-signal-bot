import os
import asyncio
import threading
from datetime import datetime, timedelta

import pytz
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import SUPPORTED_TRADES
from signal_engine import get_best_signal

IST = pytz.timezone("Asia/Kolkata")

# Tiny web server for Render
web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "Forex Signal Bot Running ✅"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Forex Signal Bot is online.\n\n"
        "Use:\n"
        "/signals 1\n"
        "/signals 2"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot online ✅"
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

    await update.message.reply_text(
        "Scanning forex market..."
    )

    signal = get_best_signal(trade_minutes)

    if not signal:
        await update.message.reply_text(
            "No high probability signal found right now."
        )
        return

    message = (
        "📊 Forex Signal\n\n"
        f"{signal['pair']} → {signal['direction']}\n"
        f"Confidence: {signal['score']}%\n"
        f"Trade: {signal['trade']}m\n"
        f"Entry: {signal['entry']}"
    )

    await update.message.reply_text(message)



async def run_bot():
    app = Application.builder().token(
        os.getenv("BOT_TOKEN")
    ).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("pairs", pairs))
    app.add_handler(CommandHandler("signals", signals))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    asyncio.run(run_bot())