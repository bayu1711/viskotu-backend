import uuid
from django.db import models
from django.conf import settings


class PrintJob(models.Model):
    STATUS_CHOICES = [
        ('JOB_PENDING_ACCEPT', 'Pending Acceptance'),
        ('JOB_PREP', 'Prep'),
        ('JOB_PRINTING', 'Printing'),
        ('JOB_QA', 'Quality Check'),
        ('JOB_SHIPPING', 'Shipping'),
        ('JOB_COMPLETED', 'Completed'),
        ('JOB_REROUTING', 'Rerouting'),
        ('JOB_STALLED', 'Stalled'),
        ('JOB_FORFEITED', 'Forfeited'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    SOURCE_CHOICES = [
        ('platform-assigned', 'Platform Assigned'),
        ('host-selected', 'Host Selected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ad_placement = models.OneToOneField(
        'placements.AdPlacement', on_delete=models.CASCADE, related_name='print_job', null=True, blank=True
    )
    production_partner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='print_jobs'
    )

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='JOB_PENDING_ACCEPT')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    production_partner_source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='platform-assigned')

    # Specs
    material = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=1)
    finish = models.CharField(max_length=100, blank=True)

    # Checklist (production milestones)
    checklist = models.JSONField(default=dict)

    # Timing
    deadline = models.DateTimeField(null=True, blank=True)
    accept_deadline = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Rerouting tracking
    reroute_count = models.IntegerField(default=0)
    tried_production_partner_ids = models.JSONField(default=list)

    # Proof of play
    proof_file = models.FileField(upload_to='proof_of_play/', null=True, blank=True)
    proof_submitted_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'print_jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f'Job {self.id} [{self.status}]'

    def reroute_to_next_production_partner(self):
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        import datetime
        User = get_user_model()

        if self.production_partner and str(self.production_partner.id) not in self.tried_production_partner_ids:
            self.tried_production_partner_ids.append(str(self.production_partner.id))

        self.reroute_count += 1

        next_printer = User.objects.filter(role='production-partner').exclude(id__in=self.tried_production_partner_ids).first()
        if next_printer:
            self.production_partner = next_printer
            self.status = 'JOB_PENDING_ACCEPT'
            self.accept_deadline = timezone.now() + datetime.timedelta(hours=24)
            self.save(update_fields=['production_partner', 'status', 'accept_deadline', 'tried_production_partner_ids', 'reroute_count', 'updated_at'])
            return next_printer
        else:
            self.production_partner = None
            self.status = 'JOB_STALLED'
            self.save(update_fields=['production_partner', 'status', 'tried_production_partner_ids', 'reroute_count', 'updated_at'])
            return None
