from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Team, Player
from .serializers import (
    TeamSerializer, TeamCreateSerializer, TeamUpdateSerializer,
    TeamWithPlayersSerializer, AssignPlayerSerializer, AvailablePlayersSerializer
)
from users.models import User
from users.permissions import IsAdminUser

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeamCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return TeamUpdateSerializer
        elif self.action == 'retrieve':
            return TeamWithPlayersSerializer
        return TeamSerializer
    
    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        team = self.get_object()
        if 'photo' not in request.FILES:
            return Response({'error': 'No se proporcionó ninguna foto'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        team.team_photo = request.FILES['photo']
        team.save()
        
        serializer = self.get_serializer(team)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def players(self, request, pk=None):
        team = self.get_object()
        players = team.players.all()
        from .serializers import PlayerSerializer
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def available_players(request):
    """Obtener jugadores disponibles para asignar a equipos"""
    tournament_id = request.GET.get('tournament')
    if not tournament_id:
        return Response({'error': 'tournament parameter required'}, status=400)
    
    # Obtener todos los jugadores (usuarios tipo player) asignados al torneo
    from users.models import UserTournamentAssignment
    assigned_users = UserTournamentAssignment.objects.filter(
        tournament_id=tournament_id,
        status__in=['confirmed', 'active']
    ).values_list('user_id', flat=True)
    
    players = User.objects.filter(
        id__in=assigned_users,
        user_type='player'
    ).select_related('profile')
    
    serializer = AvailablePlayersSerializer(
        players, 
        many=True, 
        context={'tournament_id': tournament_id}
    )
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def assign_player(request):
    """Asignar un jugador a un equipo"""
    serializer = AssignPlayerSerializer(data=request.data)
    if serializer.is_valid():
        user_id = serializer.validated_data['user_id']
        team_id = serializer.validated_data['team_id']
        is_captain = serializer.validated_data['is_captain']
        
        user = User.objects.get(id=user_id)
        team = Team.objects.get(id=team_id)
        
        # Verificar si ya existe el jugador en este equipo
        player, created = Player.objects.get_or_create(
            user=user,
            team=team,
            defaults={
                'name': f"{user.profile.first_name} {user.profile.last_name}" if hasattr(user, 'profile') else user.username,
                'is_captain': is_captain
            }
        )
        
        if not created:
            # Actualizar si ya existe
            player.is_captain = is_captain
            player.save()
        
        # Si es capitán, quitar capitanía a otros jugadores del equipo
        if is_captain:
            Player.objects.filter(team=team).exclude(id=player.id).update(is_captain=False)
        
        from .serializers import PlayerSerializer
        return Response({
            'message': 'Jugador asignado exitosamente',
            'player': PlayerSerializer(player).data
        })
    
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def remove_player(request, team_id, user_id):
    """Remover un jugador de un equipo"""
    try:
        player = Player.objects.get(team_id=team_id, user_id=user_id)
        player.delete()
        return Response({'message': 'Jugador removido del equipo'})
    except Player.DoesNotExist:
        return Response({'error': 'Jugador no encontrado en este equipo'}, status=404)
