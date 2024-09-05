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

            access_token = get_access_token(request.user, provider)

            if not access_token:
                request.session["saved_form_data"] = request.POST
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

    access_token = get_access_token(request.user, project.system.provider)

    if not access_token:
        request.session["next_url"] = reverse("projects:index")

        return redirect("oauth:oauth_login", provider=project.system.provider)

    data = {
        "method": "AccountManagement",
        "param": {"Action": "Get", "Logins": [project.login]},
        "token": access_token,
    }

    response_data = requests.post(
        f"https://{settings.YANDEX_DIRECT_DOMAIN}/live/v4/json/",
        json=data,
    )

    try:
        amount = response_data.json()["data"]["Accounts"][0]["Amount"]

        project.balance = Decimal(amount)
        project.save()
    except (IndexError, KeyError, ValueError) as e:
        request.session[f"balance_error_text_{project_id}"] = (
            f"Ошибка при разборе ответа: {repr(e)}"
        )

    return redirect("projects:index")


@login_required
def chats(request, project_id):
    # send_comment_error_text

    project = get_object_or_404(Project, id=project_id, user_id=request.user.id)

    chats = project.chats.all()

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
