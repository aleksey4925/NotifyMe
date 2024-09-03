from django.contrib.auth.decorators import login_required
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

                next_url = request.POST.get("next", None)
                if next_url:
                    return redirect(next_url)

                return redirect("main:index")
    else:
        form = SigninForm()

    context = {"title": "Войти", "form": form}

    return render(request, "users/signin.html", context)


@login_required
def signout(request):
    request.session.pop("yandex_access_token", None)

    auth.logout(request)

    return redirect("users:signin")
