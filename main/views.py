from django.shortcuts import redirect, render


def index(request):
    return redirect("main:about")


def about(request):
    context = {
        "title": "О приложении",
        "content": 'Здесь можно узнать цели создания приложения "NotifyMe"',
    }

    return render(request, "main/about.html", context)
