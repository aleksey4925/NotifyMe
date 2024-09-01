from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("signin", views.signin, name="signin"),
    path("signout", views.signout, name="signout"),
]
