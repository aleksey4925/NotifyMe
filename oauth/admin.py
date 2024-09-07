from django.contrib import admin

from oauth.models import OAuthToken

admin.site.register(OAuthToken)
