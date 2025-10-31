from rest_framework import serializers
from .models import Tournament

class TournamentSerializer(serializers.ModelSerializer):
    registered_teams_count = serializers.ReadOnlyField()
    completed_matches_count = serializers.ReadOnlyField()
    total_matches_count = serializers.ReadOnlyField()
    can_start = serializers.ReadOnlyField()
    
    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'description', 'tournament_type', 'status',
            'max_teams', 'points_per_win', 'points_per_participation',
            'created_at', 'updated_at', 'started_at', 'finished_at',
            'registered_teams_count', 'completed_matches_count', 
            'total_matches_count', 'can_start'
        ]
        read_only_fields = ['created_at', 'updated_at', 'started_at', 'finished_at']

class TournamentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = [
            'name', 'description', 'tournament_type', 'max_teams',
            'points_per_win', 'points_per_participation'
        ]

class TournamentDetailSerializer(serializers.ModelSerializer):
    teams = serializers.SerializerMethodField()
    matches = serializers.SerializerMethodField()
    registered_teams_count = serializers.ReadOnlyField()
    completed_matches_count = serializers.ReadOnlyField()
    total_matches_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'description', 'tournament_type', 'status',
            'max_teams', 'points_per_win', 'points_per_participation',
            'created_at', 'updated_at', 'started_at', 'finished_at',
            'registered_teams_count', 'completed_matches_count', 
            'total_matches_count', 'teams', 'matches'
        ]
    
    def get_teams(self, obj):
        from teams.serializers import TeamSerializer
        return TeamSerializer(obj.teams.all(), many=True).data
    
    def get_matches(self, obj):
        from brackets.serializers import MatchSerializer
        return MatchSerializer(obj.matches.all(), many=True).data
