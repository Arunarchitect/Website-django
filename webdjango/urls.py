from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import HttpResponse

from project.views import ProjectViewSet, WorkLogViewSet, DeliverableViewSet

# DRF ViewSets
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'work-logs', WorkLogViewSet, basename='worklog')
router.register(r'deliverables', DeliverableViewSet, basename='deliverable')

urlpatterns = [
    path('', lambda request: HttpResponse("It works!"), name='home'),  # Root page
    path('admin/', admin.site.urls),

    # Custom apps
    path('fees/', include('fees.urls')),
    path('expenses/', include('expense.urls')),

    # API endpoints
    path('api/', include('djoser.urls')),           # Auth routes (e.g., login, logout, etc.)
    path('api/', include('users.urls')),            # Custom user endpoints
    path('api/', include('project.urls')),         # Project-specific non-ViewSet endpoints
    path('api/', include(router.urls)),             # REST API for projects, worklogs, deliverables
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
