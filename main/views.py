from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    context = {"title": "Главная", "content": 'Главная страница приложения "Notify Me"'}

    return render(request, "main/index.html", context)


def about(request):
    context = {
        "title": "О приложении",
        "content": 'Здесь можно узнать цели создания приложения "Notify Me"',
    }

    return render(request, "main/about.html", context)
