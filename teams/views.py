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
    
    def get_queryset(self):
        queryset = Team.objects.all()
        tournament_id = self.request.query_params.get('tournament')
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset
    
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
    
    # Obtener usuarios que ya están asignados a equipos en este torneo específico
    from teams.models import Player
    assigned_user_ids = Player.objects.filter(
        team__tournament_id=tournament_id,
        user__isnull=False
    ).values_list('user_id', flat=True)
    
    # Obtener todos los jugadores que NO están asignados a este torneo
    players = User.objects.filter(
        user_type='player'
    ).exclude(
        id__in=assigned_user_ids
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_team_name(request):
    """Cambiar nombre de equipo (solo capitanes, una vez)"""
    team_id = request.data.get('team_id')
    new_name = request.data.get('new_name', '').strip()
    
    if not team_id or not new_name:
        return Response({'error': 'team_id y new_name son requeridos'}, status=400)
    
    if len(new_name) < 2:
        return Response({'error': 'El nombre debe tener al menos 2 caracteres'}, status=400)
    
    try:
        team = Team.objects.get(id=team_id)
        
        # Verificar que el usuario es capitán del equipo
        player = Player.objects.get(team=team, user=request.user, is_captain=True)
        
        # Verificar que no haya cambiado el nombre antes
        if team.name_changed:
            return Response({'error': 'El nombre del equipo ya fue cambiado anteriormente'}, status=400)
        
        # Verificar que el nombre no esté en uso en el torneo
        if Team.objects.filter(tournament=team.tournament, name=new_name).exclude(id=team.id).exists():
            return Response({'error': 'Ya existe un equipo con ese nombre en este torneo'}, status=400)
        
        # Cambiar nombre
        team.name = new_name
        team.name_changed = True
        team.save()
        
        return Response({
            'message': 'Nombre del equipo cambiado exitosamente',
            'team': TeamSerializer(team).data
        })
        
    except Team.DoesNotExist:
        return Response({'error': 'Equipo no encontrado'}, status=404)
    except Player.DoesNotExist:
        return Response({'error': 'Solo el capitán del equipo puede cambiar el nombre'}, status=403)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_team(request):
    """Obtener el equipo del usuario en un torneo específico"""
    tournament_id = request.GET.get('tournament')
    if not tournament_id:
        return Response({'error': 'tournament parameter required'}, status=400)
    
    try:
        player = Player.objects.get(
            user=request.user,
            team__tournament_id=tournament_id
        )
        return Response({
            'team': TeamWithPlayersSerializer(player.team).data,
            'is_captain': player.is_captain
        })
    except Player.DoesNotExist:
        return Response({'error': 'No tienes equipo asignado en este torneo'}, status=404)
