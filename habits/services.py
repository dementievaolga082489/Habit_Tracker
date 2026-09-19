import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id, message):
    url = f"{settings.TELEGRAM_URL}" f"{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": message,
            },
            timeout=10,
        )
        response.raise_for_status()
        return True

    except requests.RequestException as exc:
        logger.exception(
            "Не удалось отправить сообщение в Telegram: %s",
            exc,
        )
        return False
