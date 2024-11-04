from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_email(subject, from_email, to_emails, content, html_content=None):
    send_mail(
        subject, content, from_email, to_emails, html_message=html_content, fail_silently=False
    )
