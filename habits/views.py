from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Habit
from .paginators import Paginator
from .permissions import IsOwnerOrReadOnly
from .serializers import HabitListSerializer, HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с привычками.

    Предоставляет стандартные CRUD-операции.

    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = Paginator

    def get_queryset(self):
        if self.action == "public":
            return Habit.objects.filter(is_public=True)

        return Habit.objects.filter(user=self.request.user).select_related(
            "user", "related_habit"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return HabitListSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Публичные привычки",
        description="Возвращает список публичных привычек.",
    )
    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def public(self, request):
        """Список публичных привычек (только чтение)."""
        queryset = Habit.objects.filter(is_public=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HabitListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = HabitListSerializer(queryset, many=True)
        return Response(serializer.data)
