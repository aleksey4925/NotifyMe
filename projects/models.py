from django.db import models

from users.models import User


class System(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    provider = models.CharField(max_length=255, verbose_name="Провайдер")

    class Meta:
        db_table = "system"
        verbose_name = "Система"
        verbose_name_plural = "Системы"

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    login = models.EmailField(verbose_name="Логин")
    balance = models.DecimalField(
        max_digits=12, decimal_places=6, null=True, blank=True, verbose_name="Баланс"
    )
    threshold = models.BigIntegerField(verbose_name="Порог")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="Пользователь",
    )
    system = models.ForeignKey(
        System,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="Система",
    )
    balance_error = models.CharField(max_length=500, verbose_name="Ошибка баланса")

    class Meta:
        db_table = "project"
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name


class Chat(models.Model):
    chat_id = models.BigIntegerField(verbose_name="Идентификатор телеграм чата")
    comment = models.CharField(max_length=255, verbose_name="Комментарий")
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="chats",
        verbose_name="Проект",
    )
    test_notification_error = models.CharField(
        max_length=500, verbose_name="Ошибка отправки уведомления"
    )

    class Meta:
        db_table = "chat"
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"

    def __str__(self):
        return f"[{self.chat_id}]({self.comment}): '{self.project.name}'"
