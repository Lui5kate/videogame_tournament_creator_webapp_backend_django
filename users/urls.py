from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('game-types/', views.game_types, name='game_types'),
    
    # Admin endpoints
    path('players/', views.list_players, name='list_players'),
    path('assign-tournament/', views.assign_tournament, name='assign_tournament'),
    path('remove-assignment/<int:user_id>/<int:tournament_id>/', views.remove_tournament_assignment, name='remove_assignment'),
    
    # Player endpoints
    path('my-tournaments/', views.my_tournaments, name='my_tournaments'),
]
