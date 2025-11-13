from django.urls import path
from . import views

urlpatterns = [
    path('messages/', views.messages_view, name='messages'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('messages/<int:pk>/delete/', views.delete_message, name='delete_message'),
    path('messages/system-message/', views.system_message, name='system_message'),
    path('messages/recent/', views.recent_messages, name='recent_messages'),
    
    path('rooms/', views.rooms_view, name='rooms'),
    path('rooms/by-tournament/', views.room_by_tournament, name='room_by_tournament'),
]
