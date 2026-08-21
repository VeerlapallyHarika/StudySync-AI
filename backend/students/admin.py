from django.contrib import admin

from students.models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'email', 'department', 'year', 'section', 'average_score', 'group', 'created_at')
    list_filter = ('department', 'year', 'section', 'learning_preference', 'availability')
    search_fields = ('student_id', 'full_name', 'email')
    readonly_fields = ('average_score', 'strengths', 'weaknesses', 'created_at', 'updated_at')
