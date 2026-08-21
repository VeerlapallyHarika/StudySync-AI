"""Shared DRF throttling scopes for sensitive authentication endpoints.

Applying :class:`ScopedRateThrottle` with the ``login`` scope limits how often
an unauthenticated caller can attempt registration, login or token refresh,
which mitigates brute-force and credential-stuffing attacks.
"""
from rest_framework.throttling import ScopedRateThrottle


class LoginRateThrottle(ScopedRateThrottle):
    """Limits attempts against authentication endpoints per IP address."""

    scope = 'login'


__all__ = ['LoginRateThrottle']
