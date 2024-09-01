from django.urls import path

from projects import views

app_name = "projects"

urlpatterns = [
    path("", views.index, name="index"),
    path("add_project/", views.add_project, name="add_project"),
    path("<int:project_id>/chats/", views.chats, name="chats"),
    path("<int:project_id>/chats/add_chat/", views.add_chat, name="add_chat"),
]
