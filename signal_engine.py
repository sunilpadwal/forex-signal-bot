import requests
import pandas as pd

from indicators import (
    add_indicators,
    bullish_engulfing,
    bearish_engulfing,
    bullish_breakout,
    bearish_breakout
)

from config import (
    TWELVEDATA_API_KEY,
    MIN_CONFIDENCE
)


def fetch_data(symbol, interval="1min"):

    url = (
        "https://api.twelvedata.com/time_series"
    )

    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": 100,
        "apikey": TWELVEDATA_API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    data = response.json()

    if "values" not in data:
        return None

    df = pd.DataFrame(data["values"])

    df = df.iloc[::-1].reset_index(drop=True)

    numeric_cols = [
        "open",
        "high",
        "low",
        "close"
    ]

    for col in numeric_cols:
        df[col] = df[col].astype(float)

    return df


def analyze_pair(symbol, forced_expiry=None):

    df = fetch_data(symbol)

    if df is None:
        return None

    df = add_indicators(df)

    score_buy = 0
    score_sell = 0
    reasons = []

    latest = df.iloc[-1]

    # ======================
    # EMA Trend
    # ======================

    if latest["ema_fast"] > latest["ema_slow"]:
        score_buy += 20
        reasons.append("EMA Bullish")

    else:
        score_sell += 20
        reasons.append("EMA Bearish")

    # ======================
    # MACD
    # ======================

    if latest["macd"] > latest["macd_signal"]:
        score_buy += 15
        reasons.append("MACD Bullish")

    else:
        score_sell += 15
        reasons.append("MACD Bearish")

    # ======================
    # CCI
    # ======================

    if latest["cci"] > 100:
        score_buy += 15
        reasons.append("CCI Strong Bullish")

    elif latest["cci"] < -100:
        score_sell += 15
        reasons.append("CCI Strong Bearish")

    # ======================
    # Bollinger
    # ======================

    if latest["close"] > latest["bb_middle"]:
        score_buy += 10

    else:
        score_sell += 10

    # ======================
    # Candle Pattern
    # ======================

    if bullish_engulfing(df):
        score_buy += 20
        reasons.append("Bullish Engulfing")

    if bearish_engulfing(df):
        score_sell += 20
        reasons.append("Bearish Engulfing")

    # ======================
    # Price Action
    # ======================

    if bullish_breakout(df):
        score_buy += 20
        reasons.append("Bullish Breakout")

    if bearish_breakout(df):
        score_sell += 20
        reasons.append("Bearish Breakout")

    # ======================
    # Direction
    # ======================

    if score_buy > score_sell:

        direction = "BUY"
        confidence = score_buy

    else:

        direction = "SELL"
        confidence = score_sell

    if confidence < MIN_CONFIDENCE:
        return None

    # ======================
    # Dynamic expiry
    # ======================

    if forced_expiry:

        expiry = forced_expiry

    else:

        if confidence >= 85:
            expiry = 1
        else:
            expiry = 2

    return {
        "symbol": symbol,
        "direction": direction,
        "confidence": confidence,
        "expiry": expiry,
        "entry_price": latest["close"],
        "reasons": reasons
    }