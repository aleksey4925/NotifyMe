from django.shortcuts import render


def signin(request):
    context = {"title": "Войти"}

    return render(request, "users/signin.html", context)
