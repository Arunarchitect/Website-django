from django.urls import path
from .views import FeeWithPromoAPIView

urlpatterns = [
    path('fees/', FeeWithPromoAPIView.as_view(), name='fee-api'),
]