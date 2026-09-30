import os

from dotenv import load_dotenv


load_dotenv()


BINANCE_BASE_URL = os.getenv(
    "BINANCE_BASE_URL",
    "https://fapi.binance.com"
)


SYMBOL = os.getenv(
    "SYMBOL",
    "BTCUSDT"
)


INTERVAL = os.getenv(
    "INTERVAL",
    "5m"
)


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
)


TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    ""
)


HAMMER_WICK_PERCENT = float(
    os.getenv(
        "HAMMER_WICK_PERCENT",
        "75"
    )
)


LIQUIDITY_WICK_PERCENT = float(
    os.getenv(
        "LIQUIDITY_WICK_PERCENT",
        "50"
    )
)


SWING_LEFT = int(
    os.getenv(
        "SWING_LEFT",
        "3"
    )
)


SWING_RIGHT = int(
    os.getenv(
        "SWING_RIGHT",
        "3"
    )
)


POLL_SECONDS = int(
    os.getenv(
        "POLL_SECONDS",
        "5"
    )
)