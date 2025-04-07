from django.contrib import admin
from .models import Project, WorkType, WorkLog

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'client_name')  # Added 'id'

@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Added 'id'

@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'project', 'work_type', 'start_time', 'end_time', 'duration')  # Added 'id'
    list_filter = ('project', 'employee', 'work_type')
    search_fields = ('employee__username', 'project__name')
