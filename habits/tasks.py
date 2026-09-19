from celery import shared_task
from django.utils import timezone

from .models import Habit
from .services import send_telegram_message


@shared_task
def send_habit_reminders():
    now = timezone.localtime()

    habits = Habit.objects.filter(
        time__hour=now.hour,
        time__minute=now.minute,
    ).select_related("user")

    for habit in habits:
        chat_id = habit.user.tg_id

        if not chat_id:
            continue

        if habit.last_reminded_at:
            last_reminded = timezone.localtime(habit.last_reminded_at)
            days_passed = (now.date() - last_reminded.date()).days

            if days_passed < habit.periodicity:
                continue

        message = (
            "Напоминание!\n"
            f"Действие: {habit.action}\n"
            f"Место: {habit.place}\n"
            f"Время: {habit.time.strftime('%H:%M')}"
        )

        if send_telegram_message(chat_id, message):
            habit.last_reminded_at = now
            habit.save(update_fields=["last_reminded_at"])
