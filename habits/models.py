from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Habit(models.Model):
    """
    Модель полезной или приятной привычки пользователя.

    Привычка описывается формулой: «я буду [ДЕЙСТВИЕ] в [ВРЕМЯ] в [МЕСТО]».
    За выполнение полезной привычки пользователь получает вознаграждение
    (поле ``reward``) или выполняет связанную приятную привычку
    (поле ``related_habit``). Одновременно указывать оба поля нельзя.

    Ограничения:
        * ``duration`` — не более 120 секунд;
        * ``periodicity`` — от 1 до 7 дней;
        * у приятной привычки не может быть ``reward`` и ``related_habit``;
        * в ``related_habit`` можно выбрать только приятную привычку.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    place = models.CharField(max_length=255, verbose_name="Место")
    time = models.TimeField(
        verbose_name="Время",
    )
    action = models.CharField(max_length=255, verbose_name="Действие")
    is_pleasant = models.BooleanField(
        default=False, verbose_name="Признак приятной привычки"
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        related_name="related_habits",
    )
    periodicity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name="Периодичность (в днях)",
    )
    last_reminded_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Последнее напоминание"
    )

    reward = models.CharField(
        max_length=255, verbose_name="Вознаграждение", blank=True, null=True
    )
    duration = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        verbose_name="Время на выполнение (в секундах)",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def __str__(self):
        return f"я буду {self.action} в {self.time} в {self.place}"
