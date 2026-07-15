import uuid
from django.db import models
from django.conf import settings


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('disputed', 'Disputed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advertiser = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings'
    )
    space = models.ForeignKey('spaces.Space', on_delete=models.CASCADE, related_name='bookings')
    campaign = models.ForeignKey(
        'campaigns.Campaign', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Payment
    payment_intent_id = models.CharField(max_length=200, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']

    def __str__(self):
        return f'Booking {self.id} — {self.advertiser.email} @ {self.space.name}'
