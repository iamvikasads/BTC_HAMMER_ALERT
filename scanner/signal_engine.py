from scanner.candle_detector import (
    detect_75_percent_hammer,
)

from scanner.swing_detector import (
    get_previous_swing_high,
    get_previous_swing_low,
)

from scanner.liquidity_detector import (
    detect_high_liquidity_sweep,
    detect_low_liquidity_sweep,
)


# ============================================================
# CONFIGURATION
# ============================================================

# Maximum number of candles after a sweep in which
# we will accept a confirmation hammer.
MAX_HAMMER_WAIT = 3


# ============================================================
# LIQUIDITY + HAMMER FILTERS
# ============================================================

# Dominant wick required for the confirmation hammer.
LIQUIDITY_HAMMER_WICK_PERCENT = 65


# Confirmation hammer must be at least
# 1.3 times the average range of previous candles.
LIQUIDITY_HAMMER_RANGE_MULTIPLIER = 1.3


# Number of previous candles used to calculate
# the normal average candle range.
LIQUIDITY_HAMMER_LOOKBACK = 5


# ============================================================
# MARKET CONTEXT
# ============================================================

def has_bullish_context(candles, current_index):
    """
    Check for bearish pressure before a bullish hammer.
    """

    if current_index < 3:
        return False

    candle_3 = candles[current_index - 3]
    candle_2 = candles[current_index - 2]
    candle_1 = candles[current_index - 1]

    close_3 = float(candle_3["close"])
    close_2 = float(candle_2["close"])
    close_1 = float(candle_1["close"])

    return (
        close_3 > close_2
        or close_2 > close_1
    )


def has_bearish_context(candles, current_index):
    """
    Check for bullish pressure before a bearish hammer.
    """

    if current_index < 3:
        return False

    candle_3 = candles[current_index - 3]
    candle_2 = candles[current_index - 2]
    candle_1 = candles[current_index - 1]

    close_3 = float(candle_3["close"])
    close_2 = float(candle_2["close"])
    close_1 = float(candle_1["close"])

    return (
        close_3 < close_2
        or close_2 < close_1
    )


# ============================================================
# STRONG LIQUIDITY HAMMER FILTER
# ============================================================

def is_strong_liquidity_hammer(
    candles,
    current_index,
    hammer,
):
    """
    Extra filter for Liquidity Sweep + Hammer.

    Requirements:

    1. Dominant wick >= 65%.

    2. Current candle range >= 1.3x
       average range of previous 5 candles.

    This filter applies ONLY to the
    liquidity sweep + hammer setups.

    It does NOT affect the standalone
    HAMMER_80 setup.
    """

    if not hammer:
        return False

    if current_index < LIQUIDITY_HAMMER_LOOKBACK:
        return False

    # --------------------------------------------------------
    # WICK FILTER
    # --------------------------------------------------------

    wick_percent = float(
        hammer.get(
            "wick_percent",
            0,
        )
    )

    if wick_percent < LIQUIDITY_HAMMER_WICK_PERCENT:
        return False

    # --------------------------------------------------------
    # CURRENT CANDLE RANGE
    # --------------------------------------------------------

    current_candle = candles[current_index]

    current_high = float(
        current_candle["high"]
    )

    current_low = float(
        current_candle["low"]
    )

    current_range = (
        current_high - current_low
    )

    if current_range <= 0:
        return False

    # --------------------------------------------------------
    # PREVIOUS 5 CANDLE AVERAGE RANGE
    # --------------------------------------------------------

    previous_ranges = []

    start_index = (
        current_index
        - LIQUIDITY_HAMMER_LOOKBACK
    )

    for i in range(
        start_index,
        current_index,
    ):

        high = float(
            candles[i]["high"]
        )

        low = float(
            candles[i]["low"]
        )

        candle_range = high - low

        if candle_range > 0:

            previous_ranges.append(
                candle_range
            )

    if not previous_ranges:
        return False

    average_range = (
        sum(previous_ranges)
        / len(previous_ranges)
    )

    # --------------------------------------------------------
    # BIG CANDLE FILTER
    # --------------------------------------------------------

    minimum_required_range = (
        average_range
        * LIQUIDITY_HAMMER_RANGE_MULTIPLIER
    )

    if current_range < minimum_required_range:
        return False

    return True


# ============================================================
# HAMMER
# ============================================================

