from django.urls import path

from groups import views

app_name = 'groups'

urlpatterns = [
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('groups/generate/', views.GenerateGroupsView.as_view(), name='groups-generate'),
    path('groups/delete-all/', views.DeleteAllGroupsView.as_view(), name='groups-delete-all'),
    path('groups/<int:group_id>/', views.GroupDetailView.as_view(), name='group-detail'),
    path('groups/', views.GroupListView.as_view(), name='groups-list'),
    # Spec-compliant Task 4 endpoint — authenticated student's group
    path('groups/my-group/', views.MyGroupView.as_view(), name='my-group'),
    # Student collaboration
    path('student/groups/', views.StudentGroupView.as_view(), name='student-group'),
    path('student/groups/status/', views.StudentGroupStatusView.as_view(), name='student-group-status'),
    path('student/groups/generate/', views.StudentGenerateGroupsView.as_view(), name='student-group-generate'),
    path('student/groups/chat/', views.StudentGroupChatView.as_view(), name='student-group-chat'),
    path('student/groups/resources/', views.StudentGroupResourcesView.as_view(), name='student-group-resources'),
    path('student/resources/', views.StudentResourcesView.as_view(), name='student-resources'),
]
