import time
import requests
import pandas as pd

from datetime import (
    datetime,
    timedelta
)

from config import (
    BASE_URL,
    FCS_API_KEY,
    MIN_CONFIDENCE,
    SCAN_INTERVAL,
    MAX_SCAN_PAIRS,
    SUPPORTED_EXPIRIES,
)

from indicators import (
    add_indicators,
    calculate_signal
)

from forex_pairs import (
    FOREX_PAIRS
)


# ==========================================
# Symbol Fix
# EUR/USD -> EURUSD
# ==========================================

def format_symbol(symbol):

    symbol = symbol.replace("/", "")
    symbol = symbol.replace("_", "")

    return symbol.upper()


# ==========================================
# Fetch Candle Data
# ==========================================

def fetch_market_data(
    symbol,
    period="1m"
):

    try:

        symbol = format_symbol(
            symbol
        )

        url = (
            f"{BASE_URL}/forex/history"
            f"?symbol={symbol}"
            f"&period={period}"
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

        candles = []

        response_data = (
            data["response"]
        )

        for _, candle in (
            response_data.items()
        ):

            candles.append({
                "open": float(
                    candle["o"]
                ),
                "high": float(
                    candle["h"]
                ),
                "low": float(
                    candle["l"]
                ),
                "close": float(
                    candle["c"]
                ),
                "time": candle["tm"]
            })

        df = pd.DataFrame(
            candles
        )

        if len(df) < 50:
            return None

        return df

    except Exception as e:

        print(
            f"Fetch error "
            f"{symbol}: {e}"
        )

        return None


# ==========================================
# Entry / Expiry Timing
# ==========================================

def get_trade_timing(
    expiry_minutes
):

    now = datetime.now()

    entry_time = (
        now.replace(
            second=0,
            microsecond=0
        )
        + timedelta(
            minutes=1
        )
    )

    expiry_time = (
        entry_time
        + timedelta(
            minutes=expiry_minutes
        )
    )

    return (
        entry_time,
        expiry_time
    )


# ==========================================
# Analyze One Pair
# ==========================================

def analyze_pair(
    pair,
    expiry_minutes
):

    try:

        df = fetch_market_data(
            pair,
            period="1m"
        )

        if (
            df is None
            or len(df) < 50
        ):
            return None

        df = add_indicators(df)

        signal = calculate_signal(
            df
        )

        confidence = signal[
            "confidence"
        ]

        if (
            confidence
            < MIN_CONFIDENCE
        ):
            return None

        (
            entry_time,
            expiry_time
        ) = get_trade_timing(
            expiry_minutes
        )

        return {
            "pair": pair,
            "direction":
                signal[
                    "direction"
                ],
            "confidence":
                confidence,
            "reasons":
                signal[
                    "reasons"
                ],
            "duration":
                expiry_minutes,
            "entry_time":
                entry_time,
            "expiry_time":
                expiry_time,
        }

    except Exception as e:

        print(
            f"Analyze error "
            f"{pair}: {e}"
        )

        return None


# ==========================================
# Best Dynamic Mode
# Auto choose 1m or 2m
# ==========================================

def find_best_dynamic_signal():

    print(
        "Scanning market..."
    )

    while True:

        best_signal = None
        best_score = 0

        for pair in (
            FOREX_PAIRS[
                :MAX_SCAN_PAIRS
            ]
        ):

            try:

                for expiry in (
                    SUPPORTED_EXPIRIES
                ):

                    signal = (
                        analyze_pair(
                            pair,
                            expiry
                        )
                    )

                    if not signal:
                        continue

                    confidence = (
                        signal[
                            "confidence"
                        ]
                    )

                    if (
                        confidence
                        > best_score
                    ):

                        best_score = (
                            confidence
                        )

                        best_signal = (
                            signal
                        )

            except Exception as e:

                print(
                    f"Pair error "
                    f"{pair}: {e}"
                )

        if best_signal:

            print(
                f"Best signal "
                f"{best_signal['pair']}"
            )

            return best_signal

        print(
            "No strong setup "
            "found..."
        )

        time.sleep(
            SCAN_INTERVAL
        )