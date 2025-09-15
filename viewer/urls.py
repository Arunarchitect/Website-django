# viewer/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ViewerViewSet, PublicViewerAccessAPIView

router = DefaultRouter()
router.register(r'', ViewerViewSet, basename='viewer')

urlpatterns = [
    path('public/<str:access_key>/', PublicViewerAccessAPIView.as_view(), name='public-viewer-access'),
    path('', include(router.urls)),
]
