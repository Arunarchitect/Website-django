from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Fee
from .serializers import FeeSerializer

class FeeWithPromoAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        promo_code = request.query_params.get('promo_code', '').strip()

        try:
            fee = Fee.objects.filter(promo_code__iexact=promo_code).first()
            if not fee:
                fee = Fee.objects.filter(promo_code__isnull=True).first()

            if not fee:
                return Response(
                    {'error': 'Fee data not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Use the serializer to return all fields
            serializer = FeeSerializer(fee)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
