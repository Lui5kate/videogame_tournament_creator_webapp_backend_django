from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Game, TournamentGame
from .serializers import (
    GameSerializer, 
    TournamentGameSerializer,
    PredefinedGamesSerializer
)

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.filter(is_active=True)
    serializer_class = GameSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        queryset = Game.objects.filter(is_active=True)
        
        # Filtrar por tipo
        game_type = self.request.query_params.get('type', None)
        if game_type == 'predefined':
            queryset = queryset.filter(is_predefined=True)
        elif game_type == 'custom':
            queryset = queryset.filter(is_predefined=False)
        
        return queryset.order_by('is_predefined', 'name')
    
    def create(self, request, *args, **kwargs):
        """Crear juego personalizado"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Los juegos creados por usuarios no son predefinidos
        game = serializer.save(is_predefined=False)
        
        return Response(
            GameSerializer(game).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def predefined(self, request):
        """Obtener lista de juegos predefinidos disponibles"""
        # Crear juegos predefinidos si no existen
        Game.create_predefined_games()
        
        # Obtener juegos predefinidos
        predefined_games = Game.objects.filter(is_predefined=True, is_active=True)
        serializer = GameSerializer(predefined_games, many=True)
        
        return Response({
            'predefined_games': serializer.data,
            'available_templates': PredefinedGamesSerializer({}).data
        })
    
    @action(detail=False, methods=['post'])
    def create_from_template(self, request):
        """Crear juego desde plantilla predefinida"""
        template_key = request.data.get('template_key')
        
        if not template_key:
            return Response(
                {'error': 'Se requiere template_key'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Buscar en plantillas predefinidas
        template_found = None
        for game_key, game_display in Game.PREDEFINED_GAMES:
            if game_key == template_key:
                template_found = game_display
                break
        
        if not template_found:
            return Response(
                {'error': 'Plantilla no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Extraer emoji y nombre
        emoji = template_found.split(' ')[0]
        name = ' '.join(template_found.split(' ')[1:])
        
        # Crear o obtener juego
        game, created = Game.objects.get_or_create(
            name=name,
            defaults={
                'emoji': emoji,
                'is_predefined': True,
                'description': f'Juego arcade clásico: {name}',
                'is_active': True
            }
        )
        
        return Response(
            GameSerializer(game).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Subir imagen personalizada para el juego"""
        game = self.get_object()
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No se proporcionó ninguna imagen'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        game.image = request.FILES['image']
        game.save()
        
        return Response({
            'message': 'Imagen subida exitosamente',
            'image_url': game.image.url if game.image else None
        })

class TournamentGameViewSet(viewsets.ModelViewSet):
    queryset = TournamentGame.objects.all()
    serializer_class = TournamentGameSerializer
    
    def get_queryset(self):
        queryset = TournamentGame.objects.all()
        tournament_id = self.request.query_params.get('tournament', None)
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset.select_related('game', 'tournament')
    
    @action(detail=False, methods=['post'])
    def assign_to_tournament(self, request):
        """Asignar juegos a un torneo"""
        tournament_id = request.data.get('tournament_id')
        game_ids = request.data.get('game_ids', [])
        
        if not tournament_id or not game_ids:
            return Response(
                {'error': 'Se requieren tournament_id y game_ids'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el torneo existe
        from tournaments.models import Tournament
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response(
                {'error': 'Torneo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Asignar juegos
        assigned_games = []
        for game_id in game_ids:
            try:
                game = Game.objects.get(id=game_id, is_active=True)
                tournament_game, created = TournamentGame.objects.get_or_create(
                    tournament=tournament,
                    game=game,
                    defaults={'is_selected': True}
                )
                assigned_games.append(tournament_game)
            except Game.DoesNotExist:
                continue
        
        serializer = TournamentGameSerializer(assigned_games, many=True)
        return Response({
            'message': f'{len(assigned_games)} juegos asignados al torneo',
            'assigned_games': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def tournament_games(self, request):
        """Obtener juegos asignados a un torneo específico"""
        tournament_id = request.query_params.get('tournament_id')
        
        if not tournament_id:
            return Response(
                {'error': 'Se requiere tournament_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tournament_games = TournamentGame.objects.filter(
            tournament_id=tournament_id,
            is_selected=True
        ).select_related('game')
        
        serializer = TournamentGameSerializer(tournament_games, many=True)
        return Response(serializer.data)
