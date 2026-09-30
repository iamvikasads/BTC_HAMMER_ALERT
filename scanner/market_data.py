import time
import requests

from config import (
    BINANCE_BASE_URL,
    SYMBOL,
    INTERVAL,
)


# ============================================================
# CONNECTION SETTINGS
# ============================================================

REQUEST_TIMEOUT = 10

MAX_RETRIES = 3

RETRY_DELAY = 2


# ============================================================
# BINANCE KLINES
# ============================================================

def get_klines(limit=200):
    """
    Get BTCUSDT Futures candles from Binance.

    If Binance/network connection temporarily fails,
    retry the request several times before giving up.
    """

    url = (
        f"{BINANCE_BASE_URL}"
        f"/fapi/v1/klines"
    )

    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": limit,
    }

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as error:

            last_error = error

            print()
            print(
                f"⚠️ Binance connection failed "
                f"(attempt {attempt}/{MAX_RETRIES})"
            )

            print(
                f"Reason: {error}"
            )

            # Don't sleep after the final attempt.
            if attempt < MAX_RETRIES:

                print(
                    f"Retrying in "
                    f"{RETRY_DELAY} seconds..."
                )

                time.sleep(
                    RETRY_DELAY
                )

    # All retries failed.
    raise ConnectionError(
        "Unable to connect to Binance after "
        f"{MAX_RETRIES} attempts."
    ) from last_error


# ============================================================
# CONVERT BINANCE CANDLE
# ============================================================

def convert_candle(raw_candle):
    """
    Convert Binance kline format into
    our internal candle format.
    """

    return {
        "open_time": raw_candle[0],
        "open": float(raw_candle[1]),
        "high": float(raw_candle[2]),
        "low": float(raw_candle[3]),
        "close": float(raw_candle[4]),
        "volume": float(raw_candle[5]),
        "close_time": raw_candle[6],
    }


# ============================================================
# GET ALL CANDLES
# ============================================================

def get_candles(limit=200):
    """
    Return Binance candles in internal format.
    """

    raw_candles = get_klines(limit)

    candles = []

    for raw_candle in raw_candles:

        candles.append(
            convert_candle(raw_candle)
        )

    return candles


# ============================================================
# GET CLOSED CANDLES
# ============================================================

def get_closed_candles(limit=200):
    """
    Return only candles that have actually closed.

    The candle's Binance close_time is compared
    against the current UTC timestamp.
    """

    candles = get_candles(limit)

    if not candles:
        return []

    current_time_ms = int(
        time.time() * 1000
    )

    closed_candles = []

    for candle in candles:

        if candle["close_time"] < current_time_ms:

            closed_candles.append(
                candle
            )

    return closed_candles