from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, 
    AssignTournamentSerializer, TournamentAssignmentSerializer
)
from .models import PlayerProfile, User, UserTournamentAssignment
from .permissions import IsAdminUser

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(UserSerializer(request.user).data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_players(request):
    players = User.objects.filter(user_type='player').select_related('profile')
    return Response(UserSerializer(players, many=True).data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def assign_tournament(request):
    serializer = AssignTournamentSerializer(data=request.data)
    if serializer.is_valid():
        user_id = serializer.validated_data['user_id']
        tournament_id = serializer.validated_data['tournament_id']
        assignment_status = serializer.validated_data['status']
        
        try:
            user = User.objects.get(id=user_id, user_type='player')
            from tournaments.models import Tournament
            tournament = Tournament.objects.get(id=tournament_id)
            
            assignment, created = UserTournamentAssignment.objects.get_or_create(
                user=user,
                tournament=tournament,
                defaults={
                    'status': assignment_status,
                    'assigned_by': request.user
                }
            )
            
            if not created:
                assignment.status = assignment_status
                assignment.assigned_by = request.user
                assignment.save()
            
            return Response({
                'message': 'Asignación exitosa',
                'assignment': TournamentAssignmentSerializer(assignment).data
            })
            
        except User.DoesNotExist:
            return Response({'error': 'Jugador no encontrado'}, status=404)
        except Tournament.DoesNotExist:
            return Response({'error': 'Torneo no encontrado'}, status=404)
    
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def remove_tournament_assignment(request, user_id, tournament_id):
    try:
        assignment = UserTournamentAssignment.objects.get(
            user_id=user_id,
            tournament_id=tournament_id
        )
        assignment.delete()
        return Response({'message': 'Asignación eliminada'})
    except UserTournamentAssignment.DoesNotExist:
        return Response({'error': 'Asignación no encontrada'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_tournaments(request):
    if request.user.is_admin():
        from tournaments.models import Tournament
        tournaments = Tournament.objects.all()
    else:
        assignments = UserTournamentAssignment.objects.filter(
            user=request.user,
            status__in=['confirmed', 'active']
        ).select_related('tournament')
        tournaments = [a.tournament for a in assignments]
    
    from tournaments.serializers import TournamentSerializer
    return Response(TournamentSerializer(tournaments, many=True).data)

@api_view(['GET'])
@permission_classes([AllowAny])
def game_types(request):
    return Response({
        'game_types': [
            {'value': 'fighting', 'label': '🥊 Juegos de Pelea'},
            {'value': 'racing', 'label': '🏎️ Carreras'},
            {'value': 'sports', 'label': '⚽ Deportes'},
            {'value': 'shooter', 'label': '🔫 Disparos'},
            {'value': 'strategy', 'label': '🧠 Estrategia'},
            {'value': 'rpg', 'label': '🗡️ RPG'},
            {'value': 'platform', 'label': '🏃 Plataformas'},
            {'value': 'puzzle', 'label': '🧩 Puzzle'},
            {'value': 'arcade', 'label': '🕹️ Arcade'},
            {'value': 'other', 'label': '🎮 Otros'},
        ]
    })
