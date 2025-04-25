from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from projects.views import ProjectViewSet, WorkTypeViewSet, WorkLogViewSet, DeliverableViewSet
from django.http import HttpResponse


router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'work-types', WorkTypeViewSet)
router.register(r'work-logs', WorkLogViewSet)
router.register(r'deliverables', DeliverableViewSet)

urlpatterns = [
    path('', lambda request: HttpResponse("It works!"), name='home'),  # Root page
    path('admin/', admin.site.urls),
    path('fees/', include('fees.urls')),  # This adds the endpoint at /fees/
    path('expenses/', include('expense.urls')),  # This adds the endpoint at /expenses/
    
    # Add /api/ prefix for your API-related endpoints
    path('api/', include('djoser.urls')),  # This adds the API routes for djoser
    path('api/', include('users.urls')),   # This adds the API routes for users
    path('api/', include('projects.urls')),  # This adds the API routes for projects under /api/projects/

    # Include the router URLs for the new views
    path('api/', include(router.urls)),  # This adds the API endpoints for projects, work types, work logs, deliverables
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
