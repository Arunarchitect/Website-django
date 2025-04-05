# fees/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Fee

class FeeWithPromoAPIView(APIView):
    def get(self, request):
        promo_code = request.query_params.get('promo_code', '').strip()
        fee = Fee.objects.first()  # Assuming one fee record for now

        if not fee:
            return Response({'error': 'Fee data not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'base_fee_per_sqft': float(fee.base_fee_per_sqft),
            'promo_code': promo_code or None
        })