def get_hammer_signal(
    candles,
    current_index,
):
    """
    Detect a valid >80% wick hammer.

    The candle detector currently keeps the old
    function name detect_75_percent_hammer(), but
    internally it now requires >80%.
    """

    if current_index < 3:
        return None

    candle = candles[current_index]

    hammer = detect_75_percent_hammer(
        candle
    )

    if not hammer:
        return None

    # --------------------------------------------------------
    # BULLISH HAMMER
    # --------------------------------------------------------

    if hammer["direction"] == "BULLISH":

        if not has_bullish_context(
            candles,
            current_index,
        ):
            return None

        return {
            "setup": hammer["setup"],
            "direction": "BULLISH",
            "price": candle["close"],
            "wick_percent": (
                hammer["dominant_wick_percent"]
            ),
            "opposite_wick_percent": (
                hammer["opposite_wick_percent"]
            ),
            "candle_time": (
                candle["close_time"]
            ),
            "context": "BEARISH_PRESSURE",
        }

    # --------------------------------------------------------
    # BEARISH HAMMER / REVERSE HAMMER
    # --------------------------------------------------------

    if not has_bearish_context(
        candles,
        current_index,
    ):
        return None

    return {
        "setup": hammer["setup"],
        "direction": "BEARISH",
        "price": candle["close"],
        "wick_percent": (
            hammer["dominant_wick_percent"]
        ),
        "opposite_wick_percent": (
            hammer["opposite_wick_percent"]
        ),
        "candle_time": (
            candle["close_time"]
        ),
        "context": "BULLISH_PRESSURE",
    }


# ============================================================
# CURRENT LIQUIDITY SWEEP
# ============================================================

def get_current_liquidity_sweeps(
    candles,
    current_index,
    swing_left=3,
    swing_right=3,
):
    """
    Detect liquidity sweeps occurring on the
    current candle.
    """

    if current_index < 20:
        return []

    candle = candles[current_index]

    signals = []

    # --------------------------------------------------------
    # PREVIOUS CONFIRMED HIGH
    # --------------------------------------------------------

    previous_high = get_previous_swing_high(
        candles,
        current_index,
        left=swing_left,
        right=swing_right,
    )

    # --------------------------------------------------------
    # PREVIOUS CONFIRMED LOW
    # --------------------------------------------------------

    previous_low = get_previous_swing_low(
        candles,
        current_index,
        left=swing_left,
        right=swing_right,
    )

    # ========================================================
    # BEARISH SWEEP
    # ========================================================

    if previous_high:

        bearish = detect_high_liquidity_sweep(
            candle,
            previous_high,
        )

        if bearish:

            signals.append(
                {
                    **bearish,

                    "price": candle["close"],

                    "candle_time": (
                        candle["close_time"]
                    ),

                    "swing_time": (
                        previous_high["time"]
                    ),
                }
            )

    # ========================================================
    # BULLISH SWEEP
    # ========================================================

    if previous_low:

        bullish = detect_low_liquidity_sweep(
            candle,
            previous_low,
        )

        if bullish:

            signals.append(
                {
                    **bullish,

                    "price": candle["close"],

                    "candle_time": (
                        candle["close_time"]
                    ),

                    "swing_time": (
                        previous_low["time"]
                    ),
                }
            )

    return signals


# ============================================================
# FIND RECENT PREVIOUS SWEEP
# ============================================================

def find_recent_bullish_sweep(
    candles,
    current_index,
    swing_left=3,
    swing_right=3,
):
    """
    Look backwards up to MAX_HAMMER_WAIT candles
    for a bullish liquidity sweep.

    Used when the sweep happened first and the
    hammer forms later.
    """

    start_index = max(
        20,
        current_index - MAX_HAMMER_WAIT,
    )

    for sweep_index in range(
        current_index - 1,
        start_index - 1,
        -1,
    ):

        sweeps = get_current_liquidity_sweeps(
            candles,
            sweep_index,
            swing_left=swing_left,
            swing_right=swing_right,
        )

        for sweep in sweeps:

            if sweep.get("direction") == "BULLISH":

                return sweep

            if sweep.get("setup") == "LIQUIDITY_SWEEP_LONG":

                return sweep

    return None


