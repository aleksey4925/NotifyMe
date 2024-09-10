from django.utils import timezone
from datetime import timedelta
from oauth.models import OAuthToken
from projects.models import System


def save_or_update_oauth_token(request, provider, response_data, project_id):
    system = System.objects.get(provider=provider)

    token_data = response_data.json()
    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in")
    expires_at = timezone.now() + timedelta(seconds=expires_in)

    oauth_token = OAuthToken.objects.update_or_create(
        user=request.user,
        system=system,
        project_id=project_id,
        defaults={
            "access_token": access_token,
            "expires_at": expires_at,
        },
    )

    return oauth_token


def get_access_token(user, project):
    try:
        token = OAuthToken.objects.get(
            user=user, system=project.system, project=project
        )
        if token.is_expired():
            return None
        return token.access_token
    except OAuthToken.DoesNotExist:
        return None
