from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, CategoryViewSet, ItemViewSet, BrandViewSet, ShopViewSet

router = DefaultRouter()
router.register('expenses', ExpenseViewSet)
router.register('categories', CategoryViewSet)
router.register('items', ItemViewSet)
router.register('brands', BrandViewSet)
router.register('shops', ShopViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
