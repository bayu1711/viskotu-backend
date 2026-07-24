from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Payment, Payout
from .serializers import PaymentSerializer, PayoutSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff and self.request.query_params.get('all') == 'true':
            return Payment.objects.all()
        return Payment.objects.filter(payer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            payer=self.request.user, 
            status='pending'
        )

    @action(detail=False, methods=['post'], url_path='paddle-webhook', permission_classes=[permissions.AllowAny])
    def paddle_webhook(self, request):
        if request.data.get('alert_name') == 'payment_succeeded':
            passthrough = request.data.get('passthrough')
            if passthrough:
                try:
                    payment = Payment.objects.get(id=passthrough)
                    payment.status = 'succeeded'
                    transaction_id = request.data.get('transaction_id') or request.data.get('p_order_id')
                    if transaction_id:
                        payment.paddle_transaction_id = str(transaction_id)
                    payment.save()
                except Payment.DoesNotExist:
                    pass
        return Response({'status': 'ok'})

class PayoutViewSet(viewsets.ModelViewSet):
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff and self.request.query_params.get('all') == 'true':
            return Payout.objects.all()
        return Payout.objects.filter(recipient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            recipient=self.request.user, 
            status='pending'
        )
