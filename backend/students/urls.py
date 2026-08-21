from django.urls import path

from students import views

app_name = 'students'

urlpatterns = [
    path('student/register/', views.StudentRegisterView.as_view(), name='student-register'),
    path('student/login/', views.StudentLoginView.as_view(), name='student-login'),
    path('student/refresh/', views.StudentRefreshView.as_view(), name='student-refresh'),
    path('student/logout/', views.StudentLogoutView.as_view(), name='student-logout'),
    path('student/profile/', views.StudentProfileView.as_view(), name='student-profile'),
    path('student/dashboard/', views.StudentDashboardView.as_view(), name='student-dashboard'),
    path('admin/students/', views.AdminStudentListView.as_view(), name='admin-students'),
    path('admin/student/<str:student_id>/', views.AdminStudentDetailView.as_view(), name='admin-student-detail'),
    path('admin/import-csv/', views.AdminImportCsvView.as_view(), name='admin-import-csv'),
]
