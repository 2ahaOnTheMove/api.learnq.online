from django.conf import settings
from django.utils import timezone

from rest_framework import status
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler.
    Converts known DRF exceptions into a consistent API error format.
    """
    request = context.get("request")
    response = exception_handler(exc, context)
    if response is not None:
        return handle_known_exception(response=response, exc=exc, request=request)
    return handle_unknown_exception(exc=exc, request=request)


def handle_known_exception(response, exc, request):
    """
    Handle exceptions already understood by DRF.
    """
    error_type = exc.__class__.__name__
    error_code = getattr(exc, "default_code", "error")
    message = get_exception_message(exc)
    details = extract_error_details(response.data, exc)
    error_response = format_error_response(
        message=message,
        error_type=error_type,
        error_code=error_code,
        status_code=response.status_code,
        details=details,
        request=request,
    )
    response.data = error_response
    return response


def handle_unknown_exception(exc, request):
    """
    Handle exceptions that DRF does not understand.
    """
    error_type = exc.__class__.__name__
    if settings.DEBUG:
        message = str(exc)
        details = {"exception": error_type}
    else:
        message = "Internal server error."
        details = None
    error_response = format_error_response(
        message=message,
        error_type=error_type,
        error_code="internal_error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=details,
        request=request,
    )
    return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_exception_message(exc):
    """
    Extract a clean human-readable message from an exception.
    """
    if isinstance(exc, DRFValidationError):
        return "Validation failed."
    if hasattr(exc, "detail"):
        detail = exc.detail
        if isinstance(detail, str):
            return detail
        if isinstance(detail, dict):
            return "Validation failed."
        if isinstance(detail, list):
            return "Validation failed."
    return str(exc)


def extract_error_details(response_data, exc):
    """
    Extract field-level validation errors.
    """
    if isinstance(exc, DRFValidationError):
        if isinstance(response_data, dict):
            return response_data
        return None
    return None


def format_error_response(
    message,
    error_type,
    error_code,
    status_code,
    details=None,
    request=None,
):
    """
    Return the standard API error response.
    Example:
    {
        "success": false,
        "error": {
            "type": "ValidationError",
            "code": "invalid",
            "message": "Validation failed.",
            "status_code": 400,
            "timestamp": "...",
            "request_id": "...",
            "details": {
                "email": [
                    "Invalid email address or password."
                ]
            }
        }
    }
    """
    error = {
        "type": error_type,
        "code": error_code,
        "message": message,
        "status_code": status_code,
        "timestamp": timezone.now().isoformat(),
    }
    if request:
        request_id = getattr(request, "_request_id", None)
        if request_id:
            error["request_id"] = request_id
    if details:
        error["details"] = details
    return {"success": False, "error": error}
