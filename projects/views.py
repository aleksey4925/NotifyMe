from django.shortcuts import render


def index(request):
    context = {"title": "Проекты"}

    return render(request, "projects/index.html", context)


def add_project(request):
    context = {"title": "Добавить проект"}

    return render(request, "projects/add_project.html", context)


def chats(request, project_id):
    context = {"title": "Список чатов проекта"}

    return render(request, "projects/chats.html", context)
