def detect_high_liquidity_sweep(
    candle,
    swing_high,
):
    """
    Bearish liquidity sweep.

    Requirements:
    - High trades above previous swing high.
    - Close returns below the swing high.
    - Upper wick > 50% of candle range.
    """

    open_price = float(candle["open"])
    high = float(candle["high"])
    low = float(candle["low"])
    close = float(candle["close"])

    level = float(swing_high["price"])

    candle_range = high - low

    if candle_range <= 0:
        return None

    if high <= level:
        return None

    if close >= level:
        return None

    upper_wick = high - max(
        open_price,
        close,
    )

    upper_wick_percent = (
        upper_wick / candle_range
    ) * 100

    if upper_wick_percent <= 50:
        return None

    return {
        "setup": "LIQUIDITY_SWEEP_SHORT",
        "direction": "BEARISH",
        "liquidity_type": "SWING_HIGH",
        "liquidity_level": level,
        "sweep_price": high,
        "wick_percent": upper_wick_percent,
    }


def detect_low_liquidity_sweep(
    candle,
    swing_low,
):
    """
    Bullish liquidity sweep.

    Requirements:
    - Low trades below previous swing low.
    - Close returns above the swing low.
    - Lower wick > 50% of candle range.
    """

    open_price = float(candle["open"])
    high = float(candle["high"])
    low = float(candle["low"])
    close = float(candle["close"])

    level = float(swing_low["price"])

    candle_range = high - low

    if candle_range <= 0:
        return None

    if low >= level:
        return None

    if close <= level:
        return None

    lower_wick = min(
        open_price,
        close,
    ) - low

    lower_wick_percent = (
        lower_wick / candle_range
    ) * 100

    if lower_wick_percent <= 50:
        return None

    return {
        "setup": "LIQUIDITY_SWEEP_LONG",
        "direction": "BULLISH",
        "liquidity_type": "SWING_LOW",
        "liquidity_level": level,
        "sweep_price": low,
        "wick_percent": lower_wick_percent,
    }