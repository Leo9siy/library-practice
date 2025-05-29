import requests


def send_telegram_message(text):
    token = '7668162734:AAEVXIRp84sUuz3RzTbgcCdIjLQ_U3_yq6U'
    chat_id = '7311564158'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id, 'text': text
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Не удалось отправить сообщение в Telegram: {e}")