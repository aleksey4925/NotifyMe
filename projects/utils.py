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

    # try:
    #     response_data = requests.get(
    #         f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    #     )

    #     if not response_data.status_code == 200:
    #         response_data = response_data.json()

    #         try:
    #             chat = Chat.objects.get(chat_id=chat_id, project=project)
    #             chat.test_notification_error = (
    #                 f"{response_data['error_code']} {response_data['description']}"
    #             )
    #             chat.save()
    #         except Chat.DoesNotExist as e:
    #             chat.test_notification_error = f"Ошибка: {str(e)}"
    #             chat.save()
    # except Exception as e:
    #     chat.test_notification_error = f"Ошибка: {str(e)}"
    #     chat.save()

