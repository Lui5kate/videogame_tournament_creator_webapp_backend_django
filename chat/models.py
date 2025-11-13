from django.db import models
from django.utils import timezone

class ChatMessage(models.Model):
    tournament = models.ForeignKey(
        'tournaments.Tournament', 
        on_delete=models.CASCADE, 
        related_name='chat_messages'
    )
    
    # Usuario autenticado
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    
    # Nombre para mostrar (automático desde perfil)
    display_name = models.CharField(
        max_length=100, 
        verbose_name="Nombre a Mostrar",
        null=True,
        blank=True
    )
    
    message = models.TextField(
        max_length=500, 
        verbose_name="Mensaje"
    )
    
    # Tipos de mensaje
    MESSAGE_TYPES = [
        ('user', 'Mensaje de Usuario'),
        ('system', 'Mensaje del Sistema'),
        ('celebration', 'Celebración'),
    ]
    
    message_type = models.CharField(
        max_length=20, 
        choices=MESSAGE_TYPES, 
        default='user'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.display_name}: {self.message[:50]}..."
    
    def save(self, *args, **kwargs):
        # Auto-generar display_name desde el perfil del usuario
        if self.user and not self.display_name:
            if hasattr(self.user, 'profile'):
                self.display_name = f"{self.user.profile.first_name} {self.user.profile.last_name}"
            else:
                self.display_name = self.user.username
        super().save(*args, **kwargs)
    
    @classmethod
    def create_system_message(cls, tournament, message):
        """Crear mensaje del sistema"""
        return cls.objects.create(
            tournament=tournament,
            display_name="🤖 Sistema",
            message=message,
            message_type='system'
        )
    
    @classmethod
    def create_celebration_message(cls, tournament, team_name, message_type='victory'):
        """Crear mensaje de celebración"""
        celebrations = {
            'victory': f"🎉 ¡{team_name} ha ganado una partida! 🏆",
            'elimination': f"😢 {team_name} ha sido eliminado del torneo",
            'champion': f"👑 ¡{team_name} es el CAMPEÓN del torneo! 🥇",
        }
        
        message = celebrations.get(message_type, f"🎮 Evento: {team_name}")
        
        return cls.objects.create(
            tournament=tournament,
            display_name="🎊 Celebración",
            message=message,
            message_type='celebration'
        )

class ChatRoom(models.Model):
    """Sala de chat para cada torneo"""
    tournament = models.OneToOneField(
        'tournaments.Tournament', 
        on_delete=models.CASCADE, 
        related_name='chat_room'
    )
    
    is_active = models.BooleanField(default=True, verbose_name="Chat Activo")
    max_messages = models.PositiveIntegerField(
        default=1000, 
        verbose_name="Máximo de Mensajes Visibles"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Sala de Chat"
        verbose_name_plural = "Salas de Chat"
    
    def __str__(self):
        return f"Chat - {self.tournament.name}"
    
    def get_recent_messages(self, limit=None):
        """Obtener mensajes recientes"""
        limit = limit or self.max_messages
        return self.tournament.chat_messages.all()[:limit]
