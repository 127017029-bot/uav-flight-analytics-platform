"""
Custom DRF exception handler for the UAV Digital Twin Platform.

Normalises all error responses into a consistent JSON envelope so that
front-end consumers can rely on a single error schema regardless of the
exception type.

Response format::

    {
        "success": false,
        "error": {
            "code": "<ERROR_CODE>",
            "message": "<human-readable summary>",
            "details": { ... }   // optional field-level errors
        }
    }
"""

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

# Mapping of HTTP status codes to short error codes.
STATUS_CODE_MAP: dict[int, str] = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    429: "THROTTLED",
    500: "INTERNAL_SERVER_ERROR",
}


def _build_error_body(
    code: str,
    message: str,
    details: dict | list | None = None,
) -> dict:
    """Return the canonical error envelope."""
    body: dict = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details:
        body["error"]["details"] = details
    return body


def custom_exception_handler(exc, context) -> Response | None:
    """
    Wrap DRF's default exception handler to produce a uniform error schema.

    Parameters
    ----------
    exc : Exception
        The exception instance raised during request processing.
    context : dict
        Additional context supplied by DRF (view, request, args, kwargs).

    Returns
    -------
    Response | None
        A DRF ``Response`` with the standardised error body, or ``None``
        if the exception is not handled (will result in a 500).
    """
    # Convert Django's built-in ValidationError to DRF's version so the
    # default handler can process it.
    if isinstance(exc, DjangoValidationError):
        exc = ValidationError(detail=exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

    # Let DRF handle the exception first.
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception – log and return a generic 500.
        logger.exception(
            "Unhandled exception in %s",
            context.get("view", "unknown view"),
        )
        body = _build_error_body(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
        )
        return Response(body, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Determine an appropriate short code.
    error_code = STATUS_CODE_MAP.get(
        response.status_code, f"ERROR_{response.status_code}"
    )

    # Build a human-readable message.
    if isinstance(exc, ValidationError):
        message = "Validation failed."
        details = response.data
    elif isinstance(exc, Http404):
        message = "The requested resource was not found."
        details = None
    elif isinstance(exc, APIException):
        message = str(exc.detail) if hasattr(exc, "detail") else str(exc)
        details = None
    else:
        message = "An error occurred."
        details = response.data

    body = _build_error_body(code=error_code, message=message, details=details)
    response.data = body
    return response
