import os
import time
import requests
from datetime import datetime

from scanner.market_data import get_closed_candles
from scanner.signal_engine import analyze_candles
from scanner.scheduler import wait_until_next_scan

from config import (
    SYMBOL,
    INTERVAL,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)


# ============================================================
# BOT CONFIGURATION
# ============================================================

SWING_LEFT = 3
SWING_RIGHT = 3

CANDLE_LIMIT = 200

# Telegram heartbeat interval
# 12 hours = 12 * 60 * 60 seconds
HEARTBEAT_INTERVAL = 12 * 60 * 60


# ============================================================
# SCREEN
# ============================================================

def clear_screen():
    """Clear the terminal screen before each scan."""
    os.system("cls" if os.name == "nt" else "clear")


# ============================================================
# DUPLICATE PROTECTION
# ============================================================

last_processed_candle = None


# ============================================================
# TELEGRAM
# ============================================================

def send_telegram_message(message):
    """
    Send a message to Telegram.

    If Telegram configuration is missing,
    the scanner continues normally.
    """

    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram bot token not configured.")
        return

    if not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram chat ID not configured.")
        return

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()

        print("📨 Telegram alert sent.")

    except Exception as error:

        print(
            f"⚠️ Telegram error: "
            f"{type(error).__name__}: {error}"
        )


# ============================================================
# TELEGRAM SIGNAL FORMAT
# ============================================================

def format_telegram_signal(signal):
    """
    Create the one-line Telegram alert.

    Example:

    🚨 BTCUSDT 5M | HAMMER_80_LONG | 🟢 LONG
    """

    setup = signal.get(
        "setup",
        "UNKNOWN",
    )

    direction = signal.get(
        "direction",
        "",
    )

    if direction.upper() == "BULLISH":

        direction_text = "🟢 LONG"

    elif direction.upper() == "BEARISH":

        direction_text = "🔴 SHORT"

    else:

        direction_text = direction

    return (
        f"🚨 {SYMBOL} "
        f"{INTERVAL.upper()} | "
        f"{setup} | "
        f"{direction_text}"
    )


# ============================================================
# TIME FORMATTER
# ============================================================

def format_time(timestamp):
    """
    Convert Binance millisecond timestamp
    into readable local time.
    """

    dt = datetime.fromtimestamp(
        timestamp / 1000
    )

    return dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ============================================================
# SINGLE MARKET SCAN
# ============================================================

def run_scan():

    global last_processed_candle

    print()
    print("=" * 60)
    print(f"{SYMBOL} {INTERVAL.upper()} SCAN")
    print("=" * 60)

    # --------------------------------------------------------
    # GET CLOSED CANDLES
    # --------------------------------------------------------

    candles = get_closed_candles(
        CANDLE_LIMIT
    )

    if not candles:

        print(
            "❌ No closed candle data received."
        )

        return

    # --------------------------------------------------------
    # LATEST CLOSED CANDLE
    # --------------------------------------------------------

    latest_candle = candles[-1]

    open_time = latest_candle[
        "open_time"
    ]

    close_time = latest_candle[
        "close_time"
    ]

    # --------------------------------------------------------
    # CANDLE INFORMATION
    # --------------------------------------------------------

    print(
        f"Closed candles : "
        f"{len(candles)}"
    )

    print(
        f"Open time      : "
        f"{format_time(open_time)}"
    )

    print(
        f"Close time     : "
        f"{format_time(close_time)}"
    )

    print(
        f"Open           : "
        f"{latest_candle['open']}"
    )

    print(
        f"High           : "
        f"{latest_candle['high']}"
    )

    print(
        f"Low            : "
        f"{latest_candle['low']}"
    )

    print(
        f"Close          : "
        f"{latest_candle['close']}"
    )

    # --------------------------------------------------------
    # DUPLICATE PROTECTION
    # --------------------------------------------------------

    if close_time == last_processed_candle:

        print()
        print(
            "⚠️ Candle already processed."
        )

        return

    # --------------------------------------------------------
    # SIGNAL ENGINE
    # --------------------------------------------------------

    signals = analyze_candles(
        candles,
        swing_left=SWING_LEFT,
        swing_right=SWING_RIGHT,
    )

    # --------------------------------------------------------
    # MARK THIS CANDLE AS PROCESSED
    # --------------------------------------------------------

    last_processed_candle = close_time

    # --------------------------------------------------------
    # SIGNAL RESULTS
    # --------------------------------------------------------

    print()
    print("SIGNALS")
    print("-" * 40)

    if not signals:

        print(
            "No setup detected."
        )

        return

    # --------------------------------------------------------
    # DISPLAY + TELEGRAM
    # --------------------------------------------------------

    for signal in signals:

        print()
        print(
            "🚨 SETUP DETECTED"
        )

        # ----------------------------------------------------
        # SETUP
        # ----------------------------------------------------

        print(
            f"Setup     : "
            f"{signal['setup']}"
        )

        # ----------------------------------------------------
        # DIRECTION
        # ----------------------------------------------------

        print(
            f"Direction : "
            f"{signal['direction']}"
        )

        # ----------------------------------------------------
        # PRICE
        # ----------------------------------------------------

        print(
            f"Price     : "
            f"{signal['price']}"
        )

        # ----------------------------------------------------
        # WICK PERCENTAGE
        # ----------------------------------------------------

        if "wick_percent" in signal:

            print(
                f"Wick      : "
                f"{signal['wick_percent']:.2f}%"
            )

        # ----------------------------------------------------
        # LIQUIDITY LEVEL
        # ----------------------------------------------------

        if "liquidity_level" in signal:

            print(
                f"Liquidity : "
                f"{signal['liquidity_level']}"
            )

        # ----------------------------------------------------
        # SWEEP PRICE
        # ----------------------------------------------------

        if "sweep_price" in signal:

            print(
                f"Sweep     : "
                f"{signal['sweep_price']}"
            )

        # ----------------------------------------------------
        # SWING TIME
        # ----------------------------------------------------

        if "swing_time" in signal:

            print(
                f"Swing     : "
                f"{format_time(signal['swing_time'])}"
            )

        # ----------------------------------------------------
        # SIGNAL CANDLE TIME
        # ----------------------------------------------------

        if "candle_time" in signal:

            print(
                f"Candle    : "
                f"{format_time(signal['candle_time'])}"
            )

        print(
            "-" * 40
        )

        # ====================================================
        # TELEGRAM ALERT
        # ====================================================

        telegram_message = (
            format_telegram_signal(
                signal
            )
        )

        print(
            f"Telegram  : "
            f"{telegram_message}"
        )

        send_telegram_message(
            telegram_message
        )


