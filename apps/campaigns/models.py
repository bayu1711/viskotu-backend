import uuid
from django.db import models
from django.conf import settings


class Campaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_payment', 'Pending Payment'),
        ('paid', 'Paid'),
        ('in_production', 'In Production'),
        ('live_pending_pop', 'Live Pending POP'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('disputed', 'Disputed'),
        ('cancelled', 'Cancelled'),
    ]

    OBJECTIVE_CHOICES = [
        ('brand_awareness', 'Brand Awareness'),
        ('product_launch', 'Product Launch'),
        ('event_promotion', 'Event Promotion'),
        ('retargeting', 'Retargeting'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advertiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns')

    name = models.CharField(max_length=200)
    objective = models.CharField(max_length=50, choices=OBJECTIVE_CHOICES, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')

    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impressions = models.BigIntegerField(default=0)
    clicks = models.BigIntegerField(default=0)
    conversions = models.IntegerField(default=0)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Targeting
    target_locations = models.JSONField(default=list)
    target_audience = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'
        ordering = ['-created_at']

    @property
    def ctr(self):
        if self.impressions == 0:
            return 0.0
        return round(self.clicks / self.impressions * 100, 2)

    def __str__(self):
        return f'{self.name} ({self.advertiser.email})'


class CreativeAsset(models.Model):
    ASSET_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('pdf', 'PDF'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advertiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='creative_assets')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')

    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='creative_assets/')
    thumbnail = models.ImageField(upload_to='creative_assets/thumbnails/', null=True, blank=True)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES, default='image')
    file_size = models.BigIntegerField(default=0)
    dimensions = models.JSONField(default=dict)  # {width, height, dpi}

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'creative_assets'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.advertiser.email})'

class CampaignMessage(models.Model):
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
