# viewer/admin.py

from django.contrib import admin
from .models import Viewer

@admin.register(Viewer)
class ViewerAdmin(admin.ModelAdmin):
    list_display = ('view_name', 'project', 'organisation', 'user', 'view_date')
    list_filter = ('project', 'organisation', 'view_date')
