from django.db import models
from django.utils import timezone

class Tournament(models.Model):
    TOURNAMENT_TYPES = [
        ('single', 'Eliminación Simple'),
        ('double', 'Eliminación Doble'),
    ]
    
    STATUS_CHOICES = [
        ('setup', 'Configuración'),
        ('registration', 'Registro Abierto'),
        ('active', 'En Progreso'),
        ('completed', 'Finalizado'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre del Torneo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    tournament_type = models.CharField(
        max_length=10, 
        choices=TOURNAMENT_TYPES, 
        default='single',
        verbose_name="Tipo de Torneo"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='setup',
        verbose_name="Estado"
    )
    max_teams = models.PositiveIntegerField(default=16, verbose_name="Máximo de Equipos")
    points_per_win = models.PositiveIntegerField(default=3, verbose_name="Puntos por Victoria")
    points_per_participation = models.PositiveIntegerField(default=1, verbose_name="Puntos por Participación")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Torneo"
        verbose_name_plural = "Torneos"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def registered_teams_count(self):
        return self.teams.count()
    
    @property
    def completed_matches_count(self):
        return self.matches.filter(status='completed').count()
    
    @property
    def total_matches_count(self):
        return self.matches.count()
    
    def can_start(self):
        return self.registered_teams_count >= 2 and self.status == 'registration'
    
    def start_tournament(self):
        if self.can_start():
            self.status = 'active'
            self.started_at = timezone.now()
            self.save()
            return True
        return False
