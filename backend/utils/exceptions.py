"""Centralized API exception handling.

Converts DRF, Django and unexpected exceptions into a consistent JSON error
payload while keeping the appropriate HTTP status code. ``validation`` and
``error`` fields mirror the error shape the React frontend already consumes.
"""
from __future__ import annotations

import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from utils.logging import get_logger

logger = get_logger('exceptions')

MESSAGES = {
    'NOT_FOUND': 'The requested resource does not exist.',
    'PERMISSION_DENIED': 'You do not have permission to perform this action.',
    'AUTHENTICATION_FAILED': 'Authentication credentials were not provided.',
    'VALIDATION_ERROR': 'The submitted data is invalid.',
    'SERVER_ERROR': 'An unexpected error occurred. Please try again later.',
}


def studysync_exception_handler(exc, context):
    """DRF exception handler producing a consistent ``{error, message, validation}`` shape."""
    response = drf_exception_handler(exc, context)

    if response is None:
        if isinstance(exc, Http404):
            response = Response(
                {'error': 'not_found', 'message': MESSAGES['NOT_FOUND']},
                status=404,
            )
        elif isinstance(exc, DjangoPermissionDenied):
            response = Response(
                {'error': 'permission_denied', 'message': MESSAGES['PERMISSION_DENIED']},
                status=403,
            )
        else:
            logger.exception('Unhandled exception: %s', exc)
            response = Response(
                {'error': 'server_error', 'message': MESSAGES['SERVER_ERROR']},
                status=500,
            )
        return response

    if isinstance(exc, drf_exceptions.ValidationError):
        response.data = {
            'error': 'validation_error',
            'message': MESSAGES['VALIDATION_ERROR'],
            'validation': _flatten_validation(response.data),
        }
    elif isinstance(exc, drf_exceptions.AuthenticationFailed):
        response.data = {
            'error': 'authentication_failed',
            'message': str(getattr(exc, 'detail', MESSAGES['AUTHENTICATION_FAILED'])),
        }
    elif isinstance(exc, drf_exceptions.PermissionDenied):
        response.data = {
            'error': 'permission_denied',
            'message': str(getattr(exc, 'detail', MESSAGES['PERMISSION_DENIED'])),
        }
    elif isinstance(exc, drf_exceptions.NotFound):
        response.data = {
            'error': 'not_found',
            'message': str(getattr(exc, 'detail', MESSAGES['NOT_FOUND'])),
        }
    elif isinstance(exc, drf_exceptions.APIException):
        response.data = {
            'error': 'api_error',
            'message': str(getattr(exc, 'detail', MESSAGES['SERVER_ERROR'])),
        }

    return response


def _flatten_validation(detail):
    """Flatten nested DRF validation errors into a readable message string."""
    if isinstance(detail, dict):
        if len(detail) == 1 and 'non_field_errors' in detail:
            return str(detail['non_field_errors'])
        return ' '.join(str(_flatten_validation(value)) for value in detail.values())
    if isinstance(detail, (list, tuple)):
        return ' '.join(str(_flatten_validation(item)) for item in detail)
    return str(detail)
