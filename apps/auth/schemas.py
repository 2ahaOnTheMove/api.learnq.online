from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class VerifyAccountSchema(BaseModel):
    token: UUID
    code: str = Field(min_length=6, max_length=6)


class ResendVerificationSchema(BaseModel):
    token: UUID
