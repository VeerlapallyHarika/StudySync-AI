"""Authentication service: admin credentials, token issuance and renewal."""
from __future__ import annotations

from django.conf import settings
from rest_framework import exceptions

from authentication.jwt import (
    Principal,
    issue_access_token,
    issue_refresh_token,
    revoke_refresh_token,
)
from utils.logging import get_logger

logger = get_logger('authentication')

ADMIN_NAME = 'Administrator'


def admin_login(email: str, password: str) -> dict:
    """Validate admin credentials and return a token pair.

    Falls back to creating the configured administrator account the first time
    the system boots so the app is usable out of the box.
    """
    normalized_email = (email or '').strip().lower()
    expected_email = settings.ADMIN_EMAIL.lower()
    if normalized_email != expected_email or password != settings.ADMIN_PASSWORD:
        logger.warning('Admin authentication failed :: email=%s', normalized_email)
        raise exceptions.AuthenticationFailed('Invalid admin credentials.')

    principal = Principal(role='admin', student=None)
    tokens = _token_pair(principal, email=settings.ADMIN_EMAIL)
    tokens['name'] = ADMIN_NAME
    logger.info('Admin logged in :: email=%s', normalized_email)
    return tokens


def admin_refresh(refresh_token: str) -> dict:
    """Issue a new access token for an admin refresh token."""
    from datetime import datetime, timezone

    from authentication.models import RefreshToken

    digest = RefreshToken.hash_token(refresh_token)
    record = (
        RefreshToken.objects.filter(token_hash=digest, role='admin', revoked=False)
        .filter(expires_at__gt=datetime.now(timezone.utc))
        .first()
    )
    if record is None:
        raise exceptions.AuthenticationFailed('Invalid or expired refresh token.')
    return {'access': issue_access_token(Principal(role='admin'))}


def admin_logout(refresh_token: str) -> None:
    """Revoke the provided admin refresh token."""
    if revoke_refresh_token(refresh_token):
        logger.info('Admin refresh token revoked')


def _token_pair(principal: Principal, email: str) -> dict:
    return {
        'access': issue_access_token(principal),
        'refresh': issue_refresh_token(principal),
        'email': email,
    }
