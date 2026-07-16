from rest_framework import viewsets, permissions
from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer

class ThreadViewSet(viewsets.ModelViewSet):
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        thread = serializer.save()
        thread.participants.add(self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(thread__participants=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
