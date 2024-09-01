from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    system = models.CharField(max_length=255, verbose_name="Система")
    login = models.EmailField(verbose_name="Логин")
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Баланс"
    )
    threshold = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Порог"
    )

    class Meta:
        db_table = "project"
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"


class Chat(models.Model):
    chat_id = models.BigIntegerField(verbose_name="Идентификатор телеграм чата")
    comment = models.CharField(max_length=255, verbose_name="Комментарий")
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="chats",
        verbose_name="Айди проекта",
    )

    class Meta:
        db_table = "chat"
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
