from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, WorkTypeViewSet, WorkLogViewSet, DeliverableViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'work-types', WorkTypeViewSet)
router.register(r'work-logs', WorkLogViewSet)
router.register(r'deliverables', DeliverableViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
