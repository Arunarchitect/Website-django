from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ViewerViewSet, 
    Public360ImagesAPIView,
    PublicSVGFilesAPIView,
    TagViewSet,
    ViewerFileViewSet,
    ProjectAccessKeyViewSet
)

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'viewer-files', ViewerFileViewSet, basename='viewerfile')
router.register(r'access-keys', ProjectAccessKeyViewSet, basename='projectaccesskey')
router.register(r'viewers', ViewerViewSet, basename='viewer')

urlpatterns = [
    path('public/360-images/<str:access_key>/', Public360ImagesAPIView.as_view(), name='public-360-images'),
    path('public/svg-files/<str:access_key>/', PublicSVGFilesAPIView.as_view(), name='public-svg-files'),
    path('', include(router.urls)),
]