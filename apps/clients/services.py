from typing import Any

from django.db import transaction
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from apps.clients.models import Client


class ClientService:
    @staticmethod
    @transaction.atomic
    def create_client(
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        username: str,
        role: str = Client.Role.STUDENT,
    ) -> Client:
        email = email.strip().lower()
        username = username.strip().lower()

        ClientService.ensure_email_available(email)
        ClientService.ensure_username_available(username)

        return Client.objects.create_user(  # type: ignore
            email=email,
            password=password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            username=username,
            role=role,
        )

    @staticmethod
    @transaction.atomic
    def update_client(
        client: Client,
        *,
        data: dict[str, Any],
    ) -> Client:
        if not data:
            return client
        data = data.copy()
        if "email" in data:
            email = data["email"].strip().lower()
            ClientService.ensure_email_available(
                email,
                exclude_client=client,
            )
            data["email"] = email
        if "username" in data:
            username = data["username"].strip().lower()
            ClientService.ensure_username_available(
                username,
                exclude_client=client,
            )
            data["username"] = username

        if "first_name" in data:
            data["first_name"] = data["first_name"].strip()
        if "last_name" in data:
            data["last_name"] = data["last_name"].strip()

        for field, value in data.items():
            setattr(client, field, value)
        client.save(update_fields=list(data.keys()))
        return client

    @staticmethod
    @transaction.atomic
    def change_password(
        client: Client,
        *,
        current_password: str,
        new_password: str,
    ) -> Client:
        if not client.check_password(current_password):
            raise ValidationError(
                {"current_password": ("Current password is incorrect.")}
            )
        if current_password == new_password:
            raise ValidationError(
                {
                    "password": (
                        "New password must be different " "from the current password."
                    )
                }
            )
        client.set_password(new_password)
        client.save(update_fields=["password"])
        return client

    @staticmethod
    def activate_client(client: Client) -> Client:
        if client.is_active:
            return client
        client.is_active = True
        client.save(update_fields=["is_active"])
        return client

    @staticmethod
    def deactivate_client(client: Client) -> Client:
        if not client.is_active:
            return client
        client.is_active = False
        client.save(update_fields=["is_active"])
        return client

    @staticmethod
    def verify_client(client: Client) -> Client:
        if client.is_verified:
            return client
        client.is_verified = True
        client.save(update_fields=["is_verified"])
        return client

    @staticmethod
    def ensure_email_available(
        email: str,
        *,
        exclude_client: Client | None = None,
    ) -> None:
        queryset = Client.objects.filter(
            email=email,
        )
        if exclude_client is not None:
            queryset = queryset.exclude(
                pk=exclude_client.pk,
            )
        if queryset.exists():
            raise ValidationError(
                {"email": ("A client with this email already exists.")}
            )

    @staticmethod
    def ensure_username_available(
        username: str,
        *,
        exclude_client: Client | None = None,
    ) -> None:
        queryset = Client.objects.filter(
            username=username,
        )
        if exclude_client is not None:
            queryset = queryset.exclude(
                pk=exclude_client.pk,
            )
        if queryset.exists():
            raise ValidationError(
                {"username": ("A client with this username already exists.")}
            )

    @staticmethod
    def get_client(
        client_id,
    ) -> Client:
        return Client.objects.get(
            pk=client_id,
        )

    @staticmethod
    def get_client_by_email(
        email: str,
    ) -> Client | None:
        return Client.objects.filter(
            email=email.strip().lower(),
        ).first()

    @staticmethod
    def get_client_by_username(
        username: str,
    ) -> Client | None:
        return Client.objects.filter(
            username=username.strip().lower(),
        ).first()

    @staticmethod
    def list_clients() -> QuerySet[Client]:
        return Client.objects.all()
