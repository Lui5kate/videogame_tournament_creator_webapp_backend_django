from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Match, BracketGenerator
from .serializers import (
    MatchSerializer, 
    MatchCreateSerializer,
    DeclareWinnerSerializer,
    BracketVisualizationSerializer
)
from tournaments.models import Tournament

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MatchCreateSerializer
        return MatchSerializer
    
    def get_queryset(self):
        queryset = Match.objects.all()
        tournament_id = self.request.query_params.get('tournament', None)
        bracket_type = self.request.query_params.get('bracket_type', None)
        match_status = self.request.query_params.get('status', None)
        
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        if bracket_type:
            queryset = queryset.filter(bracket_type=bracket_type)
        if match_status:
            queryset = queryset.filter(status=match_status)
        
        return queryset.order_by('bracket_type', 'round_number', 'match_number')
    
    @action(detail=False, methods=['post'])
    def declare_winner(self, request):
        """Declarar ganador de una partida"""
        serializer = DeclareWinnerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        match = serializer.validated_data['match']
        winner = serializer.validated_data['winner']
        
        # Declarar ganador
        try:
            match.declare_winner(winner)
            
            # Mensajes del sistema
            from chat.models import ChatMessage
            loser = match.team2 if winner == match.team1 else match.team1
            
            # Mensaje de victoria
            ChatMessage.create_celebration_message(
                match.tournament,
                winner.name,
                'victory'
            )
            
            # Verificar si el perdedor fue eliminado
            if loser.bracket_status == 'eliminated':
                ChatMessage.create_celebration_message(
                    match.tournament,
                    loser.name,
                    'elimination'
                )
            
            # Verificar si hay un campeón
            if winner.bracket_status == 'champion':
                ChatMessage.create_celebration_message(
                    match.tournament,
                    winner.name,
                    'champion'
                )
                
                # Finalizar torneo automáticamente
                match.tournament.status = 'completed'
                match.tournament.save()
            
            # Ejecutar limpieza automática después de cada partida
            from .services import MatchService
            MatchService.cleanup_impossible_matches(match.tournament)
            
            return Response({
                'message': f'{winner.name} ha ganado la partida',
                'match': MatchSerializer(match).data,
                'winner': {
                    'name': winner.name,
                    'points': winner.points,
                    'wins': winner.wins,
                    'bracket_status': winner.bracket_status
                },
                'loser': {
                    'name': loser.name,
                    'points': loser.points,
                    'losses': loser.losses,
                    'bracket_status': loser.bracket_status
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al declarar ganador: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_brackets(self, request):
        """Generar brackets para un torneo"""
        tournament_id = request.data.get('tournament_id')
        
        if not tournament_id:
            return Response(
                {'error': 'Se requiere tournament_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Torneo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if tournament.teams.count() < 2:
            return Response(
                {'error': 'Se necesitan al menos 2 equipos para generar brackets'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Limpiar brackets existentes si los hay
        tournament.matches.all().delete()
        
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
        
        # Obtener brackets generados
        matches = tournament.matches.all()
        serializer = MatchSerializer(matches, many=True)
        
        return Response({
            'message': 'Brackets generados exitosamente',
            'tournament_type': tournament.tournament_type,
            'total_matches': matches.count(),
            'matches': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def visualization(self, request):
        """Obtener datos para visualización de brackets"""
        tournament_id = request.query_params.get('tournament_id')
        
        if not tournament_id:
            return Response(
                {'error': 'Se requiere tournament_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Torneo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Preparar datos para visualización
        data = {'tournament_id': tournament_id}
        serializer = BracketVisualizationSerializer(data)
        
        return Response({
            'tournament': {
                'id': tournament.id,
                'name': tournament.name,
                'type': tournament.tournament_type,
                'status': tournament.status
            },
            'brackets': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def start_match(self, request, pk=None):
        """Marcar partida como en progreso"""
        match = self.get_object()
        
        if match.status != 'pending':
            return Response(
                {'error': 'La partida no está en estado pendiente'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not match.is_ready_to_play:
            return Response(
                {'error': 'La partida no está lista para jugar (faltan equipos)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        match.status = 'in_progress'
        match.save()
        
        # Mensaje del sistema
        from chat.models import ChatMessage
        ChatMessage.create_system_message(
            match.tournament,
            f"🎮 ¡Partida iniciada! {match.team1.name} vs {match.team2.name}"
        )
        
        return Response({
            'message': 'Partida iniciada',
            'match': MatchSerializer(match).data
        })
    
    @action(detail=False, methods=['get'])
    def next_matches(self, request):
        """Obtener próximas partidas a jugar"""
        tournament_id = request.query_params.get('tournament_id')
        
        if not tournament_id:
            return Response(
                {'error': 'Se requiere tournament_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar partidas listas para jugar
        next_matches = Match.objects.filter(
            tournament_id=tournament_id,
            status='pending'
        ).filter(
            team1__isnull=False,
            team2__isnull=False
        ).order_by('bracket_type', 'round_number', 'match_number')[:5]
        
        serializer = MatchSerializer(next_matches, many=True)
        
        return Response({
            'next_matches': serializer.data,
            'count': next_matches.count()
        })
    
    @action(detail=False, methods=['get'])
    def get_active_round(self, request):
        """Obtener el round activo que debe jugarse siguiente"""
        tournament_id = request.query_params.get('tournament_id')
        
        if not tournament_id:
            return Response(
                {'error': 'Se requiere tournament_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Torneo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Determinar el siguiente round que debe jugarse
        active_round = self._determine_active_round(tournament)
        
        return Response({
            'active_round': active_round,
            'tournament_id': tournament_id
        })
    
    def _determine_active_round(self, tournament):
        """Determinar cuál es el round activo que debe jugarse"""
        # Orden: WR1 → LR1 → WR2 → LR2 → WR3 → LR3 → WR4 → LR4 → GF → RF
        
        # Verificar Winners rounds en orden
        max_winners_round = Match.objects.filter(
            tournament=tournament,
            bracket_type='winners'
        ).aggregate(max_round=models.Max('round_number'))['max_round'] or 0
        
        for round_num in range(1, max_winners_round + 1):
            # Verificar Winners Round
            winners_pending = Match.objects.filter(
                tournament=tournament,
                bracket_type='winners',
                round_number=round_num,
                status='pending',
                team1__isnull=False,
                team2__isnull=False
            ).exists()
            
            if winners_pending:
                return {'bracket_type': 'winners', 'round_number': round_num}
            
            # Verificar Losers Round correspondiente
            losers_pending = Match.objects.filter(
                tournament=tournament,
                bracket_type='losers',
                round_number=round_num,
                status='pending',
                team1__isnull=False,
                team2__isnull=False
            ).exists()
            
            if losers_pending:
                return {'bracket_type': 'losers', 'round_number': round_num}
        
        # Verificar finales
        grand_final_pending = Match.objects.filter(
            tournament=tournament,
            bracket_type='grand_final',
            status='pending',
            team1__isnull=False,
            team2__isnull=False
        ).exists()
        
        if grand_final_pending:
            return {'bracket_type': 'grand_final', 'round_number': 1}
        
        final_reset_pending = Match.objects.filter(
            tournament=tournament,
            bracket_type='final_reset',
            status='pending',
            team1__isnull=False,
            team2__isnull=False
        ).exists()
        
        if final_reset_pending:
            return {'bracket_type': 'final_reset', 'round_number': 1}
        
        return None
    
    @action(detail=False, methods=['post'])
    def cleanup_tournament(self, request):
        """Limpiar partidas imposibles y finalizar torneo si es necesario"""
        tournament_id = request.data.get('tournament_id')
        
        if not tournament_id:
            return Response(
                {'error': 'Se requiere tournament_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Torneo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Ejecutar limpieza inteligente
        from .services import MatchService
        orphaned_count = MatchService.cleanup_impossible_matches(tournament)
        
        # Obtener estado actualizado
        tournament.refresh_from_db()
        pending_matches = Match.objects.filter(tournament=tournament, status='pending').count()
        
        return Response({
            'message': 'Limpieza ejecutada exitosamente',
            'orphaned_teams_advanced': orphaned_count,
            'tournament_status': tournament.status,
            'pending_matches': pending_matches
        })
    
    @action(detail=True, methods=['post'])
    def manual_advance(self, request, pk=None):
        """Avanzar equipo manualmente (para partidas huérfanas)"""
        match = self.get_object()
        
        try:
            from .services import MatchService
            MatchService.manual_advance_team(match.id)
            
            # Mensaje del sistema
            from chat.models import ChatMessage
            ChatMessage.create_system_message(
                match.tournament,
                f"⚡ {match.team1.name} avanza automáticamente por BYE"
            )
            
            return Response({
                'message': f'{match.team1.name} avanzado exitosamente',
                'match': MatchSerializer(match).data
            })
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al avanzar equipo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def advanceable_matches(self, request):
        """Obtener partidas elegibles para avance manual"""
        tournament_id = request.query_params.get('tournament_id')
        
        if not tournament_id:
            return Response(
                {'error': 'Se requiere tournament_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Torneo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from .services import MatchService
        advanceable = MatchService.get_advanceable_matches(tournament)
        serializer = MatchSerializer(advanceable, many=True)
        
        return Response({
            'advanceable_matches': serializer.data,
            'count': advanceable.count()
        })
