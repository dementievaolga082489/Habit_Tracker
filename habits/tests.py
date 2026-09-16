from datetime import time

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import Habit


class HabitTests(APITestCase):
    """Тесты CRUD-операций и прав доступа для привычек."""

    def setUp(self):
        """Создаёт двух пользователей и авторизует первого."""
        self.user = User.objects.create_user(
            email="user@example.com",
            username="user",
            password="StrongPassword123",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="StrongPassword123",
        )

        self.habits_url = reverse("habits:habit-list")

        self.client.force_authenticate(user=self.user)

    def create_habit(self, **kwargs):
        """Создаёт тестовую привычку с возможностью изменить её данные."""
        data = {
            "place": "Дома",
            "time": "09:00:00",
            "action": "Пить воду",
            "is_pleasant": False,
            "periodicity": 1,
            "reward": "Посмотреть сериал",
            "duration": 60,
            "is_public": False,
        }

        data.update(kwargs)

        return self.client.post(
            self.habits_url,
            data,
            format="json",
        )

    def test_create_habit(self):
        """Проверяет создание привычки текущим пользователем."""
        response = self.create_habit()

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        habit = Habit.objects.get()

        self.assertEqual(
            habit.user,
            self.user,
        )
        self.assertEqual(
            habit.action,
            "Пить воду",
        )

    def test_user_can_see_only_own_habits(self):
        """Проверяет, что пользователь видит только свои привычки."""
        Habit.objects.create(
            user=self.other_user,
            place="Дома",
            time=time(10, 0),
            action="Читать книгу",
            duration=60,
        )

        response = self.client.get(self.habits_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["count"],
            0,
        )

    def test_update_own_habit(self):
        """Проверяет редактирование собственной привычки."""
        habit = Habit.objects.create(
            user=self.user,
            place="Дома",
            time=time(9, 0),
            action="Пить воду",
            duration=60,
        )

        url = reverse(
            "habits:habit-detail",
            kwargs={"pk": habit.pk},
        )

        response = self.client.patch(
            url,
            {"action": "Пить больше воды"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        habit.refresh_from_db()

        self.assertEqual(
            habit.action,
            "Пить больше воды",
        )

    def test_user_cannot_update_other_users_habit(self):
        """Проверяет запрет редактирования чужой привычки."""
        habit = Habit.objects.create(
            user=self.other_user,
            place="Дома",
            time=time(9, 0),
            action="Читать книгу",
            duration=60,
        )

        url = reverse(
            "habits:habit-detail",
            kwargs={"pk": habit.pk},
        )

        response = self.client.patch(
            url,
            {"action": "Изменённое действие"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_cannot_delete_other_users_habit(self):
        """Проверяет запрет удаления чужой привычки."""
        habit = Habit.objects.create(
            user=self.other_user,
            place="Дома",
            time=time(9, 0),
            action="Читать книгу",
            duration=60,
        )

        url = reverse(
            "habits:habit-detail",
            kwargs={"pk": habit.pk},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_delete_own_habit(self):
        """Проверяет удаление собственной привычки."""
        habit = Habit.objects.create(
            user=self.user,
            place="Дома",
            time=time(9, 0),
            action="Пить воду",
            duration=60,
        )

        url = reverse(
            "habits:habit-detail",
            kwargs={"pk": habit.pk},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(Habit.objects.filter(pk=habit.pk).exists())


class HabitValidationTests(APITestCase):
    """Тесты бизнес-правил и валидации привычек."""

    def setUp(self):
        """Создаёт тестового пользователя и авторизует его."""
        self.user = User.objects.create_user(
            email="user@example.com",
            username="user",
            password="StrongPassword123",
        )

        self.client.force_authenticate(user=self.user)

        self.habits_url = reverse("habits:habit-list")

    def habit_data(self, **kwargs):
        """Возвращает стандартные данные для создания привычки."""
        data = {
            "place": "Дома",
            "time": "09:00:00",
            "action": "Пить воду",
            "is_pleasant": False,
            "periodicity": 1,
            "duration": 60,
            "is_public": False,
        }

        data.update(kwargs)

        return data

    def test_reward_and_related_habit_cannot_be_used_together(self):
        """Проверяет запрет одновременного reward и related_habit."""
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Дома",
            time=time(10, 0),
            action="Принять ванну",
            is_pleasant=True,
            duration=60,
        )

        response = self.client.post(
            self.habits_url,
            self.habit_data(
                reward="Шоколад",
                related_habit=pleasant_habit.id,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_duration_cannot_be_more_than_120_seconds(self):
        """Проверяет ограничение длительности привычки в 120 секунд."""
        response = self.client.post(
            self.habits_url,
            self.habit_data(duration=121),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_related_habit_must_be_pleasant(self):
        """Проверяет, что связанная привычка должна быть приятной."""
        regular_habit = Habit.objects.create(
            user=self.user,
            place="Дома",
            time=time(10, 0),
            action="Читать книгу",
            is_pleasant=False,
            duration=60,
        )

        response = self.client.post(
            self.habits_url,
            self.habit_data(
                related_habit=regular_habit.id,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_pleasant_habit_cannot_have_reward(self):
        """Проверяет запрет вознаграждения для приятной привычки."""
        response = self.client.post(
            self.habits_url,
            self.habit_data(
                is_pleasant=True,
                reward="Шоколад",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_pleasant_habit_cannot_have_related_habit(self):
        """Проверяет запрет связанной привычки для приятной привычки."""
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place="Дома",
            time=time(10, 0),
            action="Принять ванну",
            is_pleasant=True,
            duration=60,
        )

        response = self.client.post(
            self.habits_url,
            self.habit_data(
                is_pleasant=True,
                related_habit=pleasant_habit.id,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_periodicity_cannot_be_more_than_7_days(self):
        """Проверяет, что периодичность не может превышать 7 дней."""
        response = self.client.post(
            self.habits_url,
            self.habit_data(periodicity=8),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_duration_120_seconds_is_allowed(self):
        """Проверяет допустимое максимальное значение длительности — 120 секунд."""
        response = self.client.post(
            self.habits_url,
            self.habit_data(duration=120),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_periodicity_7_days_is_allowed(self):
        """Проверяет допустимое максимальное значение периодичности — 7 дней."""
        response = self.client.post(
            self.habits_url,
            self.habit_data(periodicity=7),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )


class PublicHabitTests(APITestCase):
    """Тесты публичных привычек."""

    def setUp(self):
        """Создаёт двух пользователей и авторизует первого."""
        self.user = User.objects.create_user(
            email="user@example.com",
            username="user",
            password="StrongPassword123",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            username="other",
            password="StrongPassword123",
        )

        self.public_url = reverse("habits:habit-public")

        self.client.force_authenticate(user=self.user)

    def test_public_habits_are_visible(self):
        """Проверяет отображение публичных привычек других пользователей."""
        Habit.objects.create(
            user=self.other_user,
            place="Дома",
            time=time(9, 0),
            action="Читать книгу",
            duration=60,
            is_public=True,
        )

        response = self.client.get(self.public_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_private_habits_are_not_visible(self):
        """Проверяет, что приватные привычки не попадают в публичный список."""
        Habit.objects.create(
            user=self.other_user,
            place="Дома",
            time=time(9, 0),
            action="Читать книгу",
            duration=60,
            is_public=False,
        )

        response = self.client.get(self.public_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["count"],
            0,
        )

    def test_public_habits_cannot_be_changed_by_other_user(self):
        """Проверяет запрет изменения чужой публичной привычки."""
        habit = Habit.objects.create(
            user=self.other_user,
            place="Дома",
            time=time(9, 0),
            action="Читать книгу",
            duration=60,
            is_public=True,
        )

        detail_url = reverse(
            "habits:habit-detail",
            kwargs={"pk": habit.pk},
        )

        response = self.client.patch(
            detail_url,
            {"action": "Изменённое действие"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
