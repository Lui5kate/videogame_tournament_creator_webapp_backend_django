from rest_framework import serializers
from .models import Game, TournamentGame

class GameSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = [
            'id', 'name', 'emoji', 'image', 'description',
            'is_predefined', 'is_active', 'created_at', 'display_name'
        ]
        read_only_fields = ['created_at']
    
    def get_display_name(self, obj):
        return f"{obj.emoji} {obj.name}" if obj.emoji else obj.name

class TournamentGameSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)
    game_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = TournamentGame
        fields = ['id', 'tournament', 'game', 'game_id', 'is_selected']

class PredefinedGamesSerializer(serializers.Serializer):
    """Serializer para mostrar juegos predefinidos disponibles"""
    games = serializers.SerializerMethodField()
    
    def get_games(self, obj):
        predefined_games = []
        for game_key, game_display in Game.PREDEFINED_GAMES:
            emoji = game_display.split(' ')[0]
            name = ' '.join(game_display.split(' ')[1:])
            predefined_games.append({
                'key': game_key,
                'name': name,
                'emoji': emoji,
                'display_name': game_display
            })
        return predefined_games
