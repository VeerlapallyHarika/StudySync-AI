import os

from django.db import models


class RefreshToken(models.Model):
    """Server-side record used to revoke refresh tokens on logout.

    Only a SHA-256 digest of the token is stored so a leaked database cannot
    be replayed directly.
    """

    ROLE_CHOICES = (('admin', 'admin'), ('student', 'student'))

    token_hash = models.CharField(max_length=64, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    student = models.ForeignKey(
        'students.Student',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='refresh_tokens',
    )
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.role} refresh token (revoked={self.revoked})'

    @staticmethod
    def hash_token(token: str) -> str:
        import hashlib

        return hashlib.sha256(token.encode('utf-8')).hexdigest()
