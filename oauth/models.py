from django.db import models
from django.utils import timezone

from projects.models import System, Project
from users.models import User


class OAuthToken(models.Model):
    access_token = models.CharField(max_length=255, verbose_name="Токен доступа")
    expires_at = models.DateTimeField(verbose_name="Истекает в")

    system = models.ForeignKey(
        System,
        on_delete=models.CASCADE,
        related_name="oauth_tokens",
        verbose_name="Система",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="oauth_tokens",
        verbose_name="Пользователь",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="oauth_tokens",
        verbose_name="Проект",
    )

    class Meta:
        db_table = "oauth_token"
        verbose_name = "Токен доступа"
        verbose_name_plural = "Токены доступа"

    def is_expired(self):
        return self.expires_at < timezone.now()

    def __str__(self):
        return f"Токен доступа для проекта {self.project.name} в системе {self.system.name} для пользователя {self.user.username}"
