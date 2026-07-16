from rest_framework import viewsets, permissions
from .models import Booking
from .serializers import BookingSerializer
from django.db.models import Q

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff and self.request.query_params.get('all') == 'true':
            return Booking.objects.all()
        
        # Space owner sees bookings for their spaces.
        return Booking.objects.filter(
            Q(advertiser=user) | Q(space__owner=user)
        )

    def perform_create(self, serializer):
        serializer.save(advertiser=self.request.user)

    def perform_update(self, serializer):
        from apps.jobs.models import PrintJob
        from apps.users.models import CustomUser
        
        instance = serializer.save()
        if instance.status in ['confirmed', 'paid'] and not hasattr(instance, 'print_job'):
            # Find a printer (e.g. first available)
            printer = CustomUser.objects.filter(role='printer').first()
            PrintJob.objects.create(
                booking=instance,
                printer=printer,
                status='JOB_PENDING_ACCEPT',
                material='Standard Vinyl',
                size='24x36',
                quantity=1
            )

