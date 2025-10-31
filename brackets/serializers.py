from rest_framework import serializers
from .models import Match
from teams.serializers import TeamSerializer
from games.serializers import GameSerializer

class MatchSerializer(serializers.ModelSerializer):
    team1 = TeamSerializer(read_only=True)
    team2 = TeamSerializer(read_only=True)
    winner = TeamSerializer(read_only=True)
    game = GameSerializer(read_only=True)
    is_ready_to_play = serializers.ReadOnlyField()
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    
    class Meta:
        model = Match
        fields = [
            'id', 'tournament', 'tournament_name', 'team1', 'team2', 'winner',
            'bracket_type', 'round_number', 'match_number', 'game', 'status',
            'created_at', 'started_at', 'completed_at', 'is_ready_to_play'
        ]
        read_only_fields = ['created_at', 'started_at', 'completed_at']

class MatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [
            'tournament', 'team1', 'team2', 'bracket_type',
            'round_number', 'match_number', 'game'
        ]

class DeclareWinnerSerializer(serializers.Serializer):
    match_id = serializers.IntegerField()
    winner_id = serializers.IntegerField()
    
    def validate(self, data):
        try:
            match = Match.objects.get(id=data['match_id'])
            winner = match.tournament.teams.get(id=data['winner_id'])
            
            if winner not in [match.team1, match.team2]:
                raise serializers.ValidationError(
                    "El equipo ganador debe ser uno de los participantes de la partida"
                )
            
            if match.status == 'completed':
                raise serializers.ValidationError("Esta partida ya ha sido completada")
            
            data['match'] = match
            data['winner'] = winner
            
        except Match.DoesNotExist:
            raise serializers.ValidationError("La partida no existe")
        except Exception as e:
            raise serializers.ValidationError(f"Error: {str(e)}")
        
        return data

class BracketVisualizationSerializer(serializers.Serializer):
    """Serializer para datos de visualización del bracket"""
    tournament_id = serializers.IntegerField()
    winners_bracket = serializers.SerializerMethodField()
    losers_bracket = serializers.SerializerMethodField()
    grand_final = serializers.SerializerMethodField()
    
    def get_winners_bracket(self, obj):
        matches = Match.objects.filter(
            tournament_id=obj['tournament_id'],
            bracket_type='winners'
        ).order_by('round_number', 'match_number')
        return MatchSerializer(matches, many=True).data
    
    def get_losers_bracket(self, obj):
        matches = Match.objects.filter(
            tournament_id=obj['tournament_id'],
            bracket_type='losers'
        ).order_by('round_number', 'match_number')
        return MatchSerializer(matches, many=True).data
    
    def get_grand_final(self, obj):
        matches = Match.objects.filter(
            tournament_id=obj['tournament_id'],
            bracket_type__in=['grand_final', 'final_reset']
        ).order_by('bracket_type')
        return MatchSerializer(matches, many=True).data
