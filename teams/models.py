from django.db import models
from django.core.validators import MinLengthValidator

def team_photo_path(instance, filename):
    return f'teams/{instance.tournament.id}/{instance.name}/{filename}'

def player_photo_path(instance, filename):
    return f'teams/{instance.team.tournament.id}/{instance.team.name}/players/{filename}'

class Team(models.Model):
    tournament = models.ForeignKey(
        'tournaments.Tournament', 
        on_delete=models.CASCADE, 
        related_name='teams'
    )
    name = models.CharField(
        max_length=100, 
        validators=[MinLengthValidator(2)],
        verbose_name="Nombre del Equipo"
    )
    
    # Sistema de fotos flexible
    team_photo = models.ImageField(
        upload_to=team_photo_path, 
        blank=True, 
        null=True,
        verbose_name="Foto del Equipo"
    )
    
    # Estadísticas del torneo
    wins = models.PositiveIntegerField(default=0, verbose_name="Victorias")
    losses = models.PositiveIntegerField(default=0, verbose_name="Derrotas")
    points = models.PositiveIntegerField(default=0, verbose_name="Puntos Totales")
    
    # Estados en eliminación doble
    BRACKET_STATUS = [
        ('winners', 'Winners Bracket'),
        ('losers', 'Losers Bracket'),
        ('eliminated', 'Eliminado'),
        ('champion', 'Campeón'),
    ]
    
    bracket_status = models.CharField(
        max_length=20, 
        choices=BRACKET_STATUS, 
        default='winners',
        verbose_name="Estado en Bracket"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        unique_together = ['tournament', 'name']
        ordering = ['-points', '-wins', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.tournament.name}"
    
    @property
    def matches_played(self):
        return self.wins + self.losses
    
    @property
    def win_rate(self):
        if self.matches_played == 0:
            return 0
        return (self.wins / self.matches_played) * 100
    
    def add_victory(self):
        self.wins += 1
        self.points += self.tournament.points_per_win
        self.save()
    
    def add_loss(self):
        self.losses += 1
        self.points += self.tournament.points_per_participation
        # Lógica de eliminación doble
        if self.bracket_status == 'winners':
            self.bracket_status = 'losers'
        elif self.bracket_status == 'losers':
            self.bracket_status = 'eliminated'
        self.save()

class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(
        max_length=100, 
        validators=[MinLengthValidator(2)],
        verbose_name="Nombre del Jugador"
    )
    photo = models.ImageField(
        upload_to=player_photo_path, 
        blank=True, 
        null=True,
        verbose_name="Foto del Jugador"
    )
    is_captain = models.BooleanField(default=False, verbose_name="Es Capitán")
    
    class Meta:
        verbose_name = "Jugador"
        verbose_name_plural = "Jugadores"
        unique_together = ['team', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.team.name})"
