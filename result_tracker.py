import asyncio
import requests
from datetime import datetime

from config import (
    BASE_URL,
    TWELVE_DATA_API_KEY,
    PIP_MULTIPLIER,
)


# ==========================================
# Get latest price
# ==========================================

def get_live_price(symbol):

    try:
        url = (
            f"{BASE_URL}/price"
            f"?symbol={symbol}"
            f"&apikey={TWELVE_DATA_API_KEY}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        if "price" not in data:
            return None

        return float(data["price"])

    except Exception as e:
        print(
            f"Price fetch error "
            f"{symbol}: {e}"
        )
        return None


# ==========================================
# Result tracking
# ==========================================

async def track_trade_result(
    bot,
    chat_id,
    signal
):

    try:

        pair = signal["pair"]
        direction = signal["direction"]

        entry_time = signal["entry_time"]
        expiry_time = signal["expiry_time"]

        # ==================================
        # Wait for entry
        # ==================================

        now = datetime.now()

        wait_entry = (
            entry_time - now
        ).total_seconds()

        if wait_entry > 0:
            await asyncio.sleep(wait_entry)

        # Entry price
        entry_price = get_live_price(pair)

        if entry_price is None:
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    f"❌ Could not fetch "
                    f"entry price for {pair}"
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
            await asyncio.sleep(wait_expiry)

        exit_price = get_live_price(pair)

        if exit_price is None:
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    f"❌ Could not fetch "
                    f"exit price for {pair}"
                )
            )
            return

        # ==================================
        # Result logic
        # ==================================

        if direction == "BUY":

            passed = (
                exit_price > entry_price
            )

            pip_move = (
                (exit_price - entry_price)
                * PIP_MULTIPLIER
            )

        else:

            passed = (
                exit_price < entry_price
            )

            pip_move = (
                (entry_price - exit_price)
                * PIP_MULTIPLIER
            )

        status = (
            "✅ RESULT: PASS"
            if passed
            else "❌ RESULT: FAIL"
        )

        emoji = (
            "📈"
            if direction == "BUY"
            else "📉"
        )

        message = (
            f"{status}\n\n"
            f"Pair: {pair}\n"
            f"{direction} {emoji}\n\n"
            f"Entry: {entry_price:.5f}\n"
            f"Exit: {exit_price:.5f}\n\n"
            f"Profit Move: "
            f"{pip_move:+.1f} pips"
        )

        await bot.send_message(
            chat_id=chat_id,
            text=message
        )

    except Exception as e:

        print(
            f"Result tracker error: {e}"
        )