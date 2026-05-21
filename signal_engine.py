import time
import requests
import pandas as pd
from datetime import datetime, timedelta

from config import (
    BASE_URL,
    TWELVE_DATA_API_KEY,
    MIN_CONFIDENCE,
    SCAN_INTERVAL,
    MAX_SCAN_PAIRS,
)

from indicators import (
    add_indicators,
    calculate_signal,
)

from forex_pairs import FOREX_PAIRS


# ==========================================
# Get Candle Data
# ==========================================

def fetch_market_data(symbol, interval="1min", outputsize=100):

    try:
        url = (
            f"{BASE_URL}/time_series"
            f"?symbol={symbol}"
            f"&interval={interval}"
            f"&outputsize={outputsize}"
            f"&apikey={TWELVE_DATA_API_KEY}"
        )

        response = requests.get(url, timeout=15)
        data = response.json()

        if "values" not in data:
            return None

        df = pd.DataFrame(data["values"])

        df = df.rename(columns={
            "datetime": "time"
        })

        numeric_cols = [
            "open",
            "high",
            "low",
            "close",
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col])

        df = df.iloc[::-1].reset_index(drop=True)

        return df

    except Exception as e:
        print(f"Fetch error {symbol}: {e}")
        return None


# ==========================================
# Next Minute Entry Timing
# ==========================================

def get_entry_and_expiry(duration_minutes):

    now = datetime.now()

    next_minute = (
        now.replace(second=0, microsecond=0)
        + timedelta(minutes=1)
    )

    expiry = (
        next_minute
        + timedelta(minutes=duration_minutes)
    )

    return next_minute, expiry


# ==========================================
# Scan One Pair
# ==========================================

def analyze_pair(pair, duration_minutes):

    interval = "1min"

    df = fetch_market_data(pair, interval)

    if df is None or len(df) < 50:
        return None

    df = add_indicators(df)

    result = calculate_signal(df)

    confidence = result["confidence"]

    if confidence < MIN_CONFIDENCE:
        return None

    entry_time, expiry_time = (
        get_entry_and_expiry(duration_minutes)
    )

    return {
        "pair": pair,
        "direction": result["direction"],
        "confidence": confidence,
        "reasons": result["reasons"],
        "duration": duration_minutes,
        "entry_time": entry_time,
        "expiry_time": expiry_time,
    }


# ==========================================
# Best Dynamic Signal
# ==========================================

def find_best_dynamic_signal():

    print("Scanning market...")

    while True:

        best_signal = None
        best_confidence = 0

        for pair in FOREX_PAIRS[:MAX_SCAN_PAIRS]:

            try:

                signal_1m = analyze_pair(
                    pair,
                    duration_minutes=1
                )

                signal_2m = analyze_pair(
                    pair,
                    duration_minutes=2
                )

                signals = [
                    signal_1m,
                    signal_2m
                ]

                for signal in signals:

                    if not signal:
                        continue

                    confidence = signal["confidence"]

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_signal = signal

            except Exception as e:
                print(f"Pair error {pair}: {e}")

        if best_signal:
            print(
                f"Best setup found: "
                f"{best_signal['pair']}"
            )
            return best_signal

        print("No strong setup found...")
        time.sleep(SCAN_INTERVAL)