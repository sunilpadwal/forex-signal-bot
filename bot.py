import os
import shutil
from threading import Thread
from flask import Flask

# ==========================================
# Render / Headless Chrome Fix
# ==========================================

os.environ["DISPLAY"] = ":99"
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Chrome path (Render)
os.environ["CHROME_BIN"] = "/usr/bin/google-chrome"
os.environ["GOOGLE_CHROME_BIN"] = "/usr/bin/google-chrome"

chrome_path = (
    shutil.which("google-chrome")
    or shutil.which("google-chrome-stable")
)

print("=" * 50)
print(f"Chrome path: {chrome_path}")
print("=" * 50)

# ==========================================
# Imports
# ==========================================

from quotexpy import Quotex
from forex_pairs import FOREX_PAIRS

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

# ==========================================
# Flask app (Render Web Service)
# ==========================================

app_web = Flask(__name__)


@app_web.route("/")
def home():
    return "Forex bot running!"


def run_web():
    port = int(os.environ.get("PORT", 10000))

    print(f"🌐 Flask running on port {port}")

    app_web.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )


# ==========================================
# Environment Variables
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
QUOTEX_EMAIL = os.getenv("QUOTEX_EMAIL")
QUOTEX_PASSWORD = os.getenv("QUOTEX_PASSWORD")


# ==========================================
# /start command
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "🔥 Best Signal",
                callback_data="best"
            )
        ],
        [
            InlineKeyboardButton(
                "⚡ 1 Minute",
                callback_data="1m"
            )
        ],
        [
            InlineKeyboardButton(
                "⏱️ 2 Minute",
                callback_data="2m"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📊 Choose Signal Mode:",
        reply_markup=reply_markup
    )


# ==========================================
# Button click
# ==========================================

async def button_click(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    signal_type = query.data

    # --------------------------------------
    # UI
    # --------------------------------------

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

    # --------------------------------------
    # Credentials check
    # --------------------------------------

    if not QUOTEX_EMAIL or not QUOTEX_PASSWORD:

        await query.message.reply_text(
            "❌ Missing Quotex credentials\n\n"
            "Add:\n"
            "QUOTEX_EMAIL\n"
            "QUOTEX_PASSWORD"
        )
        return

    try:

        # ----------------------------------
        # Chrome debug
        # ----------------------------------

        chrome_exists = (
            shutil.which("google-chrome")
            or shutil.which("google-chrome-stable")
        )

        print(f"Chrome detected: {chrome_exists}")

        if not chrome_exists:

            await query.message.reply_text(
                "❌ Chrome not installed on Render"
            )
            return

        await query.message.reply_text(
            "🔐 Connecting to Quotex..."
        )

        # ----------------------------------
        # Login Quotex
        # ----------------------------------

        client = Quotex(
            email=QUOTEX_EMAIL,
            password=QUOTEX_PASSWORD
        )

        connected = await client.connect()

        if not connected:

            await query.message.reply_text(
                "❌ Quotex login failed"
            )
            return

        await query.message.reply_text(
            "✅ Logged into Quotex\n"
            "🔍 Fetching OTC + Forex pairs..."
        )

        # ----------------------------------
        # Get assets
        # ----------------------------------

        assets = client.get_available_asset()

        available_pairs = []

        assets_string = str(assets)

        for pair in FOREX_PAIRS:

            try:

                if pair in assets_string:
                    available_pairs.append(pair)

            except Exception:
                pass

        total_pairs = len(available_pairs)

        # ----------------------------------
        # No pairs
        # ----------------------------------

        if total_pairs == 0:

            await query.message.reply_text(
                "❌ No OTC / Forex pairs found"
            )
            return

        # ----------------------------------
        # Send results
        # ----------------------------------

        message = (
            "📊 Available Forex + OTC Pairs\n\n"
        )

        for pair in available_pairs[:40]:
            message += f"✅ {pair}\n"

        message += (
            f"\n📈 Total Found: {total_pairs}"
        )

        await query.message.reply_text(
            message
        )

        print(
            f"✅ Found {total_pairs} pairs"
        )

    except Exception as e:

        print("ERROR:", str(e))

        await query.message.reply_text(
            f"❌ Error:\n{str(e)}"
        )


# ==========================================
# Main
# ==========================================

def main():

    try:

        print("=" * 50)
        print("🚀 Starting Bot")
        print("=" * 50)

        # Token check
        if not BOT_TOKEN:
            raise Exception(
                "BOT_TOKEN missing"
            )

        print("✅ BOT_TOKEN found")

        # Start Flask
        Thread(
            target=run_web,
            daemon=True
        ).start()

        print("✅ Flask started")

        # Telegram app
        app = (
            ApplicationBuilder()
            .token(BOT_TOKEN)
            .build()
        )

        print("✅ Telegram app created")

        # Handlers
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

        print("✅ Handlers added")
        print("🤖 Bot started...")

        app.run_polling(
            drop_pending_updates=True,
            close_loop=False
        )

    except Exception as e:

        print("❌ STARTUP ERROR")
        print(str(e))


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    main()