from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, PlayerProfile, UserTournamentAssignment

class PlayerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerProfile
        fields = ['first_name', 'last_name', 'has_played_games', 'favorite_game_types']

class TournamentAssignmentSerializer(serializers.ModelSerializer):
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    tournament_status = serializers.CharField(source='tournament.status', read_only=True)
    
    class Meta:
        model = UserTournamentAssignment
        fields = ['id', 'tournament', 'tournament_name', 'tournament_status', 'status', 'assigned_at']

class UserSerializer(serializers.ModelSerializer):
    profile = PlayerProfileSerializer(required=False)
    tournament_assignments = TournamentAssignmentSerializer(
        source='usertournamentassignment_set', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'user_type', 'attuid', 'profile', 'tournament_assignments']
        read_only_fields = ['id']

class AssignTournamentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    tournament_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=UserTournamentAssignment.STATUS_CHOICES,
        default='invited'
    )

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    has_played_games = serializers.BooleanField(default=False)
    favorite_game_types = serializers.ListField(
        child=serializers.CharField(), 
        required=False, 
        default=list
    )
    
    class Meta:
        model = User
        fields = ['username', 'password', 'attuid', 'first_name', 'last_name', 
                 'has_played_games', 'favorite_game_types']
    
    def validate_attuid(self, value):
        if User.objects.filter(attuid=value).exists():
            raise serializers.ValidationError("Este ATTUID ya está registrado.")
        return value
    
    def create(self, validated_data):
        profile_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'has_played_games': validated_data.pop('has_played_games', False),
            'favorite_game_types': validated_data.pop('favorite_game_types', [])
        }
        
        user = User.objects.create_user(**validated_data)
        PlayerProfile.objects.create(user=user, **profile_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Credenciales inválidas.")
            if not user.is_active:
                raise serializers.ValidationError("Usuario desactivado.")
            data['user'] = user
        else:
            raise serializers.ValidationError("Debe incluir username y password.")
        
        return data
