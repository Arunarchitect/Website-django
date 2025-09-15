# viewer/admin.py

from django.contrib import admin
from .models import Viewer, ProjectAccessKey

@admin.register(Viewer)
class ViewerAdmin(admin.ModelAdmin):
    list_display = ('view_name', 'project', 'organisation', 'user', 'view_date')
    list_filter = ('project', 'organisation', 'view_date')


@admin.register(ProjectAccessKey)
class ProjectAccessKeyAdmin(admin.ModelAdmin):
    list_display = ('access_key', 'project', 'organisation')
    search_fields = ('access_key', 'project__name', 'organisation__name')
    list_filter = ('project', 'organisation')


    def save_model(self, request, obj, form, change):
        """
        Allow automatic generation of access_key if it's blank.
        """
        if not obj.access_key:
            obj.save()  # triggers auto-generation in model's save()
        else:
            super().save_model(request, obj, form, change)
