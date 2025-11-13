from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = [
        ('admin', 'Administrador'),
        ('player', 'Jugador'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='player')
    attuid = models.CharField(max_length=20, unique=True, null=True, blank=True)
    assigned_tournaments = models.ManyToManyField(
        'tournaments.Tournament',
        through='UserTournamentAssignment',
        through_fields=('user', 'tournament'),
        related_name='assigned_players',
        blank=True
    )
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def is_player(self):
        return self.user_type == 'player'
    
    def can_access_tournament(self, tournament_id):
        if self.is_admin():
            return True
        return self.assigned_tournaments.filter(id=tournament_id).exists()

class UserTournamentAssignment(models.Model):
    STATUS_CHOICES = [
        ('invited', 'Invitado'),
        ('confirmed', 'Confirmado'),
        ('declined', 'Rechazado'),
        ('active', 'Activo'),
        ('completed', 'Completado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='tournament_assignments_made'
    )
    
    class Meta:
        unique_together = ['user', 'tournament']
    
    def __str__(self):
        return f"{self.user.username} -> {self.tournament.name} ({self.status})"

class PlayerProfile(models.Model):
    GAME_TYPES = [
        ('fighting', 'Juegos de Pelea'),
        ('racing', 'Carreras'),
        ('sports', 'Deportes'),
        ('shooter', 'Disparos'),
        ('strategy', 'Estrategia'),
        ('rpg', 'RPG'),
        ('platform', 'Plataformas'),
        ('puzzle', 'Puzzle'),
        ('arcade', 'Arcade'),
        ('other', 'Otros'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    has_played_games = models.BooleanField(default=False)
    favorite_game_types = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username})"
