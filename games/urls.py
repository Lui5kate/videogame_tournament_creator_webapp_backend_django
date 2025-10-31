from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameViewSet, TournamentGameViewSet

router = DefaultRouter()
router.register(r'games', GameViewSet)
router.register(r'tournament-games', TournamentGameViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
