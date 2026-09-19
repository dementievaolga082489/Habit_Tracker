from rest_framework import serializers

from .models import Habit
from .validators import validate_habit


class HabitSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор привычки.

    Используется для создания, редактирования и детального просмотра.
    """

    class Meta:
        model = Habit
        fields = [
            "id",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "created_at",
            "user",
        ]
        read_only_fields = ["id", "created_at", "user"]

    def validate(self, data):
        if self.instance:
            data["is_pleasant"] = data.get(
                "is_pleasant",
                self.instance.is_pleasant,
            )
            data["related_habit"] = data.get(
                "related_habit",
                self.instance.related_habit,
            )
            data["reward"] = data.get(
                "reward",
                self.instance.reward,
            )
            data["duration"] = data.get(
                "duration",
                self.instance.duration,
            )
            data["periodicity"] = data.get(
                "periodicity",
                self.instance.periodicity,
            )

        return validate_habit(data)


class HabitListSerializer(serializers.ModelSerializer):
    """Облегчённый для списка."""

    class Meta:
        model = Habit
        fields = ["id", "action", "time", "place", "is_public"]
