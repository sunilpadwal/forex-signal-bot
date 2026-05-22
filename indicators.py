import pandas as pd
from ta.trend import EMAIndicator, MACD, CCIIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

from config import (
    EMA_FAST,
    EMA_SLOW,
    RSI_PERIOD,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
    CCI_PERIOD,
    BB_PERIOD,
    BB_STD,
    WEIGHTS
)


# ==========================================
# Add Indicators
# ==========================================

def add_indicators(df):

    # EMA
    df["ema_fast"] = EMAIndicator(
        close=df["close"],
        window=EMA_FAST
    ).ema_indicator()

    df["ema_slow"] = EMAIndicator(
        close=df["close"],
        window=EMA_SLOW
    ).ema_indicator()

    # MACD
    macd = MACD(
        close=df["close"],
        window_fast=MACD_FAST,
        window_slow=MACD_SLOW,
        window_sign=MACD_SIGNAL
    )

    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_hist"] = macd.macd_diff()

    # RSI
    df["rsi"] = RSIIndicator(
        close=df["close"],
        window=RSI_PERIOD
    ).rsi()

    # CCI
    df["cci"] = CCIIndicator(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=CCI_PERIOD
    ).cci()

    # Bollinger Bands
    bb = BollingerBands(
        close=df["close"],
        window=BB_PERIOD,
        window_dev=BB_STD
    )

    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()
    df["bb_mid"] = bb.bollinger_mavg()

    return df


# ==========================================
# Price Action
# ==========================================

def detect_price_action(df):

    bullish = False
    bearish = False

    last = df.iloc[-1]
    prev = df.iloc[-2]

    candle_body = abs(
        last["close"] - last["open"]
    )

    candle_range = (
        last["high"] - last["low"]
    )

    body_strength = (
        candle_body / candle_range
        if candle_range > 0
        else 0
    )

    # Bullish engulfing
    if (
        prev["close"] < prev["open"]
        and last["close"] > last["open"]
        and last["close"] > prev["open"]
    ):
        bullish = True

    # Bearish engulfing
    if (
        prev["close"] > prev["open"]
        and last["close"] < last["open"]
        and last["close"] < prev["open"]
    ):
        bearish = True

    # Strong momentum candle
    if body_strength > 0.60:

        if last["close"] > last["open"]:
            bullish = True

        else:
            bearish = True

    return bullish, bearish


# ==========================================
# Signal Engine
# ==========================================

def calculate_signal(df):

    latest = df.iloc[-1]

    buy_score = 0
    sell_score = 0

    reasons_buy = []
    reasons_sell = []

    # ======================================
    # EMA Trend
    # ======================================

    if latest["ema_fast"] > latest["ema_slow"]:

        buy_score += WEIGHTS["ema"]
        reasons_buy.append(
            "EMA bullish trend"
        )

    else:

        sell_score += WEIGHTS["ema"]
        reasons_sell.append(
            "EMA bearish trend"
        )

    # ======================================
    # MACD
    # ======================================

    if latest["macd_hist"] > 0:

        buy_score += WEIGHTS["macd"]
        reasons_buy.append(
            "MACD bullish"
        )

    else:

        sell_score += WEIGHTS["macd"]
        reasons_sell.append(
            "MACD bearish"
        )

    # ======================================
    # RSI
    # ======================================

    if latest["rsi"] < 35:

        buy_score += WEIGHTS["rsi"]
        reasons_buy.append(
            "RSI oversold"
        )

    elif latest["rsi"] > 65:

        sell_score += WEIGHTS["rsi"]
        reasons_sell.append(
            "RSI overbought"
        )

    # ======================================
    # CCI
    # ======================================

    if latest["cci"] < -100:

        buy_score += WEIGHTS["cci"]
        reasons_buy.append(
            "CCI oversold"
        )

    elif latest["cci"] > 100:

        sell_score += WEIGHTS["cci"]
        reasons_sell.append(
            "CCI overbought"
        )

    # ======================================
    # Bollinger
    # ======================================

    if latest["close"] <= latest["bb_low"]:

        buy_score += WEIGHTS[
            "bollinger"
        ]

        reasons_buy.append(
            "Lower BB touch"
        )

    elif latest["close"] >= latest["bb_high"]:

        sell_score += WEIGHTS[
            "bollinger"
        ]

        reasons_sell.append(
            "Upper BB touch"
        )

    # ======================================
    # Price Action
    # ======================================

    bullish, bearish = (
        detect_price_action(df)
    )

    if bullish:

        buy_score += WEIGHTS[
            "price_action"
        ]

        buy_score += WEIGHTS[
            "candle_bonus"
        ]

        reasons_buy.append(
            "Bullish momentum"
        )

    if bearish:

        sell_score += WEIGHTS[
            "price_action"
        ]

        sell_score += WEIGHTS[
            "candle_bonus"
        ]

        reasons_sell.append(
            "Bearish momentum"
        )

    # ======================================
    # Final Decision
    # ======================================

    if buy_score >= sell_score:

        return {
            "direction": "BUY",
            "confidence": int(
                buy_score
            ),
            "reasons": reasons_buy
        }

    return {
        "direction": "SELL",
        "confidence": int(
            sell_score
        ),
        "reasons": reasons_sell
    }