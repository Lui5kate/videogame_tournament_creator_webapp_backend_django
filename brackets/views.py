from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
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
