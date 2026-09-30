def is_swing_high(candles, index, left=3, right=3):
    """
    Confirmed swing high.

    The candidate candle must have a high greater than
    all candles on the left and at least as high as the
    candles on the right.
    """

    if index < left:
        return False

    if index + right >= len(candles):
        return False

    current_high = candles[index]["high"]

    for i in range(index - left, index):
        if candles[i]["high"] >= current_high:
            return False

    for i in range(index + 1, index + right + 1):
        if candles[i]["high"] > current_high:
            return False

    return True


def is_swing_low(candles, index, left=3, right=3):
    """
    Confirmed swing low.
    """

    if index < left:
        return False

    if index + right >= len(candles):
        return False

    current_low = candles[index]["low"]

    for i in range(index - left, index):
        if candles[i]["low"] <= current_low:
            return False

    for i in range(index + 1, index + right + 1):
        if candles[i]["low"] < current_low:
            return False

    return True


def get_confirmed_swings(
    candles,
    left=3,
    right=3,
):
    """
    Return confirmed swing highs and lows
    in chronological order.
    """

    swing_highs = []
    swing_lows = []

    last_possible_index = len(candles) - right

    for index in range(
        left,
        last_possible_index,
    ):

        candle = candles[index]

        if is_swing_high(
            candles,
            index,
            left,
            right,
        ):
            swing_highs.append({
                "index": index,
                "price": candle["high"],
                "time": candle.get("close_time"),
            })

        if is_swing_low(
            candles,
            index,
            left,
            right,
        ):
            swing_lows.append({
                "index": index,
                "price": candle["low"],
                "time": candle.get("close_time"),
            })

    return swing_highs, swing_lows


def get_previous_swing_high(
    candles,
    current_index,
    left=3,
    right=3,
):
    """
    Find the most recent CONFIRMED swing high
    before the current candle.

    The swing itself must have enough right-side
    candles to be confirmed.
    """

    if current_index <= 0:
        return None

    history = candles[:current_index]

    swing_highs, _ = get_confirmed_swings(
        history,
        left=left,
        right=right,
    )

    if not swing_highs:
        return None

    return swing_highs[-1]


def get_previous_swing_low(
    candles,
    current_index,
    left=3,
    right=3,
):
    """
    Find the most recent CONFIRMED swing low
    before the current candle.
    """

    if current_index <= 0:
        return None

    history = candles[:current_index]

    _, swing_lows = get_confirmed_swings(
        history,
        left=left,
        right=right,
    )

    if not swing_lows:
        return None

    return swing_lows[-1]