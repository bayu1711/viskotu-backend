from rest_framework import viewsets, permissions
from .models import Booking
from .serializers import BookingSerializer
from django.db.models import Q

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(
            Q(advertiser=user) | Q(space__owner=user)
        )

    def perform_create(self, serializer):
        serializer.save(advertiser=self.request.user)
