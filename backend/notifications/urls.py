from django.urls import path

from notifications import views

app_name = 'notifications'

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notifications-list'),
    path('notifications/read-all/', views.NotificationReadAllView.as_view(), name='notifications-read-all'),
    path('notifications/<int:notification_id>/read/', views.NotificationReadView.as_view(), name='notification-read'),
    path('admin/activities/', views.ActivityListView.as_view(), name='admin-activities'),
]
