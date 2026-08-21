"""API views for notifications and recent activity."""
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import HasPrincipal, IsAdmin
from notifications import services
from utils.logging import get_logger

logger = get_logger('notifications')


class NotificationListView(APIView):
    """GET /api/notifications/ — list notifications for the current principal.

    Admin principals receive admin notifications; student principals receive
    their personal notifications. DELETE clears every notification for the
    principal.
    """

    permission_classes = [HasPrincipal]

    def get(self, request):
        return Response({'notifications': services.list_for(getattr(request, 'principal', None))})

    def delete(self, request):
        deleted = services.clear_all(getattr(request, 'principal', None))
        return Response({'deleted': deleted})


class NotificationReadView(APIView):
    """POST /api/notifications/<id>/read/ — mark a single notification read."""

    permission_classes = [HasPrincipal]

    def post(self, request, notification_id):
        updated = services.mark_read(getattr(request, 'principal', None), notification_id)
        if not updated:
            return Response({'error': 'not_found', 'message': 'Notification not found.'}, status=404)
        return Response({'detail': 'Marked as read.'})


class NotificationReadAllView(APIView):
    """POST /api/notifications/read-all/ — mark every notification read."""

    permission_classes = [HasPrincipal]

    def post(self, request):
        count = services.mark_all_read(getattr(request, 'principal', None))
        return Response({'marked': count})


class ActivityListView(APIView):
    """GET /api/admin/activities/ — recent activity for the admin dashboard."""

    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({'activities': services.recent_activities()})
