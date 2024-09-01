from django.forms import CharField, PasswordInput, TextInput
from django.contrib.auth.forms import AuthenticationForm

from users.models import User


class SigninForm(AuthenticationForm):
    username = CharField()
    password = CharField()

    class Meta:
        model: User
