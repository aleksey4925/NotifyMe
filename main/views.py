from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    context = {"title": "Главная", "content": 'Главная страница приложения "Notify Me"'}

    return render(request, "main/index.html", context)
