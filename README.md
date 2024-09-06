# Проект NotifyMe

Проект Notify Me позволяет управлять кампаниями в Яндекс.Директе и отображать информацию о балансе. Этот файл содержит инструкции по установке и настройке проекта.

## Установка и настройка


Django==4.2.15
requests==2.32.3
python-dotenv==1.0.1


Создайте файл .env в корневом каталоге проекта и добавьте в него ваши переменные окружения:

    SECRET_KEY=your_secret_key
    YANDEX_CLIENT_ID=your_yandex_client_id
    YANDEX_CLIENT_SECRET=your_yandex_client_secret
    TELEGRAM_TOKEN=your_telegram_token

Замените your_yandex_client_id и your_yandex_client_secret на ваши значения.


Выполните миграции для создания необходимых таблиц в базе данных:

    python manage.py makemigrations
    python manage.py migrate


Создайте суперпользователя для доступа к административной панели Django:

    python manage.py createsuperuser

Следуйте инструкциям на экране, чтобы задать имя пользователя, email и пароль для суперпользователя.


Загрузите данные из фикстур в базу данных:

    python manage.py loaddata fixtures/projects/system.json


Не забудьте про команду:

    python manage.py collectstatic


Измените при необходимости параметр YANDEX_DIRECT_DOMAIN в файле settings.py вашего проекта.


Для запуска сервера разработки используйте команду:

    python manage.py runserver
