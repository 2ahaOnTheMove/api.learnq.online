from rest_framework import status
from rest_framework.exceptions import APIException


class BaseAPIException(APIException):
    """
    Base exception for custom API exceptions.
    Custom exceptions should inherit from this class.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An error occurred."
    default_code = "error"

    def __init__(
        self,
        detail=None,
        code=None,
        status_code=None,
    ):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(
            detail=detail or self.default_detail,
            code=code or self.default_code,
        )


class ValidationFailedError(BaseAPIException):
    """400 - Validation failed."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation failed."
    default_code = "validation_failed"


class BadRequestError(BaseAPIException):
    """400 - Bad request."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request."
    default_code = "bad_request"


class AuthenticationRequiredError(BaseAPIException):
    """401 - Authentication required."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication credentials were not provided."
    default_code = "authentication_required"


class InvalidTokenError(BaseAPIException):
    """401 - Invalid or expired token."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid or expired token."
    default_code = "invalid_token"


class PermissionDeniedError(BaseAPIException):
    """403 - Permission denied."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."
    default_code = "permission_denied"


class ResourceNotFoundError(BaseAPIException):
    """404 - Resource not found."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."
    default_code = "not_found"


class DuplicateResourceError(BaseAPIException):
    """409 - Duplicate resource."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource already exists."
    default_code = "duplicate_resource"


class ConflictError(BaseAPIException):
    """409 - Conflict."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict with existing resource."
    default_code = "conflict"


class RateLimitExceededError(BaseAPIException):
    """429 - Rate limit exceeded."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Rate limit exceeded."
    default_code = "rate_limit_exceeded"


class InternalServerError(BaseAPIException):
    """500 - Internal server error."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Internal server error."
    default_code = "internal_error"


class ServiceUnavailableError(BaseAPIException):
    """503 - Service unavailable."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporarily unavailable."
    default_code = "service_unavailable"
