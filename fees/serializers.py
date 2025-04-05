# fees/serializers.py

from rest_framework import serializers
from .models import Fee, PromoCode

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ['code', 'discount_percentage']

class FeeSerializer(serializers.ModelSerializer):
    promo_code = PromoCodeSerializer()

    class Meta:
        model = Fee
        fields = ['base_fee_per_sqft', 'promo_code']
