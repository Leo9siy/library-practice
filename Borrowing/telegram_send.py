import os

import dotenv
import requests


dotenv.load_dotenv()


def send_telegram_message(text):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Не удалось отправить сообщение в Telegram: {e}")
