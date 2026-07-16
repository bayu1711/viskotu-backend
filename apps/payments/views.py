from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Payment, Payout
from .serializers import PaymentSerializer, PayoutSerializer
import uuid

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff and self.request.query_params.get('all') == 'true':
            return Payment.objects.all()
        return Payment.objects.filter(payer=self.request.user)

    def perform_create(self, serializer):
        # Mocking Stripe integration by immediately marking as succeeded
        serializer.save(
            payer=self.request.user, 
            status='succeeded',
            stripe_payment_intent_id=f"pi_{uuid.uuid4().hex[:20]}",
            stripe_charge_id=f"ch_{uuid.uuid4().hex[:20]}"
        )

class PayoutViewSet(viewsets.ModelViewSet):
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff and self.request.query_params.get('all') == 'true':
            return Payout.objects.all()
        return Payout.objects.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        # Mocking Stripe payout
        serializer.save(
            recipient=self.request.user, 
            status='paid',
            stripe_payout_id=f"po_{uuid.uuid4().hex[:20]}"
        )
