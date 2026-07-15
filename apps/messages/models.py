import uuid
from django.db import models
from django.conf import settings


class Thread(models.Model):
    """A conversation thread between multiple participants."""
    THREAD_TYPE_CHOICES = [
        ('campaign_chat', 'Campaign Chat'),
        ('support', 'Support'),
        ('direct', 'Direct'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread_type = models.CharField(max_length=20, choices=THREAD_TYPE_CHOICES, default='direct')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='threads')
    campaign = models.ForeignKey(
        'campaigns.Campaign', on_delete=models.SET_NULL, null=True, blank=True, related_name='threads'
    )
    subject = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'threads'
        ordering = ['-updated_at']

    def __str__(self):
        return f'Thread {self.id} ({self.thread_type})'


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField()
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']

    def __str__(self):
        return f'Message {self.id} in thread {self.thread_id}'
