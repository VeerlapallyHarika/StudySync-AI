from django.urls import path

from reports import views

app_name = 'reports'

urlpatterns = [
    path('reports/', views.ReportListView.as_view(), name='reports-list'),
    path('reports/generate/', views.ReportCreateView.as_view(), name='reports-generate'),
    path('reports/<str:export_format>/', views.ReportExportView.as_view(), name='reports-export'),
]
