from django.core.management.base import BaseCommand
from decimal import Decimal
import requests

from notify_me import settings
from oauth.utils import get_access_token
from projects.models import Chat


class Command(BaseCommand):
    help = "Проверяет баланс и уведомляет, если он ниже порогового значения"

    def send_telegram_message(self, chat_id, message):
        requests.get(
            f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage",
            params={"chat_id": chat_id, "text": message},
        )

    def get_current_balance(self, login, access_token):
        data = {
            "method": "AccountManagement",
            "param": {"Action": "Get", "Logins": [login]},
            "token": access_token,
        }

        response_data = requests.post(
            f"https://{settings.YANDEX_DIRECT_DOMAIN}/live/v4/json/",
            json=data,
        )

        return response_data.json()["data"]["Accounts"][0]["Amount"]

    def handle(self, *args, **kwargs):
        chats = Chat.objects.all()
        for chat in chats:
            project = chat.project
            threshold = Decimal(project.threshold)
            access_token = get_access_token(project.user, project.system.provider)

            if not access_token:
                continue

            try:
                current_balance = self.get_current_balance(project.login, access_token)

                project.balance = Decimal(current_balance)
                project.save()

                if current_balance < threshold:
                    message = f"Внимание! Ваш баланс на аккаунте {project.login} системы {project.system.name} опустился ниже порогового уровня. Пожалуйста, пополните баланс, чтобы избежать приостановки рекламных кампаний. Текущий баланс: {current_balance}."

                    self.send_telegram_message(chat.chat_id, message)
            except Exception as e:
                continue
