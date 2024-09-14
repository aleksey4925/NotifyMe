from time import sleep
from decimal import Decimal
import os
import django
from dotenv import load_dotenv

project_folder = os.path.expanduser("~/NotifyMe")
load_dotenv(os.path.join(project_folder, ".env"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notify_me.settings")
django.setup()

from oauth.utils import get_access_token
from projects.models import Chat

from projects.utils import get_current_balance, send_telegram_message


def check_balance_and_notify():
    chats = Chat.objects.all()

    for chat in chats:
        project = chat.project
        threshold = Decimal(project.threshold)
        access_token = get_access_token(project.user, project)

        if not access_token:
            project.balance_error = "Нет токена доступа для данного проекта"
            project.save()

            continue

        response_data = get_current_balance(access_token)

        response_data = response_data.json()

        if "data" in response_data:
            if response_data["data"]["Accounts"]:
                amount = response_data["data"]["Accounts"][0].get("Amount")

                project.balance = Decimal(amount)
                project.balance_error = ""
                project.save()

                if project.balance < threshold:
                    message = f"Внимание! Ваш баланс проекта {project.name} в системе {project.system.name} опустился ниже порогового уровня. Пожалуйста, пополните баланс, чтобы избежать приостановки рекламных кампаний. Текущий баланс: {project.balance}."

                    send_telegram_message(chat.chat_id, message)

                    sleep(5)
            else:
                error = response_data["data"]["ActionsResult"][0]["Errors"][0]

                # Ошибка данных
                project.balance_error = f"{error.get('FaultCode')} {error.get('FaultString')} {error.get('FaultDetail')}"
                project.save()
        else:
            # Структурная ошибка
            project.balance_error = f"{response_data.get('error_code')} {response_data.get('error_str')} {response_data.get('error_detail')}"
            project.save()


if __name__ == "__main__":
    check_balance_and_notify()
