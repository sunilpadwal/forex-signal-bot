import time
from datetime import datetime, timedelta

from signal_engine import fetch_data


async def track_result(
    bot,
    chat_id,
    signal
):

    symbol = signal["symbol"]
    expiry = signal["expiry"]
    direction = signal["direction"]

    entry_price = signal["entry_price"]

    # wait until expiry ends
    wait_seconds = expiry * 60

    time.sleep(wait_seconds)

    df = fetch_data(symbol)

    if df is None:
        await bot.send_message(
            chat_id=chat_id,
            text="❌ Failed to fetch result data"
        )
        return

    exit_price = float(
        df.iloc[-1]["close"]
    )

    if direction == "BUY":
        passed = exit_price > entry_price
    else:
        passed = exit_price < entry_price

    result = "✅ PASS" if passed else "❌ FAIL"

    await bot.send_message(
        chat_id=chat_id,
        text=(
            f"{result}\n\n"
            f"📊 Pair: {symbol}\n"
            f"📈 Direction: {direction}\n\n"
            f"💰 Entry Price: {entry_price:.5f}\n"
            f"🏁 Exit Price: {exit_price:.5f}"
        )
    )