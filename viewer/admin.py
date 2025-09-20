from django.contrib import admin
from .models import Viewer, ProjectAccessKey, Tag, ViewerFile

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'organisation')
    list_filter = ('project', 'organisation', 'name')
    search_fields = ('name', 'project__name', 'organisation__name')
    readonly_fields = ('id',)


@admin.register(Viewer)
class ViewerAdmin(admin.ModelAdmin):
    list_display = ('view_name', 'project', 'organisation', 'user', 'view_date')
    list_filter = ('project', 'organisation', 'view_date')
    search_fields = ('view_name', 'project__name', 'organisation__name')
    readonly_fields = ('id', 'created_at')


@admin.register(ViewerFile)
class ViewerFileAdmin(admin.ModelAdmin):
    list_display = ('view_name', 'project', 'organisation', 'user', 'view_date')
    list_filter = ('project', 'organisation', 'view_date', 'tags')
    search_fields = ( 'view_name', 'project__name', 'organisation__name')
    filter_horizontal = ('tags',)  # Better interface for many-to-many field
    readonly_fields = ('id', 'created_at')


@admin.register(ProjectAccessKey)
class ProjectAccessKeyAdmin(admin.ModelAdmin):
    list_display = ('access_key', 'project', 'organisation')
    search_fields = ('access_key', 'project__name', 'organisation__name')
    list_filter = ('project', 'organisation')
    readonly_fields = ('id', 'access_key')

    def save_model(self, request, obj, form, change):
        """
        Allow automatic generation of access_key if it's blank.
        """
        if not obj.access_key:
            obj.save()  # triggers auto-generation in model's save()
        else:
            super().save_model(request, obj, form, change)