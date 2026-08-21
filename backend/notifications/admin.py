from django.contrib import admin

from notifications.models import ActivityLog, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('role', 'category', 'title', 'tone', 'read', 'created_at')
    list_filter = ('role', 'tone', 'read', 'category')
    search_fields = ('title', 'message')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor', 'detail', 'created_at')
    list_filter = ('action',)
    search_fields = ('detail',)
