from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatMessage, ChatRoom
from .serializers import (
    ChatMessageSerializer, 
    ChatMessageCreateSerializer,
    ChatRoomSerializer, 
    SystemMessageSerializer
)
from tournaments.models import Tournament
from users.permissions import IsAdminUser

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def messages_view(request):
    if request.method == 'GET':
        tournament_id = request.GET.get('tournament')
        if tournament_id:
            tournament = get_object_or_404(Tournament, id=tournament_id)
            messages = ChatMessage.objects.filter(tournament=tournament).order_by('-created_at')[:50]
            messages = list(reversed(messages))  # Mostrar en orden cronológico
            serializer = ChatMessageSerializer(messages, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'tournament parameter required'}, status=400)
    
    elif request.method == 'POST':
        serializer = ChatMessageCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save()
            return Response(ChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def message_detail(request, pk):
    message = get_object_or_404(ChatMessage, pk=pk)
    serializer = ChatMessageSerializer(message)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_message(request, pk):
    message = get_object_or_404(ChatMessage, pk=pk)
    message.delete()
    return Response({'message': 'Mensaje eliminado'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def system_message(request):
    serializer = SystemMessageSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.save()
        return Response(ChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_messages(request):
    tournament_id = request.GET.get('tournament')
    limit = int(request.GET.get('limit', 20))
    
    if not tournament_id:
        return Response({'error': 'tournament parameter required'}, status=400)
    
    # Verificar acceso al torneo
    if not request.user.can_access_tournament(tournament_id):
        return Response({'error': 'No tienes acceso a este torneo'}, status=403)
    
    messages = ChatMessage.objects.filter(
        tournament_id=tournament_id
    ).order_by('-created_at')[:limit]
    
    messages = list(reversed(messages))
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)

# Views para ChatRoom
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def rooms_view(request):
    if request.method == 'GET':
        # Solo admins pueden ver todas las salas
        if request.user.is_admin():
            rooms = ChatRoom.objects.all()
        else:
            # Jugadores solo ven salas de sus torneos asignados
            tournament_ids = request.user.assigned_tournaments.values_list('id', flat=True)
            rooms = ChatRoom.objects.filter(tournament_id__in=tournament_ids)
        
        serializer = ChatRoomSerializer(rooms, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Solo admins pueden crear salas
        if not request.user.is_admin():
            return Response({'error': 'Solo administradores pueden crear salas'}, status=403)
        
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            return Response(ChatRoomSerializer(room).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_by_tournament(request):
    tournament_id = request.GET.get('tournament')
    if not tournament_id:
        return Response({'error': 'tournament parameter required'}, status=400)
    
    # Verificar acceso al torneo
    if not request.user.can_access_tournament(tournament_id):
        return Response({'error': 'No tienes acceso a este torneo'}, status=403)
    
    try:
        room = ChatRoom.objects.get(tournament_id=tournament_id)
        serializer = ChatRoomSerializer(room)
        return Response(serializer.data)
    except ChatRoom.DoesNotExist:
        # Crear sala automáticamente si no existe
        tournament = get_object_or_404(Tournament, id=tournament_id)
        room = ChatRoom.objects.create(tournament=tournament)
        serializer = ChatRoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
