from django.shortcuts import redirect, render

from projects.models import Project, Chat


def index(request):
    # balance_error_text

    context = {
        "title": "Проекты",
    }

    projects = Project.objects.all()

    for project in projects:
        project.balance = (
            round(project.balance) if project.balance is not None else None
        )
        project.threshold = round(project.threshold)

    context.update({"projects": projects})

    return render(request, "projects/index.html", context)


def add_project(request):
    if request.method == "POST":
        name = request.POST.get("name")
        system = request.POST.get("system")
        login = request.POST.get("login")
        threshold = request.POST.get("threshold")

        Project.objects.create(
            name=name, system=system, login=login, threshold=threshold
        )

        return redirect("projects:index")
    else:
        context = {"title": "Добавить проект"}

        return render(request, "projects/add_project.html", context)


def chats(request, project_id):
    # send_comment_error_text

    context = {"title": "Список чатов проекта", "project_id": project_id}

    chats = Chat.objects.filter(project_id=project_id)

    context.update({"chats": chats})

    return render(request, "projects/chats.html", context)


def add_chat(request, project_id):
    chat_id = request.POST.get("chat_id")
    comment = request.POST.get("comment")

    Chat.objects.create(chat_id=chat_id, comment=comment, project_id=project_id)

    return redirect("projects:chats", project_id=project_id)
