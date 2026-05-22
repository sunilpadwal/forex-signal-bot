import os

# ==========================================
# Telegram
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ==========================================
# FCS API
# ==========================================

FCS_API_KEY = os.getenv("FCS_API_KEY")

BASE_URL = "https://api-v4.fcsapi.com"

# ==========================================
# Strategy Settings
# ==========================================

# Confidence threshold
MIN_CONFIDENCE = 70

# Scan every X seconds
SCAN_INTERVAL = 10

# Max pairs to scan
MAX_SCAN_PAIRS = 40

# Next minute entry buffer
ENTRY_BUFFER_SECONDS = 15

# ==========================================
# Indicators
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
# Score weights
# Total = 100
# ==========================================

WEIGHTS = {
    "ema": 20,
    "macd": 20,
    "rsi": 15,
    "cci": 15,
    "bollinger": 10,
    "price_action": 15,
    "candle_bonus": 5
}

# ==========================================
# Pip Calculation
# ==========================================

PIP_MULTIPLIER = 10000

# ==========================================
# Dynamic Expiry
# ==========================================

SUPPORTED_EXPIRIES = [1, 2]