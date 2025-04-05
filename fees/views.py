# fees/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Fee, PromoCode

class FeeWithPromoAPIView(APIView):
    def get(self, request):
        promo_code = request.query_params.get('promo_code', '').strip()

        fee = None
        if promo_code:
            try:
                promo = PromoCode.objects.get(code__iexact=promo_code)
                fee = Fee.objects.filter(promo_code=promo).first()
            except PromoCode.DoesNotExist:
                return Response({'error': 'No valid promo code.'}, status=status.HTTP_400_BAD_REQUEST)

        if not fee:
            fee = Fee.objects.filter(promo_code__isnull=True).first()

        if not fee:
            return Response({'error': 'Fee data not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'base_fee_per_sqft': float(fee.base_fee_per_sqft),
            'promo_code': promo_code or None
        })
