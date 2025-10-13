from django.db import models
from django.utils import timezone

class ChatMessage(models.Model):
    tournament = models.ForeignKey(
        'tournaments.Tournament', 
        on_delete=models.CASCADE, 
        related_name='chat_messages'
    )
    
    # Usuario simple sin autenticación
    username = models.CharField(
        max_length=50, 
        verbose_name="Nombre de Usuario"
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
    
    # Información adicional
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.username}: {self.message[:50]}..."
    
    @classmethod
    def create_system_message(cls, tournament, message):
        """Crear mensaje del sistema"""
        return cls.objects.create(
            tournament=tournament,
            username="Sistema",
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
            username="Sistema",
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
        default=100, 
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
    
    def clean_old_messages(self):
        """Limpiar mensajes antiguos si exceden el límite"""
        messages = self.tournament.chat_messages.all()
        if messages.count() > self.max_messages:
            excess_count = messages.count() - self.max_messages
            old_messages = messages[self.max_messages:]
            for msg in old_messages:
                msg.delete()
