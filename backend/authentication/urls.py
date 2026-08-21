from django.urls import path

from authentication import views

app_name = 'authentication'

urlpatterns = [
    path('admin/login/', views.AdminLoginView.as_view(), name='admin-login'),
    path('admin/refresh/', views.AdminRefreshView.as_view(), name='admin-refresh'),
    path('admin/logout/', views.AdminLogoutView.as_view(), name='admin-logout'),
]
