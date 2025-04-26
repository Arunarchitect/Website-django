from django.contrib import admin
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
    list_display = ('id', 'employee',  'deliverable', 'start_time', 'end_time', 'duration')
    list_filter = ( 'employee', 'deliverable')
    search_fields = ('employee__username', 'employee__email', 'project__name', 'deliverable__name')

    def duration(self, obj):
        return obj.duration


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'name', 'stage', 'status', 'remarks')
    list_filter = ('project', 'stage', 'status')
    search_fields = ('project__name', 'name', 'remarks')
