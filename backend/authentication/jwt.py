"""JWT helpers and the DRF authentication backend for StudySync AI.

Tokens are signed with the HS256 algorithm using the application secret and
carry a short-lived ``type=access`` claim. Refresh tokens are opaque random
strings tracked in :class:`authentication.models.RefreshToken` so they can be
revoked on logout.
"""
from __future__ import annotations

import datetime as dt
import secrets
from dataclasses import dataclass
from typing import Optional

import jwt
from django.conf import settings
from rest_framework import authentication, exceptions

from utils.logging import get_logger

logger = get_logger('jwt')

TYPE_ACCESS = 'access'
TYPE_REFRESH = 'refresh'


@dataclass
class Principal:
    """Authenticated principal attached to ``request.principal``."""

    role: str  # 'admin' or 'student'
    student: Optional['object'] = None

    # DRF throttle helpers and templates expect a Django-like user contract.
    is_authenticated = True
    is_anonymous = False

    @property
    def pk(self) -> str:
        """Stable throttle/cache identity: ``admin`` or the student's id."""
        if self.role == 'admin':
            return 'admin'
        if self.student is not None:
            return f'student-{self.student.pk}'
        return 'student-anon'

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

    @property
    def is_student(self) -> bool:
        return self.role == 'student'


def _config() -> dict:
    return settings.JWT


def issue_access_token(principal: Principal) -> str:
    """Issue a short-lived signed access token for a principal."""
    cfg = _config()
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        'sub': 'admin' if principal.is_admin else str(principal.student.pk),
        'role': principal.role,
        'type': TYPE_ACCESS,
        'iat': int(now.timestamp()),
        'exp': int((now + dt.timedelta(minutes=cfg['ACCESS_MINUTES'])).timestamp()),
        'jti': secrets.token_hex(16),
    }
    return jwt.encode(payload, cfg['SECRET'], algorithm=cfg['ALGORITHM'])


def issue_refresh_token(principal: Principal) -> str:
    """Issue a long-lived refresh token and persist its digest."""
    cfg = _config()
    from authentication.models import RefreshToken

    token = secrets.token_urlsafe(48)
    expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=cfg['REFRESH_DAYS'])
    RefreshToken.objects.create(
        token_hash=RefreshToken.hash_token(token),
        role=principal.role,
        student=principal.student if principal.is_student else None,
        expires_at=expires_at,
    )
    return token


def revoke_refresh_token(token: str) -> bool:
    """Mark a refresh token as revoked (used by logout)."""
    from authentication.models import RefreshToken

    digest = RefreshToken.hash_token(token)
    updated = RefreshToken.objects.filter(token_hash=digest).update(revoked=True)
    return updated > 0


def decode_access_token(token: str) -> Principal:
    """Decode an access token into a :class:`Principal`.

    Raises :class:`rest_framework.exceptions.AuthenticationFailed` on any
    invalid/expired token.
    """
    cfg = _config()
    try:
        payload = jwt.decode(token, cfg['SECRET'], algorithms=[cfg['ALGORITHM']])
    except jwt.ExpiredSignatureError as exc:
        raise exceptions.AuthenticationFailed('Token has expired.') from exc
    except jwt.InvalidTokenError as exc:
        raise exceptions.AuthenticationFailed('Invalid authentication token.') from exc

    if payload.get('type') != TYPE_ACCESS:
        raise exceptions.AuthenticationFailed('Invalid token type.')

    role = payload.get('role')
    if role == 'admin':
        return Principal(role='admin', student=None)
    if role == 'student':
        from students.models import Student

        try:
            student = Student.objects.get(pk=int(payload.get('sub', -1)))
        except (Student.DoesNotExist, TypeError, ValueError) as exc:
            raise exceptions.AuthenticationFailed('Student account no longer exists.') from exc
        return Principal(role='student', student=student)

    raise exceptions.AuthenticationFailed('Unknown token role.')


class JWTAuthentication(authentication.BaseAuthentication):
    """DRF authenticator reading ``Authorization: Bearer <access-token>``."""

    keyword = 'Bearer'

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).split()
        if not header:
            return None
        if header[0].lower() != self.keyword.lower().encode():
            return None
        if len(header) == 1:
            raise exceptions.AuthenticationFailed('Bearer token is missing.')
        if len(header) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header.')

        token = header[1].decode('utf-8')
        principal = decode_access_token(token)
        request.principal = principal
        return principal, token

    def authenticate_header(self, request) -> str:
        return self.keyword


__all__ = [
    'Principal',
    'JWTAuthentication',
    'issue_access_token',
    'issue_refresh_token',
    'revoke_refresh_token',
    'decode_access_token',
]
