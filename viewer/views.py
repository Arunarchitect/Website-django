# viewer/views.py

from rest_framework import viewsets
from .models import Viewer
from .serializers import ViewerSerializer

class ViewerViewSet(viewsets.ModelViewSet):
    queryset = Viewer.objects.all()
    serializer_class = ViewerSerializer
