from rest_framework import viewsets, status
from rest_framework.decorators import action
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

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ChatMessageCreateSerializer
        return ChatMessageSerializer
    
    def get_queryset(self):
        queryset = ChatMessage.objects.all()
        tournament_id = self.request.query_params.get('tournament', None)
        message_type = self.request.query_params.get('type', None)
        
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        if message_type:
            queryset = queryset.filter(message_type=message_type)
        
        # Limitar a los últimos 100 mensajes por defecto
        limit = int(self.request.query_params.get('limit', 100))
        return queryset.order_by('-created_at')[:limit]
    
    def create(self, request, *args, **kwargs):
        """Crear nuevo mensaje de chat"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obtener IP del usuario para moderación
        ip_address = self.get_client_ip(request)
        
        message = serializer.save(
            ip_address=ip_address,
            message_type='user'
        )
        
        # Limpiar mensajes antiguos si es necesario
        try:
            chat_room = message.tournament.chat_room
            chat_room.clean_old_messages()
        except ChatRoom.DoesNotExist:
            # Crear sala de chat si no existe
            ChatRoom.objects.create(tournament=message.tournament)
        
        return Response(
            ChatMessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )
    
    def get_client_ip(self, request):
        """Obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=False, methods=['post'])
    def system_message(self, request):
        """Crear mensaje del sistema"""
        serializer = SystemMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = serializer.save()
        
        return Response(
            ChatMessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Obtener mensajes recientes de un torneo"""
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
        
        # Obtener mensajes recientes
        limit = int(request.query_params.get('limit', 50))
        messages = tournament.chat_messages.order_by('-created_at')[:limit]
        
        # Invertir orden para mostrar más antiguos primero
        messages = list(reversed(messages))
        
        serializer = ChatMessageSerializer(messages, many=True)
        
        return Response({
            'tournament': {
                'id': tournament.id,
                'name': tournament.name,
                'status': tournament.status
            },
            'messages': serializer.data,
            'total_messages': tournament.chat_messages.count()
        })

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    
    def get_queryset(self):
        queryset = ChatRoom.objects.all()
        tournament_id = self.request.query_params.get('tournament', None)
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset.select_related('tournament')
    
    @action(detail=False, methods=['get'])
    def by_tournament(self, request):
        """Obtener sala de chat por torneo"""
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
        
        # Obtener o crear sala de chat
        chat_room, created = ChatRoom.objects.get_or_create(
            tournament=tournament,
            defaults={'is_active': True}
        )
        
        serializer = ChatRoomSerializer(chat_room)
        
        return Response({
            'chat_room': serializer.data,
            'created': created
        })
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Activar/desactivar chat"""
        chat_room = self.get_object()
        
        chat_room.is_active = not chat_room.is_active
        chat_room.save()
        
        # Mensaje del sistema
        status_msg = "activado" if chat_room.is_active else "desactivado"
        ChatMessage.create_system_message(
            chat_room.tournament,
            f"💬 El chat ha sido {status_msg}"
        )
        
        return Response({
            'message': f'Chat {status_msg}',
            'is_active': chat_room.is_active
        })
    
    @action(detail=True, methods=['post'])
    def clear_messages(self, request, pk=None):
        """Limpiar todos los mensajes del chat"""
        chat_room = self.get_object()
        
        # Eliminar todos los mensajes
        deleted_count = chat_room.tournament.chat_messages.count()
        chat_room.tournament.chat_messages.all().delete()
        
        # Mensaje de confirmación
        ChatMessage.create_system_message(
            chat_room.tournament,
            f"🧹 Chat limpiado. Se eliminaron {deleted_count} mensajes"
        )
        
        return Response({
            'message': f'Se eliminaron {deleted_count} mensajes',
            'deleted_count': deleted_count
        })
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Obtener estadísticas del chat"""
        chat_room = self.get_object()
        
        messages = chat_room.tournament.chat_messages.all()
        
        stats = {
            'total_messages': messages.count(),
            'user_messages': messages.filter(message_type='user').count(),
            'system_messages': messages.filter(message_type='system').count(),
            'celebration_messages': messages.filter(message_type='celebration').count(),
            'unique_users': messages.filter(message_type='user').values('username').distinct().count(),
            'is_active': chat_room.is_active,
            'max_messages': chat_room.max_messages,
            'created_at': chat_room.created_at
        }
        
        return Response(stats)
