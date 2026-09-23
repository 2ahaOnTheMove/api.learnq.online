from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class EmailDeliveryError(Exception):
    """Raised when the SMTP server does not accept an email for delivery."""


class EmailService:

    @staticmethod
    def send_templated_email(
        *, subject: str, recipient: str, template_name: str, context: dict
    ) -> None:
        html_content = render_to_string(template_name, context)
        message = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_content),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        message.attach_alternative(
            html_content,
            "text/html",
        )
        try:
            sent_count = message.send(fail_silently=False)
        except Exception as exc:
            raise EmailDeliveryError(
                "The email service is temporarily unavailable."
            ) from exc
        if sent_count != 1:
            raise EmailDeliveryError("The email service did not accept the message.")

    @classmethod
    def send_verification_code(
        cls, *, recipient: str, username: str, code: str
    ) -> None:
        cls.send_templated_email(
            subject="Verify your account",
            recipient=recipient,
            template_name="email/verify-account-otp.html",
            context={
                "username": username,
                "code": code,
            },
        )