# ============================================================
# LIVE SCANNER
# ============================================================

def run_live_scanner():

    print()
    print("=" * 60)
    print("BTC HAMMER ALERT BOT")
    print("=" * 60)

    print(
        f"Symbol    : {SYMBOL}"
    )

    print(
        f"Timeframe : {INTERVAL}"
    )

    print(
        "Schedule  : Every 5 minutes"
    )

    print(
        "Scan      : 00,05,10,15,...55"
    )

    print(
        "Scan delay: 2 seconds"
    )

    print(
        "Heartbeat : Every 12 hours"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # TELEGRAM STARTUP ALERT
    # --------------------------------------------------------

    send_telegram_message(
        f"🤖 {SYMBOL} {INTERVAL.upper()} | "
        f"BOT STARTED | 🟢 ONLINE"
    )

    # --------------------------------------------------------
    # HEARTBEAT TIMER
    # --------------------------------------------------------

    last_heartbeat = time.time()

    while True:

        try:

            # ------------------------------------------------
            # WAIT FOR NEXT 5-MINUTE SCAN
            # ------------------------------------------------

            wait_until_next_scan()

            # ------------------------------------------------
            # CLEAR SCREEN BEFORE EVERY SCAN
            # ------------------------------------------------

            clear_screen()

            # ------------------------------------------------
            # 12-HOUR HEARTBEAT
            # ------------------------------------------------

            current_time = time.time()

            if (
                current_time - last_heartbeat
                >= HEARTBEAT_INTERVAL
            ):

                send_telegram_message(
                    f"💚 {SYMBOL} "
                    f"{INTERVAL.upper()} | "
                    f"BOT ALIVE | 🟢 ONLINE"
                )

                last_heartbeat = current_time

            # ------------------------------------------------
            # RUN MARKET SCAN
            # ------------------------------------------------

            run_scan()

        except KeyboardInterrupt:

            print()
            print(
                "🛑 Scanner stopped by user."
            )

            # ------------------------------------------------
            # MANUAL STOP TELEGRAM ALERT
            # ------------------------------------------------

            send_telegram_message(
                f"🛑 {SYMBOL} "
                f"{INTERVAL.upper()} | "
                f"BOT STOPPED | 🔴 OFFLINE"
            )

            break

        except Exception as error:

            print()
            print(
                "❌ Scanner error:"
            )

            print(
                f"{type(error).__name__}: "
                f"{error}"
            )

            print()
            print(
                "Retrying at next "
                "5-minute cycle..."
            )

            time.sleep(5)


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    run_live_scanner()