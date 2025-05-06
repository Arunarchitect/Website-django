from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProjectViewSet,
    WorkLogViewSet,
    DeliverableViewSet,
    MyMembershipsView,  # Importing the view
    OrganisationListView, OrganisationProjectsView
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'work-logs', WorkLogViewSet, basename='worklog')
router.register(r'deliverables', DeliverableViewSet, basename='deliverable')

urlpatterns = [
    path('', include(router.urls)),
    path('my-memberships/', MyMembershipsView.as_view(), name='my-memberships'),  # Add custom view
    path('my-organisations/', OrganisationListView.as_view(), name='my-organisations'),
    path('organisations/<int:organisation_id>/projects/', OrganisationProjectsView.as_view(), name='organisation-projects'),
]
