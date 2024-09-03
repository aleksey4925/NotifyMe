import requests
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import redirect, render

PROVIDERS = {
    "yandex": {
        "client_id": settings.YANDEX_CLIENT_ID,
        "client_secret": settings.YANDEX_CLIENT_SECRET,
        "authorization_url": "https://oauth.yandex.ru/authorize",
        "token_url": "https://oauth.yandex.ru/token",
    },
}


@login_required
def oauth_login(request, provider):
    provider_config = PROVIDERS.get(provider)
    if not provider_config:
        return render(request, "oauth/error.html", {"error": "No provider found."})

    client_id = provider_config["client_id"]

    authorization_url = f"{provider_config["authorization_url"]}?response_type=code&client_id={client_id}"

    return redirect(authorization_url)


@login_required
def oauth_callback(request, provider):
    provider_config = PROVIDERS.get(provider)

    code = request.GET.get("code")
    if not code:
        return render(
            request, "oauth/error.html", {"error": "Authorization code not found."}
        )

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": provider_config["client_id"],
        "client_secret": provider_config["client_secret"],
    }

    response = requests.post(provider_config["token_url"], data=data)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")

        request.session["yandex_access_token"] = access_token

        next_url = request.session.pop('next_url', None)
        if next_url:
            return redirect(next_url)

        return redirect("main:index")
    else:
        return render(
            request, "oauth/error.html", {"error": "Failed to obtain access token."}
        )
