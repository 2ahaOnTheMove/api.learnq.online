from typing import cast
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.auth.exceptions import AccountNotVerifiedError
from apps.auth.services.verification import VerificationService
from apps.clients.models import Client


class AuthenticationService:
    @staticmethod
    def login(email: str, password: str) -> dict:
        user = authenticate(
            email=email,
            password=password,
        )
        user = cast(Client, user)
        if user is None:
            raise ValueError("Invalid email address or password.")
        if not user.is_verified:  # type: ignore
            verification = VerificationService.get_or_create(user)
            raise AccountNotVerifiedError(token=verification.token)
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user,
        }
