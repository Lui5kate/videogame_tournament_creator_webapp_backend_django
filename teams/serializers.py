from rest_framework import serializers
from .models import Team, Player

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'photo', 'is_captain']

class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    matches_played = serializers.ReadOnlyField()
    win_rate = serializers.ReadOnlyField()
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'team_photo', 'wins', 'losses', 'points',
            'bracket_status', 'created_at', 'matches_played', 'win_rate',
            'tournament', 'tournament_name', 'players'
        ]
        read_only_fields = ['wins', 'losses', 'points', 'bracket_status', 'created_at']

class TeamCreateSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, write_only=True)
    
    class Meta:
        model = Team
        fields = ['tournament', 'name', 'team_photo', 'players']
    
    def validate_players(self, value):
        if len(value) != 2:
            raise serializers.ValidationError("Debe haber exactamente 2 jugadores por equipo.")
        
        # Verificar que los nombres de jugadores no estén duplicados
        player_names = [player['name'].strip() for player in value]
        if len(set(player_names)) != len(player_names):
            raise serializers.ValidationError("Los nombres de los jugadores deben ser únicos dentro del equipo.")
        
        # Verificar que haya exactamente un capitán
        captains = [player for player in value if player.get('is_captain', False)]
        if len(captains) != 1:
            raise serializers.ValidationError("Debe haber exactamente un capitán por equipo.")
        
        return value
    
    def create(self, validated_data):
        players_data = validated_data.pop('players', [])
        team = Team.objects.create(**validated_data)
        
        for player_data in players_data:
            Player.objects.create(team=team, **player_data)
        
        return team

class TeamUpdateSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, required=False)
    
    class Meta:
        model = Team
        fields = ['name', 'players']
    
    def update(self, instance, validated_data):
        players_data = validated_data.pop('players', [])
        
        # Actualizar nombre del equipo
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        
        # Actualizar jugadores
        if players_data:
            for i, player_data in enumerate(players_data):
                if i < len(instance.players.all()):
                    player = instance.players.all()[i]
                    player.name = player_data.get('name', player.name)
                    player.is_captain = player_data.get('is_captain', player.is_captain)
                    player.save()
        
        return instance

class TeamWithPlayersSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    matches_played = serializers.ReadOnlyField()
    win_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'team_photo', 'wins', 'losses', 'points',
            'bracket_status', 'created_at', 'matches_played', 'win_rate',
            'players'
        ]