def find_recent_bearish_sweep(
    candles,
    current_index,
    swing_left=3,
    swing_right=3,
):
    """
    Look backwards up to MAX_HAMMER_WAIT candles
    for a bearish liquidity sweep.
    """

    start_index = max(
        20,
        current_index - MAX_HAMMER_WAIT,
    )

    for sweep_index in range(
        current_index - 1,
        start_index - 1,
        -1,
    ):

        sweeps = get_current_liquidity_sweeps(
            candles,
            sweep_index,
            swing_left=swing_left,
            swing_right=swing_right,
        )

        for sweep in sweeps:

            if sweep.get("direction") == "BEARISH":

                return sweep

            if sweep.get("setup") == "LIQUIDITY_SWEEP_SHORT":

                return sweep

    return None


# ============================================================
# SAME-CANDLE SWEEP + HAMMER
# ============================================================

def combine_same_candle_sweep(
    sweep,
    hammer,
):
    """
    Combine a liquidity sweep and hammer when
    BOTH happen on the SAME candle.
    """

    if not sweep or not hammer:
        return None

    # --------------------------------------------------------
    # BULLISH
    # --------------------------------------------------------

    if (
        sweep.get("direction") == "BULLISH"
        and hammer.get("direction") == "BULLISH"
    ):

        return {
            "setup": "LIQUIDITY_SWEEP_HAMMER_LONG",

            "direction": "BULLISH",

            "price": hammer["price"],

            "wick_percent": (
                hammer["wick_percent"]
            ),

            "opposite_wick_percent": (
                hammer["opposite_wick_percent"]
            ),

            "liquidity_level": (
                sweep.get("liquidity_level")
            ),

            "sweep_price": (
                sweep.get("sweep_price")
            ),

            "candle_time": (
                hammer["candle_time"]
            ),

            "swing_time": (
                sweep.get("swing_time")
            ),

            "confirmation": "SAME_CANDLE",
        }

    # --------------------------------------------------------
    # BEARISH
    # --------------------------------------------------------

    if (
        sweep.get("direction") == "BEARISH"
        and hammer.get("direction") == "BEARISH"
    ):

        return {
            "setup": "LIQUIDITY_SWEEP_HAMMER_SHORT",

            "direction": "BEARISH",

            "price": hammer["price"],

            "wick_percent": (
                hammer["wick_percent"]
            ),

            "opposite_wick_percent": (
                hammer["opposite_wick_percent"]
            ),

            "liquidity_level": (
                sweep.get("liquidity_level")
            ),

            "sweep_price": (
                sweep.get("sweep_price")
            ),

            "candle_time": (
                hammer["candle_time"]
            ),

            "swing_time": (
                sweep.get("swing_time")
            ),

            "confirmation": "SAME_CANDLE",
        }

    return None


# ============================================================
# DELAYED SWEEP + HAMMER
# ============================================================

def build_delayed_bullish_signal(
    candles,
    current_index,
    hammer,
    swing_left=3,
    swing_right=3,
):
    """
    Sweep happens first.
    Hammer happens later.
    """

    if not hammer:
        return None

    if hammer["direction"] != "BULLISH":
        return None

    sweep = find_recent_bullish_sweep(
        candles,
        current_index,
        swing_left=swing_left,
        swing_right=swing_right,
    )

    if not sweep:
        return None

    return {
        "setup": "LIQUIDITY_SWEEP_THEN_HAMMER_LONG",

        "direction": "BULLISH",

        "price": hammer["price"],

        "wick_percent": (
            hammer["wick_percent"]
        ),

        "opposite_wick_percent": (
            hammer["opposite_wick_percent"]
        ),

        "liquidity_level": (
            sweep.get("liquidity_level")
        ),

        "sweep_price": (
            sweep.get("sweep_price")
        ),

        "candle_time": (
            hammer["candle_time"]
        ),

        "swing_time": (
            sweep.get("swing_time")
        ),

        "confirmation": "LATER_HAMMER",

        "sweep_candle_time": (
            sweep.get("candle_time")
        ),
    }


