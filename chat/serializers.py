from rest_framework import serializers
from .models import ChatMessage, ChatRoom

class ChatMessageSerializer(serializers.ModelSerializer):
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    formatted_time = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'tournament', 'tournament_name', 'username', 'message',
            'message_type', 'created_at', 'formatted_time'
        ]
        read_only_fields = ['created_at', 'ip_address']
    
    def get_formatted_time(self, obj):
        return obj.created_at.strftime('%H:%M')

class ChatMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['tournament', 'username', 'message']
    
    def validate_username(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres")
        return value.strip()
    
    def validate_message(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("El mensaje no puede estar vacío")
        return value.strip()

class ChatRoomSerializer(serializers.ModelSerializer):
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    recent_messages = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'tournament', 'tournament_name', 'is_active',
            'max_messages', 'created_at', 'recent_messages', 'message_count'
        ]
        read_only_fields = ['created_at']
    
    def get_recent_messages(self, obj):
        messages = obj.get_recent_messages()
        return ChatMessageSerializer(messages, many=True).data
    
    def get_message_count(self, obj):
        return obj.tournament.chat_messages.count()

class SystemMessageSerializer(serializers.Serializer):
    """Serializer para crear mensajes del sistema"""
    tournament_id = serializers.IntegerField()
    message = serializers.CharField(max_length=500)
    message_type = serializers.ChoiceField(
        choices=['system', 'celebration'],
        default='system'
    )
    
    def validate_tournament_id(self, value):
        from tournaments.models import Tournament
        try:
            tournament = Tournament.objects.get(id=value)
            return value
        except Tournament.DoesNotExist:
            raise serializers.ValidationError("El torneo no existe")
    
    def create(self, validated_data):
        from tournaments.models import Tournament
        tournament = Tournament.objects.get(id=validated_data['tournament_id'])
        
        return ChatMessage.objects.create(
            tournament=tournament,
            username="Sistema",
            message=validated_data['message'],
            message_type=validated_data['message_type']
        )
