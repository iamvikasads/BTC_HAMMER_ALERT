import time
from datetime import datetime, timedelta


SCAN_DELAY_SECONDS = 2


def get_next_scan_time(delay_seconds=SCAN_DELAY_SECONDS):
    """
    Calculate the next 5-minute candle-close scan time.

    Examples:
        10:00:02
        10:05:02
        10:10:02
        10:15:02
        ...
    """

    now = datetime.now()

    # Find the next 5-minute boundary.
    minutes_to_add = 5 - (now.minute % 5)

    next_scan = now.replace(
        second=0,
        microsecond=0,
    ) + timedelta(
        minutes=minutes_to_add
    )

    next_scan += timedelta(
        seconds=delay_seconds
    )

    # Safety check.
    if next_scan <= now:
        next_scan += timedelta(minutes=5)

    return next_scan


def seconds_until_next_scan(
    delay_seconds=SCAN_DELAY_SECONDS,
):
    """
    Return seconds remaining until
    the next scheduled scan.
    """

    now = datetime.now()

    next_scan = get_next_scan_time(
        delay_seconds
    )

    seconds = (
        next_scan - now
    ).total_seconds()

    return max(0, seconds)


def wait_until_next_scan(
    delay_seconds=SCAN_DELAY_SECONDS,
):
    """
    Wait until the next synchronized
    5-minute candle close.
    """

    next_scan = get_next_scan_time(
        delay_seconds
    )

    now = datetime.now()

    seconds = (
        next_scan - now
    ).total_seconds()

    seconds = max(0, seconds)

    print()
    print(
        f"Current time : "
        f"{now.strftime('%H:%M:%S')}"
    )

    print(
        f"Next scan    : "
        f"{next_scan.strftime('%H:%M:%S')}"
    )

    print(
        f"Sleeping     : "
        f"{seconds:.1f} seconds"
    )

    time.sleep(seconds)

    print()
    print(
        f"🚨 SCAN TIME: "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )