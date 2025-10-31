from django.db import models
from django.utils import timezone

class Match(models.Model):
    MATCH_STATUS = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
    ]
    
    BRACKET_TYPE = [
        ('winners', 'Winners Bracket'),
        ('losers', 'Losers Bracket'),
        ('grand_final', 'Gran Final'),
        ('final_reset', 'Final Reset'),
    ]
    
    tournament = models.ForeignKey(
        'tournaments.Tournament', 
        on_delete=models.CASCADE, 
        related_name='matches'
    )
    
    # Equipos participantes
    team1 = models.ForeignKey(
        'teams.Team', 
        on_delete=models.CASCADE, 
        related_name='matches_as_team1',
        null=True, blank=True
    )
    team2 = models.ForeignKey(
        'teams.Team', 
        on_delete=models.CASCADE, 
        related_name='matches_as_team2',
        null=True, blank=True
    )
    
    # Resultado
    winner = models.ForeignKey(
        'teams.Team', 
        on_delete=models.CASCADE, 
        related_name='won_matches',
        null=True, blank=True
    )
    
    # Información del bracket
    bracket_type = models.CharField(
        max_length=20, 
        choices=BRACKET_TYPE, 
        default='winners'
    )
    round_number = models.PositiveIntegerField(verbose_name="Número de Ronda")
    match_number = models.PositiveIntegerField(verbose_name="Número de Partida")
    
    # Juego asignado
    game = models.ForeignKey(
        'games.Game', 
        on_delete=models.SET_NULL, 
        null=True, blank=True
    )
    
    # Estado y timestamps
    status = models.CharField(
        max_length=20, 
        choices=MATCH_STATUS, 
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Partidas padre (para bracket de eliminación doble)
    parent_match1 = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='child_matches1',
        null=True, blank=True
    )
    parent_match2 = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='child_matches2',
        null=True, blank=True
    )
    
    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"
        ordering = ['bracket_type', 'round_number', 'match_number']
        unique_together = ['tournament', 'bracket_type', 'round_number', 'match_number']
    
    def __str__(self):
        if self.team1 and self.team2:
            return f"{self.team1.name} vs {self.team2.name} - R{self.round_number}"
        return f"Partida R{self.round_number}M{self.match_number}"
    
    @property
    def is_ready_to_play(self):
        return self.team1 and self.team2 and self.status == 'pending'
    
    def declare_winner(self, winning_team):
        """Declarar ganador y actualizar estadísticas"""
        from .services import MatchService
        return MatchService.declare_winner(self, winning_team)

class BracketGenerator:
    """Generador de brackets para torneos"""
    
    @staticmethod
    def generate_single_elimination(tournament):
        """Generar bracket de eliminación simple"""
        from .services import BracketGenerator as ServiceGenerator
        return ServiceGenerator.generate_single_elimination(tournament)
    
    @staticmethod
    def generate_double_elimination(tournament):
        """Generar bracket de eliminación doble"""
        from .services import BracketGenerator as ServiceGenerator
        return ServiceGenerator.generate_double_elimination(tournament)
