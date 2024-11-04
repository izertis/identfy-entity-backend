import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect


class EmailService:
    def __init__(self, subject, email, template):
        self.subject = subject
        self.email = email
        self.template = template

    def send_mail(self):
        try:
            email = EmailMessage(
                self.subject,
                self.template,
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
            )
            email.content_subtype = "html"
            email.send()
            logging.info("Email sent")
            return HttpResponseRedirect(".")
        except Exception as e:
            print(e)
