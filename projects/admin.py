from django.contrib import admin
from .models import Project, WorkType, WorkLog, Deliverable


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'client_name', 'current_stage')
    search_fields = ('name', 'client_name')
    list_filter = ('current_stage',)


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'project', 'work_type', 'start_time', 'end_time', 'duration')
    list_filter = ('project', 'employee', 'work_type')
    search_fields = ('employee__username', 'project__name')


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'name', 'stage', 'status', 'remarks')
    list_filter = ('project', 'stage', 'status')
    search_fields = ('name', 'project__name', 'remarks')
