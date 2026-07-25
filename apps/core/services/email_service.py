from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from apps.core.utils.async_task import run_in_background

@run_in_background
def send_welcome_email(user, reset_url=None):
    subject = "Welcome to Viskotu!" if not reset_url else "Reset Your Viskotu Password"
    context = {
        'user': user,
        'reset_url': reset_url,
    }
    
    html_message = render_to_string('emails/welcome.html', context)
    message = "Welcome to Viskotu!" if not reset_url else f"Reset your password here: {reset_url}"
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

@run_in_background
def send_campaign_funded_email(campaign, advertiser):
    subject = f"Campaign '{campaign.title}' Funded!"
    context = {
        'campaign': campaign,
        'advertiser': advertiser,
    }
    
    html_message = render_to_string('emails/campaign_funded.html', context)
    message = f"Your campaign '{campaign.title}' has been successfully funded."
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[advertiser.email],
        html_message=html_message,
        fail_silently=False,
    )

@run_in_background
def send_job_assigned_email(job, printer):
    subject = f"New Print Job Assigned: {job.title}" if hasattr(job, 'title') else "New Print Job Assigned"
    context = {
        'job': job,
        'printer': printer,
    }
    
    html_message = render_to_string('emails/job_assigned.html', context)
    message = f"You have been assigned a new print job."
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[printer.email],
        html_message=html_message,
        fail_silently=False,
    )

@run_in_background
def send_payout_requested_email(payout, owner):
    subject = "Payout Requested"
    context = {
        'payout': payout,
        'owner': owner,
    }
    
    html_message = render_to_string('emails/payout_requested.html', context)
    message = f"Your payout request has been received."
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[owner.email],
        html_message=html_message,
        fail_silently=False,
    )
