from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PayoutViewSet

router = DefaultRouter()
router.register(r'transactions', PaymentViewSet, basename='payment')
router.register(r'payouts', PayoutViewSet, basename='payout')

urlpatterns = [
    path('', include(router.urls)),
]
