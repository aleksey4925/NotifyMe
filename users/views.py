from django.contrib import auth
from django.shortcuts import redirect, render

from users.forms import SigninForm


def signin(request):
    if request.method == "POST":
        form = SigninForm(data=request.POST)
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)

                return redirect("projects:index")
    else:
        form = SigninForm()

    context = {"title": "Войти", "form": form}

    return render(request, "users/signin.html", context)


def signout(request):
    return redirect("users:signin")
