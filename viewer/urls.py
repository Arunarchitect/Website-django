# viewer/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ViewerViewSet

router = DefaultRouter()
router.register(r'', ViewerViewSet, basename='viewer')  # Empty prefix or 'viewers' as you want

urlpatterns = [
    path('', include(router.urls)),
]
