import asyncio
import requests

from datetime import datetime

from config import (
    BASE_URL,
    FCS_API_KEY,
    PIP_MULTIPLIER
)


# ==========================================
# Format Symbol
# ==========================================

def format_symbol(symbol):

    symbol = symbol.replace("/", "")
    symbol = symbol.replace("_", "")

    return symbol.upper()


# ==========================================
# Get Live Price
# ==========================================

def get_live_price(symbol):

    try:

        symbol = format_symbol(
            symbol
        )

        url = (
            f"{BASE_URL}/forex/latest"
            f"?symbol={symbol}"
            f"&access_key={FCS_API_KEY}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        if (
            not data.get("status")
            or "response"
            not in data
        ):
            return None

        result = data["response"]

        if not result:
            return None

        active = result[0].get(
            "active",
            {}
        )

        price = active.get("c")

        if price is None:
            return None

        return float(price)

    except Exception as e:

        print(
            f"Price fetch error "
            f"{symbol}: {e}"
        )

        return None


# ==========================================
# Track Trade Result
# ==========================================

async def track_trade_result(
    bot,
    chat_id,
    signal
):

    try:

        pair = signal["pair"]
        direction = signal[
            "direction"
        ]

        entry_time = signal[
            "entry_time"
        ]

        expiry_time = signal[
            "expiry_time"
        ]

        # ==================================
        # Wait for entry
        # ==================================

        now = datetime.now()

        wait_entry = (
            entry_time - now
        ).total_seconds()

        if wait_entry > 0:

            await asyncio.sleep(
                wait_entry
            )

        # Capture entry price
        entry_price = (
            get_live_price(pair)
        )

        if entry_price is None:

            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "❌ Could not "
                    f"fetch entry "
                    f"price for "
                    f"{pair}"
                )
            )

            return

        # ==================================
        # Wait for expiry
        # ==================================

        now = datetime.now()

        wait_expiry = (
            expiry_time - now
        ).total_seconds()

        if wait_expiry > 0:

            await asyncio.sleep(
                wait_expiry
            )

        exit_price = (
            get_live_price(pair)
        )

        if exit_price is None:

            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "❌ Could not "
                    f"fetch exit "
                    f"price for "
                    f"{pair}"
                )
            )

            return

        # ==================================
        # Result Logic
        # ==================================

        if direction == "BUY":

            passed = (
                exit_price
                > entry_price
            )

            pip_move = (
                (
                    exit_price
                    - entry_price
                )
                * PIP_MULTIPLIER
            )

        else:

            passed = (
                exit_price
                < entry_price
            )

            pip_move = (
                (
                    entry_price
                    - exit_price
                )
                * PIP_MULTIPLIER
            )

        status = (
            "✅ RESULT: PASS"
            if passed
            else
            "❌ RESULT: FAIL"
        )

        emoji = (
            "📈"
            if direction
            == "BUY"
            else "📉"
        )

        message = (
            f"{status}\n\n"
            f"Pair: {pair}\n"
            f"{direction} "
            f"{emoji}\n\n"
            f"Entry: "
            f"{entry_price:.5f}\n"
            f"Exit: "
            f"{exit_price:.5f}\n\n"
            f"Profit Move: "
            f"{pip_move:+.1f} "
            f"pips"
        )

        await bot.send_message(
            chat_id=chat_id,
            text=message
        )

    except Exception as e:

        print(
            f"Result tracker "
            f"error: {e}"
        )