from django.db import models

def game_image_path(instance, filename):
    return f'games/{instance.name}/{filename}'

class Game(models.Model):
    PREDEFINED_GAMES = [
        ('mario_kart', '🏎️ Mario Kart'),
        ('smash_bros', '👊 Super Smash Bros'),
        ('marvel_vs_capcom', '⚔️ Marvel vs Capcom 3'),
        ('street_fighter', '🥊 Street Fighter'),
        ('tekken', '🥋 Tekken'),
        ('fifa', '⚽ FIFA'),
        ('rocket_league', '🚗 Rocket League'),
        ('mortal_kombat', '🩸 Mortal Kombat'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre del Juego")
    emoji = models.CharField(
        max_length=10, 
        blank=True, 
        verbose_name="Emoji Identificador"
    )
    image = models.ImageField(
        upload_to=game_image_path, 
        blank=True, 
        null=True,
        verbose_name="Imagen del Juego"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_predefined = models.BooleanField(default=False, verbose_name="Juego Predefinido")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Juego"
        verbose_name_plural = "Juegos"
        ordering = ['is_predefined', 'name']
    
    def __str__(self):
        return f"{self.emoji} {self.name}" if self.emoji else self.name
    
    @classmethod
    def create_predefined_games(cls):
        """Crear juegos predefinidos si no existen"""
        for game_key, game_display in cls.PREDEFINED_GAMES:
            emoji = game_display.split(' ')[0]
            name = ' '.join(game_display.split(' ')[1:])
            
            cls.objects.get_or_create(
                name=name,
                defaults={
                    'emoji': emoji,
                    'is_predefined': True,
                    'description': f'Juego arcade clásico: {name}'
                }
            )

class TournamentGame(models.Model):
    """Relación entre torneos y juegos disponibles"""
    tournament = models.ForeignKey(
        'tournaments.Tournament', 
        on_delete=models.CASCADE, 
        related_name='available_games'
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    is_selected = models.BooleanField(default=True, verbose_name="Seleccionado para el Torneo")
    
    class Meta:
        verbose_name = "Juego del Torneo"
        verbose_name_plural = "Juegos del Torneo"
        unique_together = ['tournament', 'game']
    
    def __str__(self):
        return f"{self.game.name} - {self.tournament.name}"
