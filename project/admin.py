from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Project, WorkLog, Deliverable, Organisation, OrganisationMembership


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(OrganisationMembership)
class OrganisationMembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'organisation', 'role')
    list_filter = ('organisation', 'role')
    search_fields = ('user__username', 'user__email', 'organisation__name')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organisation', 'location', 'client_name', 'current_stage')
    search_fields = ('name', 'client_name', 'organisation__name')
    list_filter = ('current_stage', 'organisation')


@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'deliverable', 'start_time', 'end_time', 'duration', 'remarks')
    list_filter = ('employee', 'deliverable', 'remarks')
    search_fields = ('employee__username', 'employee__email', 'deliverable__project__name', 'deliverable__name', 'remarks')
    date_hierarchy = 'start_time'
    raw_id_fields = ('employee', 'deliverable')

    def duration(self, obj):
        if obj.end_time and obj.start_time:
            delta = obj.end_time - obj.start_time
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "Not completed"
    duration.short_description = 'Duration'


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'stage_display', 'status_display', 'assignee', 'start_date', 'has_worklogs')
    list_filter = ('project', 'stage', 'status')
    search_fields = ('project__name', 'name', 'remarks')
    list_select_related = ('project', 'assignee')
    raw_id_fields = ('project', 'assignee', 'validator')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (None, {
            'fields': ('project', 'name', 'stage'),
            'description': 'Basic deliverable information'
        }),
        ('Status', {
            'fields': ('status', 'remarks'),
            'description': 'Note: Validation statuses (Ready/Passed/Failed/Discrepancy) require work logs.'
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'validation_date'),
            'classes': ('collapse',)
        }),
        ('Assignment', {
            'fields': ('assignee', 'validator'),
            'classes': ('collapse',)
        }),
    )

    def stage_display(self, obj):
        return obj.stage_name
    stage_display.short_description = 'Stage'
    stage_display.admin_order_field = 'stage'

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'

    def has_worklogs(self, obj):
        return obj.worklogs.exists()
    has_worklogs.boolean = True
    has_worklogs.short_description = 'Has Worklogs'

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, str(e), level=messages.ERROR)
        except Exception as e:
            self.message_user(request, f"An error occurred: {str(e)}", level=messages.ERROR)