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
    
    def create(self, validated_data):
        players_data = validated_data.pop('players', [])
        team = Team.objects.create(**validated_data)
        
        for player_data in players_data:
            Player.objects.create(team=team, **player_data)
        
        return team

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
