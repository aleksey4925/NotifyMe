from time import sleep
from decimal import Decimal
import requests
import os
import django
from dotenv import load_dotenv

project_folder = os.path.expanduser('~/NotifyMe')
load_dotenv(os.path.join(project_folder, '.env'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notify_me.settings")
django.setup()

from notify_me import settings
from oauth.utils import get_access_token
from projects.models import Chat


def send_telegram_message(chat_id, message):
    requests.get(f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage?chat_id={chat_id}&text={message}")

def get_current_balance(login, access_token):
    data = {
        "method": "AccountManagement",
        "param": {"Action": "Get", "SelectionCriteria": {
            "Logins": [
                login
            ]
        }},
        "token": access_token,
    }

    response_data = requests.post(
        f"https://{settings.YANDEX_DIRECT_DOMAIN}/live/v4/json/",
        json=data,
    )

    try:
        response_data = response_data.json()

        if "data" in response_data and "Accounts" in response_data["data"] and response_data["data"]["Accounts"]:
            return response_data["data"]["Accounts"][0].get("Amount")
        else:
            return None
    except Exception:
        return None

def check_balance_and_notify():
    chats = Chat.objects.all()

    for chat in chats:
        project = chat.project
        threshold = Decimal(project.threshold)
        access_token = get_access_token(project.user, project.system.provider, project.login)

        if not access_token:
            print(f"Нет токена доступа для {project.login} в системе {project.system.name}")
            continue

        current_balance = get_current_balance(project.login, access_token)

        if not current_balance == None:
            project.balance = Decimal(current_balance)
            project.save()

            if current_balance < threshold:
                message = f"Внимание! Ваш баланс на аккаунте {project.login} в системе {project.system.name} опустился ниже порогового уровня. Пожалуйста, пополните баланс, чтобы избежать приостановки рекламных кампаний. Текущий баланс: {current_balance}."

                send_telegram_message(chat.chat_id, message)

                sleep(5)
        else:
            print(f"Произошла непредвиденная ошибка при проверке баланса {project.login} в системе {project.system.name}")

if __name__ == "__main__":
    check_balance_and_notify()
