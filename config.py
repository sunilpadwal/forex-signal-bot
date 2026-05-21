import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

# Free API safe settings
SCAN_LIMIT = 10

# Confidence threshold
MIN_CONFIDENCE = 75

# Entry buffer
ENTRY_BUFFER_SECONDS = 20

# Timeframes
TIMEFRAME_1M = "1min"
TIMEFRAME_2M = "2min"