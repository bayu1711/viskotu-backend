from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import PrintJob
from .serializers import PrintJobSerializer
from django.db.models import Q

class PrintJobViewSet(viewsets.ModelViewSet):
    serializer_class = PrintJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff and self.request.query_params.get('all') == 'true':
            return PrintJob.objects.all()
        return PrintJob.objects.filter(Q(production_partner=user) | Q(ad_placement__advertiser=user) | Q(ad_placement__space__owner=user)).distinct()

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        job = self.get_object()
        if job.production_partner != request.user and not request.user.is_staff:
            return Response({'detail': 'Not authorized to accept this job.'}, status=status.HTTP_403_FORBIDDEN)
        if job.status != 'JOB_PENDING_ACCEPT':
            return Response({'detail': f'Cannot accept job with status {job.status}.'}, status=status.HTTP_400_BAD_REQUEST)
        job.status = 'JOB_PREP'
        job.accepted_at = timezone.now()
        job.save(update_fields=['status', 'accepted_at', 'updated_at'])
        return Response(PrintJobSerializer(job, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        job = self.get_object()
        if job.production_partner != request.user and not request.user.is_staff:
            return Response({'detail': 'Not authorized to reject this job.'}, status=status.HTTP_403_FORBIDDEN)
        if job.status != 'JOB_PENDING_ACCEPT':
            return Response({'detail': f'Cannot reject job with status {job.status}.'}, status=status.HTTP_400_BAD_REQUEST)
        job.reroute_to_next_production_partner()
        return Response(PrintJobSerializer(job, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        job = self.get_object()
        if job.production_partner != request.user and not request.user.is_staff:
            return Response({'detail': 'Not authorized to update this job.'}, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        valid_statuses = ['JOB_PREP', 'JOB_PRINTING', 'JOB_QA', 'JOB_SHIPPING', 'JOB_COMPLETED']
        if new_status not in valid_statuses:
            return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
            
        job.status = new_status
        if new_status == 'JOB_COMPLETED' and not job.completed_at:
            job.completed_at = timezone.now()
            job.save(update_fields=['status', 'completed_at', 'updated_at'])
        else:
            job.save(update_fields=['status', 'updated_at'])
        return Response(PrintJobSerializer(job, context={'request': request}).data)
