import pandas as pd
import ta


def add_indicators(df):

    # EMA
    df["ema_fast"] = ta.trend.EMAIndicator(
        close=df["close"],
        window=9
    ).ema_indicator()

    df["ema_slow"] = ta.trend.EMAIndicator(
        close=df["close"],
        window=21
    ).ema_indicator()

    # MACD
    macd = ta.trend.MACD(df["close"])

    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    # CCI
    df["cci"] = ta.trend.CCIIndicator(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=20
    ).cci()

    # Bollinger
    bb = ta.volatility.BollingerBands(
        close=df["close"],
        window=20,
        window_dev=2
    )

    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()
    df["bb_middle"] = bb.bollinger_mavg()

    return df


# ==================================
# Candle Patterns
# ==================================

def bullish_engulfing(df):

    if len(df) < 2:
        return False

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    return (
        prev["close"] < prev["open"]
        and curr["close"] > curr["open"]
        and curr["close"] > prev["open"]
        and curr["open"] < prev["close"]
    )


def bearish_engulfing(df):

    if len(df) < 2:
        return False

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    return (
        prev["close"] > prev["open"]
        and curr["close"] < curr["open"]
        and curr["open"] > prev["close"]
        and curr["close"] < prev["open"]
    )


# ==================================
# Price Action Breakout
# ==================================

def bullish_breakout(df):

    recent_high = df["high"].tail(10).max()
    current_close = df.iloc[-1]["close"]

    return current_close > recent_high


def bearish_breakout(df):

    recent_low = df["low"].tail(10).min()
    current_close = df.iloc[-1]["close"]

    return current_close < recent_low