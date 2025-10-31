from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatMessageViewSet, ChatRoomViewSet

router = DefaultRouter()
router.register(r'messages', ChatMessageViewSet)
router.register(r'rooms', ChatRoomViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
