import re
import uuid
from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)

ClientRole = Literal["student", "teacher", "moderator"]


class ClientBaseSchema(BaseModel):
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=30)
    last_name: str = Field(min_length=1, max_length=30)
    username: str = Field(min_length=3, max_length=50)
    role: ClientRole = "student"

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ ]+", value):
            raise ValueError("Name can only contain letters and spaces.")
        return value

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[a-z0-9-]+", value):
            raise ValueError(
                "Username can only contain lowercase letters, numbers, and hyphens."
            )
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class ClientCreateSchema(ClientBaseSchema):
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(
        cls,
        value: str,
        info,
    ) -> str:
        password = info.data.get("password")
        if password is not None and value != password:
            raise ValueError("Passwords do not match.")
        return value
