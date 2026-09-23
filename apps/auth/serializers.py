from pydantic import ValidationError
from rest_framework import serializers

from apps.auth.exceptions import AccountNotVerifiedError
from apps.auth.schemas import (
    LoginSchema,
    ResendVerificationSchema,
    VerifyAccountSchema,
)
from apps.auth.services.auth import AuthenticationService
from apps.auth.services.verification import VerificationService
from apps.clients.serializers import ClientSerializer
from apps.common.helpers import format_pydantic_error


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        try:
            schema = LoginSchema(email=attrs["email"], password=attrs["password"])
        except ValidationError as exc:
            raise serializers.ValidationError(format_pydantic_error(exc))
        try:
            result = AuthenticationService.login(
                email=schema.email, password=schema.password
            )
        except AccountNotVerifiedError as exc:
            raise serializers.ValidationError(
                {
                    "error": "account_not_verified",
                    "message": str(exc),
                    "verification_token": exc.token,
                }
            )
        except ValueError as exc:
            raise serializers.ValidationError({"email": str(exc)})
        return {
            "access": result["access"],
            "refresh": result["refresh"],
            "user": ClientSerializer(result["user"]).data,
        }


class VerifyAccountSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    code = serializers.CharField(min_length=6, max_length=6, trim_whitespace=True)

    def validate(self, attrs):
        try:
            schema = VerifyAccountSchema(token=attrs["token"], code=attrs["code"])
        except ValidationError as exc:
            raise serializers.ValidationError(format_pydantic_error(exc))
        try:
            VerificationService.verify(token=schema.token, code=schema.code)
        except ValueError as exc:
            raise serializers.ValidationError({"code": str(exc)})
        return {"message": "Your account has been verified successfully."}


class ResendVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def validate(self, attrs):
        try:
            schema = ResendVerificationSchema(token=attrs["token"])
        except ValidationError as exc:
            raise serializers.ValidationError(format_pydantic_error(exc))
        try:
            VerificationService.resend(token=schema.token)
        except ValueError as exc:
            raise serializers.ValidationError({"token": str(exc)})
        return {"message": "A new verification code has been sent."}
