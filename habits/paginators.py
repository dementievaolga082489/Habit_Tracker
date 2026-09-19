from rest_framework.pagination import LimitOffsetPagination


class Paginator(LimitOffsetPagination):
    """Пагинатор для привычек (limit/offset)."""

    default_limit = 5
    max_limit = 20
