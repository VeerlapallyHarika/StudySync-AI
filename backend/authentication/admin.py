from django.contrib import admin

from authentication.models import RefreshToken


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('role', 'student', 'revoked', 'expires_at', 'created_at')
    list_filter = ('role', 'revoked')
    search_fields = ('student__email',)
