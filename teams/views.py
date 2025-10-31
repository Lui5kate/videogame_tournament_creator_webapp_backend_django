from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Team, Player
from .serializers import (
    TeamSerializer, 
    TeamCreateSerializer, 
    TeamWithPlayersSerializer,
    PlayerSerializer
)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeamCreateSerializer
        elif self.action in ['retrieve', 'list']:
            return TeamWithPlayersSerializer
        return TeamSerializer
    
    def get_queryset(self):
        queryset = Team.objects.all()
        tournament_id = self.request.query_params.get('tournament', None)
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset.order_by('-points', '-wins', 'name')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verificar que el torneo esté en estado de registro
        tournament = serializer.validated_data['tournament']
        if tournament.status not in ['setup', 'registration']:
            return Response(
                {'error': 'El registro de equipos está cerrado para este torneo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar límite de equipos
        if tournament.teams.count() >= tournament.max_teams:
            return Response(
                {'error': f'Se ha alcanzado el límite máximo de {tournament.max_teams} equipos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        team = serializer.save()
        
        # Mensaje del sistema
        from chat.models import ChatMessage
        ChatMessage.create_system_message(
            tournament,
            f"👥 ¡El equipo {team.name} se ha registrado al torneo!"
        )
        
        return Response(
            TeamWithPlayersSerializer(team).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        """Subir foto del equipo"""
        team = self.get_object()
        
        if 'team_photo' not in request.FILES:
            return Response(
                {'error': 'No se proporcionó ninguna imagen'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        team.team_photo = request.FILES['team_photo']
        team.save()
        
        return Response({
            'message': 'Foto subida exitosamente',
            'team_photo_url': team.team_photo.url if team.team_photo else None
        })
    
    @action(detail=True, methods=['get'])
    def players(self, request, pk=None):
        """Obtener jugadores del equipo"""
        team = self.get_object()
        players = team.players.all()
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_player(self, request, pk=None):
        """Agregar jugador al equipo"""
        team = self.get_object()
        
        # Verificar que el torneo no haya iniciado
        if team.tournament.status not in ['setup', 'registration']:
            return Response(
                {'error': 'No se pueden agregar jugadores después de iniciar el torneo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PlayerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        player = serializer.save(team=team)
        
        return Response(
            PlayerSerializer(player).data,
            status=status.HTTP_201_CREATED
        )

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        queryset = Player.objects.all()
        team_id = self.request.query_params.get('team', None)
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verificar que el equipo no tenga más de 2 jugadores
        team = serializer.validated_data['team']
        if team.players.count() >= 2:
            return Response(
                {'error': 'Un equipo no puede tener más de 2 jugadores'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el torneo esté en estado de registro
        if team.tournament.status not in ['setup', 'registration']:
            return Response(
                {'error': 'No se pueden agregar jugadores después de iniciar el torneo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        player = serializer.save()
        
        return Response(
            PlayerSerializer(player).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        """Subir foto del jugador"""
        player = self.get_object()
        
        if 'photo' not in request.FILES:
            return Response(
                {'error': 'No se proporcionó ninguna imagen'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        player.photo = request.FILES['photo']
        player.save()
        
        return Response({
            'message': 'Foto subida exitosamente',
            'photo_url': player.photo.url if player.photo else None
        })
    
    @action(detail=True, methods=['post'])
    def set_captain(self, request, pk=None):
        """Establecer jugador como capitán"""
        player = self.get_object()
        
        # Remover capitanía de otros jugadores del equipo
        player.team.players.update(is_captain=False)
        
        # Establecer como capitán
        player.is_captain = True
        player.save()
        
        return Response({
            'message': f'{player.name} es ahora el capitán del equipo {player.team.name}'
        })
