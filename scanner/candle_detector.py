def calculate_candle(candle):
    """
    Calculate OHLC candle structure and wick percentages.
    """

    open_price = float(candle["open"])
    high = float(candle["high"])
    low = float(candle["low"])
    close = float(candle["close"])

    candle_range = high - low

    if candle_range <= 0:
        return None

    body = abs(close - open_price)

    upper_wick = high - max(open_price, close)

    lower_wick = min(open_price, close) - low

    upper_wick_percent = (
        upper_wick / candle_range
    ) * 100

    lower_wick_percent = (
        lower_wick / candle_range
    ) * 100

    if lower_wick_percent > upper_wick_percent:

        direction = "BULLISH"

        dominant_wick = lower_wick

        dominant_wick_percent = (
            lower_wick_percent
        )

        opposite_wick_percent = (
            upper_wick_percent
        )

    else:

        direction = "BEARISH"

        dominant_wick = upper_wick

        dominant_wick_percent = (
            upper_wick_percent
        )

        opposite_wick_percent = (
            lower_wick_percent
        )

    return {
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,

        "range": candle_range,
        "body": body,

        "upper_wick": upper_wick,
        "lower_wick": lower_wick,

        "upper_wick_percent": (
            upper_wick_percent
        ),

        "lower_wick_percent": (
            lower_wick_percent
        ),

        "dominant_wick": dominant_wick,

        "dominant_wick_percent": (
            dominant_wick_percent
        ),

        "opposite_wick_percent": (
            opposite_wick_percent
        ),

        "direction": direction,
    }


def detect_75_percent_hammer(candle):
    """
    Hammer detection.

    IMPORTANT:
    The function name is kept unchanged so
    existing imports continue working.

    New requirement:
        Dominant wick MUST be MORE THAN 80%
        of the complete candle range.
    """

    result = calculate_candle(candle)

    if result is None:
        return None

    # ==================================================
    # 80% WICK REQUIREMENT
    # ==================================================

    if result["dominant_wick_percent"] <= 80:
        return None

    # ==================================================
    # SETUP
    # ==================================================

    if result["direction"] == "BULLISH":

        result["setup"] = "HAMMER_80_LONG"

    else:

        result["setup"] = "HAMMER_80_SHORT"

    return result