import os

# ==========================================
# Telegram
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ==========================================
# Twelve Data
# ==========================================

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

BASE_URL = "https://api.twelvedata.com"

# ==========================================
# Signal Settings
# ==========================================

# Confidence threshold
MIN_CONFIDENCE = 70

# Scan interval (seconds)
SCAN_INTERVAL = 10

# Best Dynamic Mode
# Auto choose 1m or 2m
ENABLE_DYNAMIC_MODE = True

# Entry buffer before next candle
ENTRY_BUFFER_SECONDS = 15

# Maximum pairs to scan at once
MAX_SCAN_PAIRS = 40

# ==========================================
# Indicator Weights
# Total = 100
# ==========================================

WEIGHTS = {
    "ema_trend": 20,
    "macd": 20,
    "rsi": 15,
    "cci": 15,
    "bollinger": 10,
    "price_action": 15,
    "candle_bonus": 5,
}

# ==========================================
# Indicator Settings
# ==========================================

EMA_FAST = 9
EMA_SLOW = 21

RSI_PERIOD = 14

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

CCI_PERIOD = 20

BB_PERIOD = 20
BB_STD = 2

# ==========================================
# Trade Timing
# ==========================================

DEFAULT_DURATION_1M = 60
DEFAULT_DURATION_2M = 120

# ==========================================
# Result Tracking
# ==========================================

ENABLE_RESULT_TRACKING = True
PIP_MULTIPLIER = 10000