from django.contrib import admin

from insights.models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('default_group_size', 'kmeans_random_state', 'export_default_format', 'updated_at')
