from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, available_players, assign_player, remove_player

router = DefaultRouter()
router.register(r'teams', TeamViewSet)

urlpatterns = [
    # URLs personalizadas ANTES del router
    path('available-players/', available_players, name='available_players'),
    path('assign-player/', assign_player, name='assign_player'),
    path('remove-player/<int:team_id>/<int:user_id>/', remove_player, name='remove_player'),
    
    # Router URLs
    path('', include(router.urls)),
]
