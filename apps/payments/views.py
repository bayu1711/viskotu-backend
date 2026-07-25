from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
import requests
import csv
from django.http import HttpResponse
from django.db.models import Sum
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

    @action(detail=False, methods=['post'], url_path='create-transaction')
    def create_transaction(self, request):
        total_cost = request.data.get('total_cost')
        if not total_cost:
            return Response({'error': 'total_cost is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        headers = {
            'Authorization': f'Bearer {settings.PADDLE_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'items': [{
                "price": {
                    "description": "Custom Ad Campaign", 
                    "product_id": settings.PADDLE_PRODUCT_ID, 
                    "unit_price": {
                        "amount": int(float(total_cost) * 100), 
                        "currency_code": "USD"
                    }
                }, 
                "quantity": 1
            }]
        }
        
        try:
            response = requests.post('https://api.paddle.com/transactions', headers=headers, json=payload)
            response.raise_for_status()
            data = response.json().get('data', {})
            return Response({'transaction_id': data.get('id')})
        except requests.RequestException as e:
            return Response({'error': 'Failed to create transaction', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=False, methods=['post'], url_path='request-withdrawal')
    def request_withdrawal(self, request):
        payouts = Payout.objects.filter(recipient=request.user, status='pending')
        total_amount = payouts.aggregate(Sum('amount'))['amount__sum'] or 0
        if total_amount >= 50:
            payouts.update(status='requested')
            return Response({'status': 'success', 'message': f'Withdrawal requested for ${total_amount}'})
        return Response({'error': 'Minimum withdrawal threshold is $50'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='export-csv', permission_classes=[permissions.IsAdminUser])
    def export_csv(self, request):
        payouts = Payout.objects.filter(status='requested').select_related('recipient')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payouts.csv"'
        writer = csv.writer(response)
        writer.writerow(['Recipient Name', 'Email', 'Amount', 'Currency'])
        for payout in payouts:
            name = getattr(payout.recipient, 'name', '') or f"{getattr(payout.recipient, 'first_name', '')} {getattr(payout.recipient, 'last_name', '')}".strip()
            writer.writerow([name, payout.recipient.email, payout.amount, payout.currency])
        return response

    @action(detail=False, methods=['post'], url_path='process-wise', permission_classes=[permissions.IsAdminUser])
    def process_wise(self, request):
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response({'error': 'No user_ids provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        for uid in user_ids:
            payouts = Payout.objects.filter(recipient_id=uid, status='requested')
            total = payouts.aggregate(Sum('amount'))['amount__sum'] or 0
            if total > 0:
                # Mock Wise API call
                try:
                    # requests.post('https://api.sandbox.transferwise.tech/v1/transfers', ...)
                    pass
                except Exception:
                    pass
                payouts.update(status='processing')
        return Response({'status': 'success'})

    @action(detail=False, methods=['post'], url_path='mark-paid', permission_classes=[permissions.IsAdminUser])
    def mark_paid(self, request):
        payout_ids = request.data.get('payout_ids', [])
        if not payout_ids:
            return Response({'error': 'No payout_ids provided'}, status=status.HTTP_400_BAD_REQUEST)
        Payout.objects.filter(id__in=payout_ids).update(status='paid')
        return Response({'status': 'success'})

