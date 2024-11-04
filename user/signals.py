from base64 import urlsafe_b64encode

from django import utils
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template, render_to_string
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.signals import reset_password_token_created

from .services.email_service import EmailService
from .tasks import send_email


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, **kwargs
):
    context = {
        "reset_password_url": f"{settings.FRONTEND_URL}/password_reset/{reset_password_token.key}"
    }

    email_plaintext_message = render_to_string(
        "email/password_reset_email.txt", context
    )
    email_html_message = render_to_string(
        "email/password_reset_email.html", context
    )

    send_email.delay(
        _("Password reset for Identfy"),
        settings.DEFAULT_FROM_EMAIL,
        [reset_password_token.user.email],
        email_plaintext_message,
        email_html_message,
    )


@receiver(post_save, sender=User)
def post_save_profile(sender, instance: User, **kwargs):

    if (
        not instance.is_superuser
        and instance.email is not None
        and kwargs.get("created")
    ):

        subject = _("Identfy Account Activation")
        token_service = PasswordResetTokenGenerator()
        welcome_message = _(
            str(
                "You have been invited to the Identfy Platform for Verifiable Credentials. In order to continue you need to activate your account and update your password through the form available at the following link: "
            )
        )
        message = get_template("email/welcome_user.html").render(
            (
                {
                    "user": _("Your username is : ") + instance.username,
                    "message": welcome_message,
                    "domain": settings.BACKEND_DOMAIN,
                    "uid": urlsafe_b64encode(
                        utils.encoding.force_bytes(instance.pk)
                    ).decode("utf-8"),
                    "token": token_service.make_token(instance),
                    "activate_message": _("Account Activation"),
                }
            )
        )
        mail = EmailService(subject, instance.email, message)
        mail.send_mail()
