from datetime import timedelta
import secrets

from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import check_password, make_password

from apps.auth.models import EmailVerification
from apps.auth.services.email import EmailService
from apps.clients.models import Client


class VerificationService:
    CODE_EXPIRY_MINUTES = 10
    MAX_ATTEMPTS = 5
    RESEND_COOLDOWN_SECONDS = 60
    MAX_RESENDS = 3

    @staticmethod
    def generate_code() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    @classmethod
    @transaction.atomic
    def get_or_create(cls, user: Client) -> EmailVerification:
        try:
            verification = EmailVerification.objects.select_for_update().get(user=user)
            if verification.expires_at > timezone.now():
                return verification
        except EmailVerification.DoesNotExist:
            verification = EmailVerification(user=user)
        code = cls.generate_code()
        verification.code_hash = make_password(code)
        verification.expires_at = timezone.now() + timedelta(
            minutes=cls.CODE_EXPIRY_MINUTES
        )
        verification.attempts = 0
        verification.save()
        cls.send_code(user=user, code=code)
        return verification

    @classmethod
    def verify(cls, *, token, code: str) -> Client:
        invalid_code = False
        with transaction.atomic():
            try:
                verification = (
                    EmailVerification.objects.select_for_update()
                    .select_related("user")
                    .get(token=token)
                )
            except EmailVerification.DoesNotExist:
                raise ValueError("Invalid or expired verification token.")
            user = verification.user
            if user.is_verified:
                verification.delete()
                raise ValueError("This account is already verified.")
            if verification.expires_at <= timezone.now():
                raise ValueError("Verification code has expired.")
            if verification.attempts >= cls.MAX_ATTEMPTS:
                raise ValueError(
                    "Too many verification attempts. " "Please request a new code."
                )
            if not check_password(
                code,
                verification.code_hash,
            ):
                verification.attempts += 1
                verification.save(update_fields=["attempts"])
                invalid_code = True
            else:
                user.is_verified = True
                user.save(update_fields=["is_verified"])
                verification.delete()
        if invalid_code:
            raise ValueError("Invalid verification code.")
        return user

    @classmethod
    @transaction.atomic
    def resend(cls, *, token) -> None:
        try:
            verification = (
                EmailVerification.objects.select_for_update()
                .select_related("user")
                .get(token=token)
            )
        except EmailVerification.DoesNotExist:
            raise ValueError("Invalid or expired verification token.")
        user = verification.user
        if user.is_verified:
            verification.delete()
            raise ValueError("This account is already verified.")
        now = timezone.now()
        if verification.resend_count >= cls.MAX_RESENDS:
            if verification.expires_at:
                next_allowed = verification.expires_at + timedelta(
                    minutes=cls.CODE_EXPIRY_MINUTES
                )
                if now < next_allowed:
                    remaining = int((next_allowed - now).total_seconds() / 60)
                    raise ValueError(
                        "You have reached the maximum number of resend attempts. "
                        f"Please try again after {remaining} minutes."
                    )
        if verification.last_sent_at:
            next_allowed = verification.last_sent_at + timedelta(
                seconds=cls.RESEND_COOLDOWN_SECONDS
            )
            if now < next_allowed:
                remaining = int((next_allowed - now).total_seconds())
                raise ValueError(
                    f"Please wait {remaining } seconds before requesting "
                    "another verification code."
                )
        code = cls.generate_code()
        verification.code_hash = make_password(code)
        verification.expires_at = timezone.now() + timedelta(
            minutes=cls.CODE_EXPIRY_MINUTES
        )
        verification.attempts = 0
        verification.resend_count += 1
        verification.last_sent_at = now
        verification.save(
            update_fields=[
                "code_hash",
                "expires_at",
                "attempts",
                "resend_count",
                "last_sent_at",
            ]
        )
        cls.send_code(user=user, code=code)

    @staticmethod
    def send_code(*, user: Client, code: str) -> None:
        EmailService.send_verification_code(
            recipient=user.email,
            username=user.username,
            code=code,
        )
