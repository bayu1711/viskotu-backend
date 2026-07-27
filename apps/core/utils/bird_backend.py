import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives

class BirdEmailBackend(BaseEmailBackend):
    """
    A custom Django EmailBackend that sends emails using the Bird REST API.
    """
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.api_url = "https://eu1.platform.bird.com/v1/email/messages"
        self.api_key = getattr(settings, 'BIRD_API_KEY', '')
        self.default_from = getattr(settings, 'DEFAULT_FROM_EMAIL', 'onboarding@messagebird.dev')

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        num_sent = 0
        for message in email_messages:
            if self._send(message):
                num_sent += 1
        return num_sent

    def _send(self, email_message):
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("BIRD_API_KEY is not configured in settings.")
            return False

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        # Handle HTML content
        html_body = ""
        if isinstance(email_message, EmailMultiAlternatives):
            for alt in email_message.alternatives:
                if alt[1] == "text/html":
                    html_body = alt[0]
                    break

        payload = {
            "from": email_message.from_email or self.default_from,
            "to": [{"email": addr} for addr in email_message.to],
            "subject": email_message.subject,
            "html": html_body or email_message.body,
            "text": email_message.body,
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            if not self.fail_silently:
                raise e
            return False
