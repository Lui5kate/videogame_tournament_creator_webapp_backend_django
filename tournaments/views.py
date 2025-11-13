from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Tournament
from .serializers import (
    TournamentSerializer, 
    TournamentCreateSerializer, 
    TournamentDetailSerializer
)
from brackets.models import BracketGenerator

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TournamentCreateSerializer
        elif self.action == 'retrieve':
            return TournamentDetailSerializer
        return TournamentSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Crear torneo con estado inicial
        tournament = serializer.save(status='registration')
        
        # Generar equipos automáticamente
        from teams.models import Team
        max_teams = tournament.max_teams
        for i in range(1, max_teams + 1):
            Team.objects.create(
                name=f"Equipo {i}",
                tournament=tournament
            )
        
        # Crear sala de chat automáticamente
        from chat.models import ChatRoom
        ChatRoom.objects.get_or_create(tournament=tournament)
        
        return Response(
            TournamentSerializer(tournament).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Iniciar torneo y generar brackets"""
        tournament = self.get_object()
        
        if not tournament.can_start():
            return Response(
                {'error': 'El torneo no puede iniciarse. Necesita al menos 2 equipos registrados.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Iniciar torneo
        tournament.start_tournament()
        
        # Generar brackets según el tipo
        if tournament.tournament_type == 'single':
            success = BracketGenerator.generate_single_elimination(tournament)
        else:
            success = BracketGenerator.generate_double_elimination(tournament)
        
        if not success:
            return Response(
                {'error': 'Error al generar brackets'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Mensaje del sistema
        from chat.models import ChatMessage
        ChatMessage.create_system_message(
            tournament,
            f"🚀 ¡El torneo {tournament.name} ha comenzado! ¡Que empiecen los juegos! 🎮"
        )
        
        return Response({
            'message': 'Torneo iniciado exitosamente',
            'tournament': TournamentSerializer(tournament).data
        })
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Obtener estadísticas del torneo"""
        tournament = self.get_object()
        
        # Calcular estadísticas
        teams = tournament.teams.all()
        matches = tournament.matches.all()
        
        stats = {
            'tournament_info': {
                'name': tournament.name,
                'type': tournament.get_tournament_type_display(),
                'status': tournament.get_status_display(),
                'created_at': tournament.created_at,
                'started_at': tournament.started_at,
                'finished_at': tournament.finished_at,
            },
            'teams_stats': {
                'total_teams': teams.count(),
                'active_teams': teams.exclude(bracket_status='eliminated').count(),
                'eliminated_teams': teams.filter(bracket_status='eliminated').count(),
                'champion': teams.filter(bracket_status='champion').first(),
            },
            'matches_stats': {
                'total_matches': matches.count(),
                'completed_matches': matches.filter(status='completed').count(),
                'pending_matches': matches.filter(status='pending').count(),
                'in_progress_matches': matches.filter(status='in_progress').count(),
            },
            'leaderboard': [
                {
                    'team_name': team.name,
                    'points': team.points,
                    'wins': team.wins,
                    'losses': team.losses,
                    'win_rate': team.win_rate,
                    'bracket_status': team.get_bracket_status_display(),
                }
                for team in teams.order_by('-points', '-wins', 'name')
            ]
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        """Finalizar torneo manualmente"""
        tournament = self.get_object()
        
        if tournament.status == 'completed':
            return Response(
                {'error': 'El torneo ya está finalizado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tournament.status = 'completed'
        tournament.finished_at = timezone.now()
        tournament.save()
        
        # Determinar campeón si no existe
        champion = tournament.teams.filter(bracket_status='champion').first()
        if not champion:
            # Buscar equipo con más puntos
            champion = tournament.teams.order_by('-points', '-wins').first()
            if champion:
                champion.bracket_status = 'champion'
                champion.save()
        
        # Mensaje de finalización
        from chat.models import ChatMessage
        if champion:
            ChatMessage.create_celebration_message(
                tournament, 
                champion.name, 
                'champion'
            )
        
        ChatMessage.create_system_message(
            tournament,
            f"🏁 El torneo {tournament.name} ha finalizado. ¡Gracias a todos por participar!"
        )
        
        return Response({
            'message': 'Torneo finalizado exitosamente',
            'champion': champion.name if champion else None,
            'tournament': TournamentSerializer(tournament).data
        })
