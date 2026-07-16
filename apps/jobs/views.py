from rest_framework import viewsets, permissions
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
        # Printer can see jobs assigned to them
        # Space owner can see jobs for their spaces?
        # Let's filter by printer for now
        return PrintJob.objects.filter(printer=user)
