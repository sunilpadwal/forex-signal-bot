from datetime import datetime, timedelta
import random

import pytz
import yfinance as yf

from forex_pairs import FOREX_PAIRS

IST = pytz.timezone("Asia/Kolkata")


def get_best_signal(trade_minutes=1):
    best_signal = None
    best_score = 0

    for pair in FOREX_PAIRS:
        try:
            data = yf.download(
                pair,
                period="1d",
                interval="1m",
                progress=False
            )

            if data.empty or len(data) < 30:
                continue

            close_prices = data["Close"].tolist()

            last_price = close_prices[-1]
            avg_5 = sum(close_prices[-5:]) / 5
            avg_20 = sum(close_prices[-20:]) / 20

            direction = "BUY ↑" if avg_5 > avg_20 else "SELL ↓"

            score = 70

            if abs(avg_5 - avg_20) / last_price > 0.0002:
                score += 10

            score += random.randint(0, 15)

            if score < 80:
                continue

            if score > best_score:
                best_score = score

                entry_time = (
                    datetime.now(IST)
                    + timedelta(minutes=1)
                ).strftime("%I:%M %p")

                best_signal = {
                    "pair": pair.replace("=X", ""),
                    "direction": direction,
                    "score": score,
                    "entry": entry_time,
                    "trade": trade_minutes
                }

        except Exception:
            continue

    return best_signal