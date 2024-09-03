from django.urls import path

from oauth import views

app_name = "oauth"

urlpatterns = [
    path("login/<str:provider>/", views.oauth_login, name="oauth_login"),
    path("callback/<str:provider>/", views.oauth_callback, name="oauth_callback"),
]
