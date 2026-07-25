from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
import requests
import csv
import os
import hashlib
from django.http import HttpResponse
from django.db.models import Sum
from .models import Payment, Payout
from .serializers import PaymentSerializer, PayoutSerializer
from apps.campaigns.models import Campaign # Assuming Campaign is here, if needed for custom_1, or maybe we just pass custom_1 from frontend?
from apps.core.services.email_service import send_campaign_funded_email, send_payout_requested_email
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
        gateway = request.data.get('gateway', 'paddle')
        campaign_id = request.data.get('campaign_id', '')
        
        if not total_cost:
            return Response({'error': 'total_cost is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if gateway == 'payhere':
            import uuid
            order_id = str(uuid.uuid4())
            amount_lkr = float(total_cost) * 300
            amount_formatted = "{:.2f}".format(amount_lkr)
            currency = 'LKR'
            
            merchant_id = os.environ.get('PAYHERE_MERCHANT_ID', getattr(settings, 'PAYHERE_MERCHANT_ID', ''))
            merchant_secret = os.environ.get('PAYHERE_SECRET', getattr(settings, 'PAYHERE_SECRET', ''))
            
            # Generate the PayHere MD5 hash
            # md5sig = md5( merchant_id + order_id + amount_formatted_to_2_decimals + currency + md5(merchant_secret).upper() ).upper()
            
            hashed_secret = hashlib.md5(merchant_secret.encode('utf-8')).hexdigest().upper()
            hash_string = f"{merchant_id}{order_id}{amount_formatted}{currency}{hashed_secret}"
            md5sig = hashlib.md5(hash_string.encode('utf-8')).hexdigest().upper()
            
            payhere_payload = {
                'sandbox': True,
                'merchant_id': merchant_id,
                'return_url': request.build_absolute_uri('/') + 'return',
                'cancel_url': request.build_absolute_uri('/') + 'cancel',
                'notify_url': request.build_absolute_uri('/api/payments/payhere-webhook/'),
                'order_id': order_id,
                'items': 'Custom Ad Campaign',
                'currency': currency,
                'amount': amount_formatted,
                'hash': md5sig,
                'custom_1': campaign_id,
                'first_name': getattr(request.user, 'first_name', ''),
                'last_name': getattr(request.user, 'last_name', ''),
                'email': getattr(request.user, 'email', ''),
                'phone': getattr(request.user, 'phone', ''),
                'address': '',
                'city': '',
                'country': 'Sri Lanka'
            }
            return Response({
                'gateway': 'payhere',
                'payhere_payload': payhere_payload
            })
            
        # Paddle logic
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
            }],
            'custom_data': {'campaign_id': campaign_id}
        }
        
        try:
            response = requests.post('https://api.paddle.com/transactions', headers=headers, json=payload)
            response.raise_for_status()
            data = response.json().get('data', {})
            return Response({'gateway': 'paddle', 'transaction_id': data.get('id')})
        except requests.RequestException as e:
            return Response({'error': 'Failed to create transaction', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='payhere-webhook', permission_classes=[permissions.AllowAny])
    def payhere_webhook(self, request):
        merchant_id = request.data.get('merchant_id')
        order_id = request.data.get('order_id')
        payhere_amount = request.data.get('payhere_amount')
        payhere_currency = request.data.get('payhere_currency')
        status_code = request.data.get('status_code')
        md5sig = request.data.get('md5sig')
        custom_1 = request.data.get('custom_1')
        
        my_merchant_id = os.environ.get('PAYHERE_MERCHANT_ID', getattr(settings, 'PAYHERE_MERCHANT_ID', ''))
        merchant_secret = os.environ.get('PAYHERE_SECRET', getattr(settings, 'PAYHERE_SECRET', ''))
        
        hashed_secret = hashlib.md5(merchant_secret.encode('utf-8')).hexdigest().upper()
        local_hash_string = f"{my_merchant_id}{order_id}{payhere_amount}{payhere_currency}{status_code}{hashed_secret}"
        local_md5sig = hashlib.md5(local_hash_string.encode('utf-8')).hexdigest().upper()
        
        if local_md5sig == md5sig:
            if status_code == '2':
                # Payment success
                if custom_1:
                    try:
                        from apps.campaigns.models import Campaign
                        campaign = Campaign.objects.get(id=custom_1)
                        campaign.status = 'funded'
                        campaign.save()
                        # Send email
                        advertiser = getattr(campaign, 'advertiser', getattr(campaign, 'user', getattr(campaign, 'owner', None)))
                        if advertiser:
                            send_campaign_funded_email(campaign, advertiser)
                    except (ImportError, Exception):
                        pass
                
                return Response({'status': 'ok'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'failed or pending'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

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
            
            for payout in payouts:
                send_payout_requested_email(payout, request.user)
                
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

