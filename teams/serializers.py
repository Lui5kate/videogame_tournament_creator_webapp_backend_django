from rest_framework import serializers
from .models import Team, Player
from users.models import User

class PlayerSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = ['id', 'name', 'photo', 'is_captain', 'user_info']
    
    def get_user_info(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'attuid': obj.user.attuid,
                'full_name': f"{obj.user.profile.first_name} {obj.user.profile.last_name}" if hasattr(obj.user, 'profile') else obj.user.username
            }
        return None

class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)
    matches_played = serializers.ReadOnlyField()
    win_rate = serializers.ReadOnlyField()
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'name_changed', 'team_photo', 'wins', 'losses', 'points',
            'bracket_status', 'created_at', 'matches_played', 'win_rate',
            'tournament', 'tournament_name', 'players'
        ]
        read_only_fields = ['wins', 'losses', 'points', 'bracket_status', 'created_at', 'name_changed']

class AssignPlayerSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    team_id = serializers.IntegerField()
    is_captain = serializers.BooleanField(default=False)
    
    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value, user_type='player')
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Jugador no encontrado")
    
    def validate_team_id(self, value):
        try:
            Team.objects.get(id=value)
            return value
        except Team.DoesNotExist:
            raise serializers.ValidationError("Equipo no encontrado")
    
    def validate(self, data):
        # Verificar que el jugador no esté ya en otro equipo del mismo torneo
        team = Team.objects.get(id=data['team_id'])
        user = User.objects.get(id=data['user_id'])
        
        existing_player = Player.objects.filter(
            user=user,
            team__tournament=team.tournament
        ).first()
        
        if existing_player and existing_player.team.id != team.id:
            raise serializers.ValidationError(
                f"El jugador ya está asignado al equipo '{existing_player.team.name}'"
            )
        
        return data

class AvailablePlayersSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    current_team = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'attuid', 'full_name', 'current_team']
    
    def get_full_name(self, obj):
        if hasattr(obj, 'profile'):
            return f"{obj.profile.first_name} {obj.profile.last_name}"
        return obj.username
    
    def get_current_team(self, obj):
        tournament_id = self.context.get('tournament_id')
        if tournament_id:
            player = Player.objects.filter(
                user=obj,
                team__tournament_id=tournament_id
            ).first()
            if player:
                return {
                    'id': player.team.id,
                    'name': player.team.name,
                    'is_captain': player.is_captain
                }
        return None

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
            'id', 'name', 'name_changed', 'team_photo', 'wins', 'losses', 'points',
            'bracket_status', 'created_at', 'matches_played', 'win_rate',
            'players'
        ]
