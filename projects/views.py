from decimal import Decimal
from django.urls import reverse
import requests

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from check_balance import get_current_balance
from oauth.utils import get_access_token
from projects.models import Project, Chat
from projects.forms import ProjectForm, ChatForm

from notify_me import settings


@login_required
def index(request):
    projects = Project.objects.filter(user=request.user)

    context = {"title": "Проекты", "projects": projects}

    return render(request, "projects/index.html", context)


@login_required
def add_project(request):
    if request.method == "POST":
        form = ProjectForm(data=request.POST)
        if form.is_valid():
            system = form.cleaned_data["system"]
            provider = system.provider

            project = form.save(commit=False)
            project.user = request.user
            project.save()

            request.session["project_id"] = project.id
            request.session["next_url"] = reverse("projects:edit_project_balance", kwargs={"project_id": project.id})

            return redirect("oauth:oauth_login", provider=provider)
    else:
        form = ProjectForm()

    context = {"title": "Добавить проект", "form": form}

    return render(request, "projects/add_project.html", context)


@login_required
def edit_project_balance(request, project_id):
    project = Project.objects.get(id=project_id, user=request.user)

    access_token = get_access_token(request.user, project)

    if not access_token:
        project.balance_error = f"Токен доступа для {project.login} в системе {project.system.name} не найден"
        project.save()

        return redirect("projects:index")

    response_data = get_current_balance(project.login, access_token)

    response_data = response_data.json()

    if "data" in response_data:
        if response_data["data"]["Accounts"]:
            amount = response_data["data"]["Accounts"][0].get("Amount")

            project.balance = Decimal(amount)
            project.save()

            return redirect("projects:chats", project_id=project_id)
        else:
            error = response_data["data"]["ActionsResult"][0]["Errors"][0]

            # Ошибка данных
            error_msg = f"{error.get('FaultCode')} {error.get('FaultString')} {error.get('FaultDetail')}"
    else:
        # Структурная ошибка
        error_msg = f"{response_data.get('error_code')} {response_data.get('error_str')} {response_data.get('error_detail')}"

    project.balance_error = error_msg
    project.save()

    return redirect("projects:index")


@login_required
def refresh_balance(request, project_id):
    project = Project.objects.get(id=project_id, user=request.user)

    access_token = get_access_token(request.user, project)

    if not access_token:
        project.balance_error = (
            f"Нет токена доступа для {project.login} в системе {project.system.name}"
        )
        project.save()

        return redirect("projects:index")

    response_data = get_current_balance(project.login, access_token)

    response_data = response_data.json()

    if "data" in response_data:
        if response_data["data"]["Accounts"]:
            amount = response_data["data"]["Accounts"][0].get("Amount")

            project.balance = Decimal(amount)
        else:
            error = response_data["data"]["ActionsResult"][0]["Errors"][0]

            # Ошибка данных
            error_msg = f"{error.get('FaultCode')} {error.get('FaultString')} {error.get('FaultDetail')}"

            project.balance_error = error_msg
    else:
        # Структурная ошибка
        error_msg = f"{response_data.get('error_code')} {response_data.get('error_str')} {response_data.get('error_detail')}"

        project.balance_error = error_msg

    project.save()

    return redirect("projects:index")


@login_required
def chats(request, project_id):
    project = get_object_or_404(Project, id=project_id, user_id=request.user.id)

    chats = project.chats.all()

    test_notification_error_key = next(
        (key for key in request.session.keys() if "test_notification_error_" in key),
        None,
    )

    if test_notification_error_key:
        test_chat_id = test_notification_error_key.replace(
            "test_notification_error_", ""
        )
        test_notification_error = request.session.pop(test_notification_error_key)
    else:
        test_notification_error = ""
        test_chat_id = ""

    context = {
        "title": "Список чатов проекта",
        "project_id": project_id,
        "chats": chats,
        "test_notification_error": test_notification_error,
        "test_chat_id": test_chat_id,
    }

    return render(request, "projects/chats.html", context)


@login_required
def add_chat(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)

    form = ChatForm(data=request.POST)
    if form.is_valid():
        chat = form.save(commit=False)
        chat.project = project
        chat.save()

        return redirect("projects:chats", project_id=project_id)
    else:
        chats = Chat.objects.filter(project_id=project_id)

        context = {
            "title": "Список чатов проекта",
            "project_id": project_id,
            "form": form,
            "chats": chats,
        }

        return render(request, "projects/chats.html", context)


@login_required
def send_test_notification(request, project_id):
    chat_id = request.GET.get("chat_id")
    is_new = request.GET.get("is_new", None)

    project = Project.objects.get(id=project_id, user=request.user)

    message = "Тестовое уведомление"

    try:
        response_data = requests.get(
            f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        )

        if not response_data.status_code == 200:
            response_data = response_data.json()

            if is_new:
                request.session[f"test_notification_error_{chat_id}"] = f"{response_data['error_code']} {response_data['description']}"
            else:
                try:
                    chat = Chat.objects.get(chat_id=chat_id, project=project)
                    chat.test_notification_error = (
                        f"{response_data['error_code']} {response_data['description']}"
                    )
                    chat.save()
                except Chat.DoesNotExist as e:
                    request.session[f"test_notification_error_{chat_id}"] = f"Ошибка: {str(e)}"

        return redirect("projects:chats", project_id=project_id)
    except Exception as e:
        request.session[f"test_notification_error_{chat_id}"] = f"Ошибка: {str(e)}"

        return redirect("projects:chats", project_id=project_id)


@login_required
def delete_chat(request, project_id, chat_id):
    project = Project.objects.get(id=project_id, user=request.user)

    if project:
        chat = Chat.objects.get(id=chat_id, project=project)
        chat.delete()

        return redirect("projects:chats", project_id=project_id)
    else:
        return redirect("main:index")
