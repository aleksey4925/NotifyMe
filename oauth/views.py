import requests
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import redirect, render

from oauth.utils import save_or_update_oauth_token

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

    authorization_url = f"{provider_config['authorization_url']}?response_type=code&client_id={client_id}"

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

    response_data = requests.post(provider_config["token_url"], data=data)

    if response_data.status_code == 200:
        project_id = request.session.pop("project_id")

        save_or_update_oauth_token(request, provider, response_data, project_id)

        next_url = request.session.pop("next_url")

        return redirect(next_url)
    else:
        return render(
            request, "oauth/error.html", {"error": "Failed to obtain access token."}
        )
