from django.urls import path

from insights import views

app_name = 'insights'

urlpatterns = [
    path('admin/analytics/', views.AdminAnalyticsView.as_view(), name='admin-analytics'),
    path('admin/settings/', views.AdminSettingsView.as_view(), name='admin-settings'),
    path('admin/system-info/', views.AdminSystemInfoView.as_view(), name='admin-system-info'),
    path('student/insights/', views.StudentInsightsView.as_view(), name='student-insights'),
    path('student/change-password/', views.StudentChangePasswordView.as_view(), name='student-change-password'),
]
