import asyncio
import os

from threading import Thread
from datetime import datetime, timedelta

from flask import Flask

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from forex_pairs import FOREX_PAIRS
from signal_engine import analyze_pair
from result_tracker import track_result
from config import (
    BOT_TOKEN,
    ENTRY_BUFFER_SECONDS
)

# =====================================
# Flask for Render
# =====================================

app_web = Flask(__name__)


@app_web.route("/")
def home():
    return "Bot running"


def run_web():
    port = int(
        os.environ.get("PORT", 10000)
    )

    app_web.run(
        host="0.0.0.0",
        port=port
    )


# =====================================
# START COMMAND
# =====================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                "🔥 Best Dynamic",
                callback_data="best"
            )
        ],
        [
            InlineKeyboardButton(
                "⚡ 1 Minute",
                callback_data="1"
            )
        ],
        [
            InlineKeyboardButton(
                "⏱️ 2 Minute",
                callback_data="2"
            )
        ]
    ]

    markup = InlineKeyboardMarkup(
        keyboard
    )

    await update.message.reply_text(
        "Choose signal mode:",
        reply_markup=markup
    )


# =====================================
# SIGNAL BUTTON
# =====================================

async def button_click(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    mode = query.data

    await query.edit_message_text(
        "🔍 Scanning market...\n"
        "📊 Checking indicators..."
    )

    best_signal = None

    for pair in FOREX_PAIRS:

        try:

            if mode == "1":
                signal = analyze_pair(
                    pair,
                    forced_expiry=1
                )

            elif mode == "2":
                signal = analyze_pair(
                    pair,
                    forced_expiry=2
                )

            else:
                signal = analyze_pair(pair)

            if signal:

                if (
                    best_signal is None
                    or signal["confidence"]
                    > best_signal["confidence"]
                ):
                    best_signal = signal

        except Exception:
            pass

    if not best_signal:

        await query.message.reply_text(
            "❌ No strong setup found"
        )
        return

    now = datetime.now()

    next_minute = (
        now.replace(
            second=0,
            microsecond=0
        )
        + timedelta(minutes=1)
    )

    entry_time = (
        next_minute
        - timedelta(
            seconds=ENTRY_BUFFER_SECONDS
        )
    )

    exit_time = (
        next_minute
        + timedelta(
            minutes=best_signal["expiry"]
        )
    )

    reasons_text = "\n".join(
        [
            f"✅ {x}"
            for x
            in best_signal["reasons"]
        ]
    )

    message = (

        f"🚨 SIGNAL FOUND 🚨\n\n"

        f"📊 Pair: "
        f"{best_signal['symbol']}\n"

        f"📈 Signal: "
        f"{best_signal['direction']}\n"

        f"🎯 Confidence: "
        f"{best_signal['confidence']}%\n"

        f"⏳ Expiry: "
        f"{best_signal['expiry']} Minute\n\n"

        f"⏰ Entry Time:\n"
        f"{entry_time.strftime('%H:%M:%S')}\n\n"

        f"🏁 Exit Time:\n"
        f"{exit_time.strftime('%H:%M:%S')}\n\n"

        f"💰 Entry Price:\n"
        f"{best_signal['entry_price']:.5f}\n\n"

        f"📌 Reasons:\n"
        f"{reasons_text}"
    )

    await query.message.reply_text(
        message
    )

    asyncio.create_task(
        track_result(
            context.bot,
            query.message.chat.id,
            best_signal
        )
    )


# =====================================
# MAIN
# =====================================

def main():

    Thread(
        target=run_web,
        daemon=True
    ).start()

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button_click
        )
    )

    print(
        "🤖 Bot started..."
    )

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()