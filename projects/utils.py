import requests
from notify_me import settings


def get_current_balance(login, access_token):
    data = {
        "method": "AccountManagement",
        "param": {
            "Action": "Get",
            "SelectionCriteria": {"Logins": [login.split("@")[0]]},
        },
        "locale": "ru",
        "token": access_token,
    }

    response_data = requests.post(
        f"https://{settings.YANDEX_DIRECT_DOMAIN}/live/v4/json/",
        json=data,
    )

    return response_data


def send_telegram_message(chat_id, message):
    requests.get(
        f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    )
