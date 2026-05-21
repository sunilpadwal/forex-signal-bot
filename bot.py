import os
import asyncio
from threading import Thread
from flask import Flask

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from signal_engine import find_best_dynamic_signal
from result_tracker import track_trade_result


# ==========================================
# Flask (Render keep alive)
# ==========================================

app_web = Flask(__name__)


@app_web.route("/")
def home():
    return "Forex Signal Bot Running ✅"


def run_web():
    port = int(
        os.environ.get("PORT", 10000)
    )

    app_web.run(
        host="0.0.0.0",
        port=port
    )


# ==========================================
# /start
# ==========================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                "🔥 Best Dynamic",
                callback_data="best_dynamic"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(
        keyboard
    )

    await update.message.reply_text(
        "Choose Signal Mode:",
        reply_markup=reply_markup
    )


# ==========================================
# Signal Button
# ==========================================

async def button_click(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🔥 Best Dynamic Mode\n\n"
        "🔍 Scanning market...\n"
        "⏳ Looking for best setup..."
    )

    try:

        signal = await asyncio.to_thread(
            find_best_dynamic_signal
        )

        if not signal:

            await query.message.reply_text(
                "❌ No strong setup found"
            )
            return

        pair = signal["pair"]
        direction = signal["direction"]
        confidence = signal["confidence"]

        entry_time = signal[
            "entry_time"
        ].strftime("%H:%M:%S")

        expiry_time = signal[
            "expiry_time"
        ].strftime("%H:%M:%S")

        reasons = signal["reasons"]

        emoji = (
            "📈"
            if direction == "BUY"
            else "📉"
        )

        reason_text = (
            "\n".join(
                [
                    f"• {r}"
                    for r in reasons[:3]
                ]
            )
        )

        signal_message = (
            f"🚀 SIGNAL READY\n\n"
            f"Pair: {pair}\n"
            f"{direction} {emoji}\n\n"
            f"⏰ Entry Time: "
            f"{entry_time}\n"
            f"⏳ Expiry: "
            f"{expiry_time}\n\n"
            f"🔥 Confidence: "
            f"{confidence}%\n\n"
            f"Reason:\n"
            f"{reason_text}\n\n"
            f"Enter at start "
            f"of next candle."
        )

        await query.message.reply_text(
            signal_message
        )

        # ==================================
        # PASS / FAIL Tracking
        # ==================================

        asyncio.create_task(
            track_trade_result(
                context.bot,
                query.message.chat_id,
                signal
            )
        )

    except Exception as e:

        await query.message.reply_text(
            f"❌ Error:\n{str(e)}"
        )


# ==========================================
# Main
# ==========================================

def main():

    try:

        print(
            "🚀 Starting bot..."
        )

        if not BOT_TOKEN:
            raise Exception(
                "BOT_TOKEN missing"
            )

        print(
            "✅ BOT_TOKEN found"
        )

        Thread(
            target=run_web,
            daemon=True
        ).start()

        print(
            "✅ Flask started"
        )

        app = (
            ApplicationBuilder()
            .token(BOT_TOKEN)
            .build()
        )

        print(
            "✅ Telegram app created"
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
            "✅ Handlers added"
        )

        print(
            "🤖 Bot started..."
        )

        app.run_polling(
            drop_pending_updates=True,
            close_loop=False
        )

    except Exception as e:

        print(
            "❌ STARTUP ERROR:"
        )

        print(str(e))


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    main()