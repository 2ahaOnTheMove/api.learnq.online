from rest_framework import serializers

from apps.clients.models import Client
from apps.clients.schemas import (
    ClientCreateSchema,
)
from apps.clients.services import ClientService
from apps.common.helpers import format_pydantic_error


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "email",
            "username",
            "role",
            "is_verified",
        ]
        read_only_fields = fields


class ClientCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    confirm_password = serializers.CharField(
        write_only=True, min_length=8, max_length=128
    )

    class Meta:
        model = Client
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "username",
            "role",
            "password",
            "confirm_password",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        try:
            schema = ClientCreateSchema.model_validate(attrs)
        except Exception as exc:
            raise serializers.ValidationError(format_pydantic_error(exc)) from exc
        return schema.model_dump()

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        try:
            return ClientService.create_client(**validated_data)
        except serializers.ValidationError:
            raise
