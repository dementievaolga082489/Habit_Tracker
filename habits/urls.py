from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .apps import HabitsConfig
from .views import HabitViewSet

app_name = HabitsConfig.name

router = SimpleRouter()
router.register("", HabitViewSet, basename="habit")

urlpatterns = [
    path("", include(router.urls)),
]
