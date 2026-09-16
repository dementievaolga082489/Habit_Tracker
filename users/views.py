from rest_framework import generics, permissions, status
from rest_framework.response import Response

from users.models import User
from users.serializers import RegisterSerializer, UserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """
    View для регистрации нового пользователя.

    Доступна без аутентификации (``AllowAny``). Принимает POST
    с полями ``email``, ``username``, ``password``, ``password_confirm``
    и опционально ``phone``.

    Пароль хешируется внутри ``RegisterSerializer.create()`` через
    ``User.objects.create_user()``, поэтому дополнительно вызывать
    ``set_password`` не нужно.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """
        Создаёт пользователя и возвращает его профиль без пароля.

        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View для просмотра и редактирования профиля текущего пользователя.

    Доступна только аутентифицированным пользователям.
    Позволяет изменить ``username``, ``phone`` и ``tg_id``.
    Поле ``email`` доступно только для чтения.
    """

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self) -> User:
        """
        Возвращает текущего пользователя.

        """
        return self.request.user
