from django.contrib.auth.forms import AuthenticationForm

from users.models import User


class SigninForm(AuthenticationForm):
    class Meta:
        model = User
