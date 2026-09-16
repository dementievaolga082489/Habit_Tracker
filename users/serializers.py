"""
Сериализаторы приложения users.

Содержит сериализаторы для регистрации, просмотра и редактирования
профиля пользователя, а также для работы с Telegram chat_id.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователя для чтения и редактирования профиля.

    Используется в эндпоинтах ``/api/users/me/`` и подобных.
    Поле ``email`` доступно только для чтения (это логин).
    Поля ``phone`` и ``tg_id`` можно редактировать.
    """

    class Meta:
        model = User
        fields = ["id", "email", "username", "phone", "tg_id"]
        read_only_fields = ["id", "email"]
        extra_kwargs = {
            "username": {
                "help_text": "Отображаемое имя пользователя.",
                "required": False,
            },
            "phone": {
                "help_text": "Номер телефона (необязательно).",
                "required": False,
            },
            "tg_id": {
                "help_text": "ID чата в Telegram для получения напоминаний.",
                "required": False,
            },
        }


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации нового пользователя.

    Принимает ``email`` (логин), ``username``, ``password``
    и опционально ``phone``. Пароль хешируется через
    ``User.objects.create_user()``.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Пароль длиной не менее 8 символов.",
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Повтор пароля для подтверждения.",
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["email", "username", "password", "password_confirm", "phone"]
        extra_kwargs = {
            "email": {
                "required": True,
                "help_text": "Email используется в качестве логина.",
            },
            "username": {
                "required": True,
                "help_text": "Отображаемое имя пользователя.",
            },
            "phone": {
                "required": False,
                "help_text": "Номер телефона (необязательно).",
            },
        }

    def validate(self, data: dict) -> dict:
        """
        Проверяет, что пароль и его подтверждение совпадают.

        """
        if data.get("password") != data.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Пароли не совпадают."}
            )
        return data

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        validated_data.pop("password_confirm", None)

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user
