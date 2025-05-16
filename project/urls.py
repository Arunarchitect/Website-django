from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProjectViewSet,
    WorkLogViewSet,
    DeliverableViewSet,
    MyMembershipsView,
    OrganisationListView, 
    OrganisationProjectsView,
    OrganisationMembersView,  # Add this import
    UserDetailView,
    UserOrganisationMembershipsView,
    UserAssignedDeliverablesView,
    UserWorkLogsView,
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'work-logs', WorkLogViewSet, basename='worklog')
router.register(r'deliverables', DeliverableViewSet, basename='deliverable')

urlpatterns = [
    path('', include(router.urls)),
    path('my-memberships/', MyMembershipsView.as_view(), name='my-memberships'),
    path('my-organisations/', OrganisationListView.as_view(), name='my-organisations'),
    path('organisations/<int:organisation_id>/projects/', OrganisationProjectsView.as_view(), name='organisation-projects'),
    path('organisations/<int:organisation_id>/members/', OrganisationMembersView.as_view(), name='organisation-members'),  # Add this line
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/organisations/', UserOrganisationMembershipsView.as_view(), name='user-organisations'),
    path('users/<int:user_id>/deliverables/', UserAssignedDeliverablesView.as_view(), name='user-deliverables'),
    path('users/<int:user_id>/worklogs/', UserWorkLogsView.as_view(), name='user-worklogs'),
]