def build_delayed_bearish_signal(
    candles,
    current_index,
    hammer,
    swing_left=3,
    swing_right=3,
):
    """
    Sweep happens first.
    Hammer happens later.
    """

    if not hammer:
        return None

    if hammer["direction"] != "BEARISH":
        return None

    sweep = find_recent_bearish_sweep(
        candles,
        current_index,
        swing_left=swing_left,
        swing_right=swing_right,
    )

    if not sweep:
        return None

    return {
        "setup": "LIQUIDITY_SWEEP_THEN_HAMMER_SHORT",

        "direction": "BEARISH",

        "price": hammer["price"],

        "wick_percent": (
            hammer["wick_percent"]
        ),

        "opposite_wick_percent": (
            hammer["opposite_wick_percent"]
        ),

        "liquidity_level": (
            sweep.get("liquidity_level")
        ),

        "sweep_price": (
            sweep.get("sweep_price")
        ),

        "candle_time": (
            hammer["candle_time"]
        ),

        "swing_time": (
            sweep.get("swing_time")
        ),

        "confirmation": "LATER_HAMMER",

        "sweep_candle_time": (
            sweep.get("candle_time")
        ),
    }


# ============================================================
# MAIN HISTORICAL ANALYZER
# ============================================================

def analyze_candle(
    candles,
    current_index,
    swing_left=3,
    swing_right=3,
):
    """
    Analyze ONE closed candle.

    Supported setups:

    1. HAMMER_80_LONG
    2. HAMMER_80_SHORT
    3. LIQUIDITY_SWEEP_LONG
    4. LIQUIDITY_SWEEP_SHORT
    5. LIQUIDITY_SWEEP_HAMMER_LONG
    6. LIQUIDITY_SWEEP_HAMMER_SHORT
    7. LIQUIDITY_SWEEP_THEN_HAMMER_LONG
    8. LIQUIDITY_SWEEP_THEN_HAMMER_SHORT
    """

    if not candles:
        return []

    if current_index < 20:
        return []

    if current_index >= len(candles):
        return []

    signals = []

    # ========================================================
    # HAMMER
    # ========================================================

    hammer = get_hammer_signal(
        candles,
        current_index,
    )

    # ========================================================
    # CURRENT SWEEP
    # ========================================================

    current_sweeps = get_current_liquidity_sweeps(
        candles,
        current_index,
        swing_left=swing_left,
        swing_right=swing_right,
    )

    # ========================================================
    # STRONG LIQUIDITY + HAMMER FILTER
    # ========================================================

    strong_liquidity_hammer = False

    if hammer:

        strong_liquidity_hammer = (
            is_strong_liquidity_hammer(
                candles,
                current_index,
                hammer,
            )
        )

    # ========================================================
    # SAME CANDLE:
    # SWEEP + HAMMER
    # ========================================================

    same_candle_signal_found = False

    if (
        hammer
        and current_sweeps
        and strong_liquidity_hammer
    ):

        for sweep in current_sweeps:

            combined = combine_same_candle_sweep(
                sweep,
                hammer,
            )

            if combined:

                signals.append(
                    combined
                )

                same_candle_signal_found = True

    # ========================================================
    # NORMAL STANDALONE HAMMER
    # ========================================================

    if hammer and not same_candle_signal_found:

        signals.append(
            hammer
        )

    # ========================================================
    # DELAYED:
    # SWEEP FIRST → HAMMER LATER
    # ========================================================

    if (
        hammer
        and not same_candle_signal_found
        and strong_liquidity_hammer
    ):

        delayed_long = (
            build_delayed_bullish_signal(
                candles,
                current_index,
                hammer,
                swing_left=swing_left,
                swing_right=swing_right,
            )
        )

        if delayed_long:

            signals.append(
                delayed_long
            )

        delayed_short = (
            build_delayed_bearish_signal(
                candles,
                current_index,
                hammer,
                swing_left=swing_left,
                swing_right=swing_right,
            )
        )

        if delayed_short:

            signals.append(
                delayed_short
            )

    # ========================================================
    # STANDALONE LIQUIDITY SWEEP
    # ========================================================

    if current_sweeps:

        for sweep in current_sweeps:

            # If same candle already became a combined
            # sweep + hammer setup, don't duplicate the
            # plain liquidity signal.
            if same_candle_signal_found:
                continue

            signals.append(
                sweep
            )

    return signals


# ============================================================
# LIVE ANALYZER
# ============================================================

def analyze_candles(
    candles,
    swing_left=3,
    swing_right=3,
):
    """
    Analyze the latest closed candle.
    """

    if len(candles) < 20:
        return []

    current_index = (
        len(candles) - 1
    )

    return analyze_candle(
        candles,
        current_index,
        swing_left=swing_left,
        swing_right=swing_right,
    )