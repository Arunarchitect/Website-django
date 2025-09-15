from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Viewer, ProjectAccessKey
from .serializers import ViewerSerializer
from rest_framework.permissions import AllowAny

class ViewerViewSet(viewsets.ModelViewSet):
    """
    Default authenticated API access to Viewer model.
    """
    queryset = Viewer.objects.all()
    serializer_class = ViewerSerializer
    permission_classes = [AllowAny]  # Or change to IsAuthenticated if you want auth

class PublicViewerAccessAPIView(APIView):
    """
    Public (unauthenticated) access to project views using access_key.
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Disable authentication for public access

    def get(self, request, access_key):
        try:
            access = ProjectAccessKey.objects.get(access_key=access_key)
        except ProjectAccessKey.DoesNotExist:
            return Response(
                {"detail": "Invalid access key."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        viewers = Viewer.objects.filter(
            project=access.project,
            organisation=access.organisation
        ).order_by('-view_date')

        serializer = ViewerSerializer(viewers, many=True, context={'request': request})
        return Response({
            "project": access.project.name,
            "organisation": access.organisation.name,
            "views": serializer.data
        })
