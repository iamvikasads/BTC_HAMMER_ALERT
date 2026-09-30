import requests

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)


def send_telegram_message(message):
    """
    Send a text message to Telegram.
    """

    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram bot token is missing.")
        return False

    if not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram chat ID is missing.")
        return False

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
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

        return True

    except requests.RequestException as error:

        print(
            f"⚠️ Telegram message failed: {error}"
        )

        return False