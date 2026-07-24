from django.utils import timezone
import datetime
from apps.jobs.models import PrintJob
from django.contrib.auth import get_user_model

MAX_REROUTE_ATTEMPTS = 2

def reroute_production_partner(job, reason="MISSED_ACCEPT_WINDOW"):
    User = get_user_model()
    
    if job.reroute_count >= MAX_REROUTE_ATTEMPTS:
        return {
            'new_production_partner': None,
            'reroute_reason': reason,
            'exhausted': True,
            'exhaust_reason': 'max_attempts_reached'
        }
        
    if job.production_partner and str(job.production_partner.id) not in job.tried_production_partner_ids:
        job.tried_production_partner_ids.append(str(job.production_partner.id))
        
    # Get a new partner
    excluded_ids = job.tried_production_partner_ids
    available_candidates = User.objects.filter(role='production-partner').exclude(id__in=excluded_ids)
    
    new_partner = available_candidates.first()
    
    if not new_partner:
        return {
            'new_production_partner': None,
            'reroute_reason': reason,
            'exhausted': True,
            'exhaust_reason': 'no_backup_available'
        }
        
    return {
        'new_production_partner': new_partner,
        'reroute_reason': reason,
        'exhausted': False
    }

def check_accept_window_expiry():
    now = timezone.now()
    # Find jobs that are pending accept and past their deadline
    expired_jobs = PrintJob.objects.filter(
        status='JOB_PENDING_ACCEPT',
        accept_deadline__lt=now
    )
    
    processed_count = 0
    
    for job in expired_jobs:
        result = reroute_production_partner(job)
        
        if result['exhausted']:
            job.status = 'JOB_STALLED'
            job.production_partner = None
            job.save(update_fields=['status', 'production_partner', 'updated_at'])
        else:
            job.reroute_count += 1
            job.status = 'JOB_REROUTING'
            job.production_partner = result['new_production_partner']
            job.accept_deadline = now + datetime.timedelta(hours=24)
            job.save(update_fields=[
                'status', 'production_partner', 'accept_deadline', 
                'reroute_count', 'tried_production_partner_ids', 'updated_at'
            ])
            
        processed_count += 1
        
    return processed_count
