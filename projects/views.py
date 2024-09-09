from decimal import Decimal
from django.urls import reverse
import requests

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from oauth.utils import get_access_token
from projects.models import Project, Chat
from projects.forms import ProjectForm, ChatForm

from notify_me import settings


@login_required
def index(request):
    projects = Project.objects.filter(user_id=request.user.id)

    for project in projects:
        if project.balance:
            project.balance = round(project.balance)

    for project in projects:
        error_text = request.session.pop(f"balance_error_text_{project.id}", None)
        if error_text:
            project.balance_error_texts = error_text

    context = {"title": "Проекты", "projects": projects}

    return render(request, "projects/index.html", context)


@login_required
def add_project(request):
    if request.method == "POST":
        form = ProjectForm(data=request.POST)
        if form.is_valid():
            system = form.cleaned_data["system"]
            provider = system.provider
            login = request.POST.get("login")

            access_token = get_access_token(request.user, provider, login)

            if not access_token:
                request.session["saved_form_data"] = request.POST
                request.session["login"] = request.POST.get("login")
                request.session["next_url"] = reverse("projects:add_project")

                return redirect("oauth:oauth_login", provider=provider)

            project = form.save(commit=False)
            project.user = request.user
            project.save()

            return redirect("projects:index")
    else:
        if "saved_form_data" in request.session:
            request.method = "POST"
            request.POST = request.session.pop("saved_form_data")

            return add_project(request)
        else:
            form = ProjectForm()

    context = {"title": "Добавить проект", "form": form}

    return render(request, "projects/add_project.html", context)


@login_required
def refresh_balance(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    access_token = get_access_token(request.user, project.system.provider, project.login)

    if not access_token:
        request.session["login"] = project.login
        request.session["next_url"] = reverse("projects:index")

        return redirect("oauth:oauth_login", provider=project.system.provider)

    data = {
        "method": "AccountManagement",
        "param": {"Action": "Get", "SelectionCriteria": {
            "Logins": [
                project.login
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
            amount = response_data["data"]["Accounts"][0].get("Amount")

            project.balance = Decimal(amount)
            project.save()
        else:
            request.session[f"balance_error_text_{project_id}"] = f"Error code: {response_data.get('error_code')}, Error str: {response_data.get('error_str')}, Error detail: {response_data.get('error_detail')}"
    except Exception:
        request.session[f"balance_error_text_{project_id}"] = "Неизвестная ошибка"

    return redirect("projects:index")


@login_required
def chats(request, project_id):
    project = get_object_or_404(Project, id=project_id, user_id=request.user.id)

    chats = project.chats.all()

    for chat in chats:
        error_text = request.session.pop(f"test_notification_error_{chat.chat_id}", None)
        if error_text:
            chat.test_notification_error = error_text

    context = {
        "title": "Список чатов проекта",
        "project_id": project_id,
        "chats": chats,
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
    chat_id = request.GET.get('chat_id')

    project = Project.objects.get(id=project_id, user=request.user)

    if project:
        message = "Тестовое уведомление"

        try:
            response_data = requests.get(f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage?chat_id={chat_id}&text={message}")

            if not response_data.status_code == 200:
                response_data = response_data.json()

                request.session[f"test_notification_error_{chat_id}"] = (
                    f"Error code: {response_data['error_code']}, Description: {response_data['description']}"
                )

            return redirect("projects:chats", project_id=project_id)
        except Exception:
            request.session[f"test_notification_error_{chat_id}"] = "Непредвиденная ошибка при отправке тестового уведомления"

            return redirect("projects:chats", project_id=project_id)
    else:
        return redirect("main:index")

@login_required
def delete_chat(request, project_id, chat_id):
    project = Project.objects.get(id=project_id, user=request.user)

    if project:
        chat = Chat.objects.get(id=chat_id, project=project)
        chat.delete()

        return redirect("projects:chats", project_id=project_id)
    else:
        return redirect("main:index")
