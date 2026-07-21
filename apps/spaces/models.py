import uuid
from django.db import models
from django.conf import settings


class Space(models.Model):
    CATEGORY_CHOICES = [
        ('vehicles', 'Vehicles'),
        ('gadgets', 'Gadgets'),
        ('fixed', 'Fixed Spaces'),
        ('wearables', 'Wearables'),
        ('events', 'Events'),
        ('animals', 'Animals'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ]

    FULFILLMENT_CHOICES = [
        ('managed_printing', 'Managed Printing'),
        ('self_fulfillment', 'Self Fulfillment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='spaces')

    # Basic info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    item_type = models.CharField(max_length=100, blank=True)

    # Location
    address = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Specifications
    width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    material = models.CharField(max_length=100, blank=True)
    min_dpi = models.IntegerField(default=300)
    accepted_formats = models.JSONField(default=list)

    # Pricing
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    billing_period = models.CharField(
        max_length=20,
        choices=[('hourly','Hourly'),('daily','Daily'),('weekly','Weekly'),('monthly','Monthly'),('yearly','Yearly')],
        default='daily'
    )
    min_booking_duration = models.IntegerField(default=1)
    bulk_discount_enabled = models.BooleanField(default=False)
    bulk_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Production
    fulfillment_type = models.CharField(max_length=20, choices=FULFILLMENT_CHOICES, default='managed_printing')
    self_fulfillment_reason = models.CharField(max_length=50, blank=True)
    print_partner_routing = models.CharField(max_length=20, blank=True)
    preferred_production_partner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='preferred_for_spaces'
    )

    # Lead times
    install_lead_days = models.IntegerField(default=2)
    production_lead_days = models.IntegerField(default=3)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    occupancy_rate = models.IntegerField(default=0)

    # Stats
    impressions_estimate = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'spaces'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.owner.email})'


class SpacePhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='spaces/photos/')
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'space_photos'
        ordering = ['order']


class SpaceAvailability(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    is_blocked = models.BooleanField(default=True)
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'space_availability'
        unique_together = ['space', 'date']
