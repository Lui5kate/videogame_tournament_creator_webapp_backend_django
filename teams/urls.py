from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, available_players, assign_player, remove_player, change_team_name, my_team

router = DefaultRouter()
router.register(r'teams', TeamViewSet)

urlpatterns = [
    # URLs personalizadas ANTES del router
    path('available-players/', available_players, name='available_players'),
    path('assign-player/', assign_player, name='assign_player'),
    path('remove-player/<int:team_id>/<int:user_id>/', remove_player, name='remove_player'),
    path('change-team-name/', change_team_name, name='change_team_name'),
    path('my-team/', my_team, name='my_team'),
    
    # Router URLs
    path('', include(router.urls)),
]
