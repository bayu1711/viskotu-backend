from rest_framework import serializers
from .models import Thread, Message
from apps.users.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender_detail = UserSerializer(source='sender', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'thread', 'sender', 'sender_detail', 'body', 'attachment', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']

class ThreadSerializer(serializers.ModelSerializer):
    participants_detail = UserSerializer(source='participants', many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ['id', 'thread_type', 'participants', 'participants_detail', 'campaign', 'subject', 'created_at', 'updated_at', 'last_message', 'unread_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if msg:
            return MessageSerializer(msg).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.messages.exclude(sender=request.user).filter(is_read=False).count()
        return 0
