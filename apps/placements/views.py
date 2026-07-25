from rest_framework import viewsets, permissions
from .models import AdPlacement
from .serializers import AdPlacementSerializer
from django.db.models import Q

class AdPlacementViewSet(viewsets.ModelViewSet):
    serializer_class = AdPlacementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff and self.request.query_params.get('all') == 'true':
            return AdPlacement.objects.all()
        
        # Space owner sees ad_placements for their spaces.
        return AdPlacement.objects.filter(
            Q(advertiser=user) | Q(space__owner=user)
        )

    def perform_create(self, serializer):
        serializer.save(advertiser=self.request.user)

    def perform_update(self, serializer):
        from apps.jobs.models import PrintJob
        from apps.core.services.email_service import send_job_assigned_email
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        instance = serializer.save()
        if instance.status in ['confirmed', 'paid'] and not hasattr(instance, 'print_job'):
            # Find a production_partner (e.g. first available)
            production_partner = User.objects.filter(role='production-partner').first()
            job = PrintJob.objects.create(
                ad_placement=instance,
                production_partner=production_partner,
                status='JOB_PENDING_ACCEPT',
                material='Standard Vinyl',
                size='24x36',
                quantity=1
            )
            if production_partner:
                send_job_assigned_email(job, production_partner)

