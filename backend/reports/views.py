"""API views for the reports application."""
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import IsAdmin
from reports import services
from utils.logging import get_logger

logger = get_logger('reports')


class ReportListView(APIView):
    """GET /api/reports/ — list stored reports; POST generates a new report."""

    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(services.list_reports(request.query_params))

    def post(self, request):
        generated_by = getattr(request.user, 'email', '')
        return Response(services.generate_report(generated_by=generated_by), status=status.HTTP_201_CREATED)


class ReportCreateView(APIView):
    """POST /api/reports/ — generate and persist a fresh report."""

    permission_classes = [IsAdmin]

    def post(self, request):
        generated_by = getattr(request.user, 'email', '')
        return Response(services.generate_report(generated_by=generated_by), status=status.HTTP_201_CREATED)


class ReportExportView(APIView):
    """POST /api/reports/<format>/ — download a CSV, Excel or PDF export."""

    permission_classes = [IsAdmin]

    FORMATS = {
        'csv': services.export_csv,
        'excel': services.export_excel,
        'pdf': services.export_pdf,
    }

    def post(self, request, export_format: str):
        exporter = self.FORMATS.get(export_format)
        if exporter is None:
            return Response(
                {'error': 'validation_error', 'message': 'Unsupported export format. Use csv, excel or pdf.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content, filename, content_type = exporter()
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
