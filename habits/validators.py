from rest_framework.exceptions import ValidationError


def validate_habit(data):
    """Комплексная валидация привычки."""
    is_pleasant = data.get("is_pleasant", False)
    related_habit = data.get("related_habit")
    reward = data.get("reward")
    duration = data.get("duration")
    periodicity = data.get("periodicity", 1)

    # 1. Нельзя одновременно связанную привычку и вознаграждение
    if related_habit and reward:
        raise ValidationError(
            "Нельзя одновременно указывать связанную привычку и вознаграждение."
        )

    # 2. Время выполнения ≤ 120 секунд
    if duration and duration > 120:
        raise ValidationError("Время выполнения не может превышать 120 секунд.")

    # 3. В связанные привычки только приятные
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError(
            "В связанные привычки можно выбирать только приятные привычки."
        )

    # 4. У приятной привычки не может быть вознаграждения или связанной
    if is_pleasant:
        if reward:
            raise ValidationError("У приятной привычки не может быть вознаграждения.")
        if related_habit:
            raise ValidationError(
                "У приятной привычки не может быть связанной привычки."
            )

    # 5. Периодичность не реже 1 раза в 7 дней
    if periodicity and (periodicity < 1 or periodicity > 7):
        raise ValidationError("Периодичность должна быть от 1 до 7 дней.")

    return data
