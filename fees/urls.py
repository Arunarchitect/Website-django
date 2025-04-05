# fees/urls.py

from django.urls import path
from .views import FeeWithPromoAPIView

urlpatterns = [
    path('fee/', FeeWithPromoAPIView.as_view(), name='fee-with-promo'),
]
