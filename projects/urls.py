from django.urls import path

from projects import views

app_name = "projects"

urlpatterns = [
    path("", views.index, name="index"),
    path("add_project/", views.add_project, name="add_project"),
    path(
        "<int:project_id>/refresh_balance/",
        views.refresh_balance,
        name="refresh_balance",
    ),
    path("<int:project_id>/chats/", views.chats, name="chats"),
    path("<int:project_id>/chats/add_chat/", views.add_chat, name="add_chat"),
    path(
        "<int:project_id>/chats/<int:chat_id>/send-test-notification/",
        views.send_test_notification,
        name="send_test_notification",
    ),
]
