from django.contrib import admin

from groups.models import StudyGroup


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'average_performance', 'complementary_skill_score', 'team_leader', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'team_leader')
    readonly_fields = ('members', 'overall_strengths', 'overall_weaknesses')
