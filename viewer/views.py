from rest_framework import viewsets, status, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Viewer, ProjectAccessKey, Tag, ViewerFile
from .serializers import (
    ViewerSerializer, 
    ProjectAccessKeySerializer,
    TagSerializer,
    ViewerFileSerializer
)

class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter tags by organisation and project if provided in query params.
        """
        queryset = Tag.objects.all()
        organisation_id = self.request.query_params.get('organisation_id')
        project_id = self.request.query_params.get('project_id')
        
        if organisation_id:
            queryset = queryset.filter(organisation_id=organisation_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            
        return queryset

class ViewerViewSet(viewsets.ModelViewSet):
    """
    Default authenticated API access to Viewer model.
    """
    queryset = Viewer.objects.all()
    serializer_class = ViewerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter by organisation and project if provided in query params.
        """
        queryset = Viewer.objects.all()
        organisation_id = self.request.query_params.get('organisation_id')
        project_id = self.request.query_params.get('project_id')
        
        if organisation_id:
            queryset = queryset.filter(organisation_id=organisation_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            
        return queryset

class ViewerFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing SVG files.
    """
    queryset = ViewerFile.objects.all()
    serializer_class = ViewerFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter by organisation and project if provided in query params.
        """
        queryset = ViewerFile.objects.all()
        organisation_id = self.request.query_params.get('organisation_id')
        project_id = self.request.query_params.get('project_id')
        
        if organisation_id:
            queryset = queryset.filter(organisation_id=organisation_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            
        return queryset

    @action(detail=True, methods=['post'])
    def add_tags(self, request, pk=None):
        """
        Add tags to a ViewerFile instance.
        """
        viewer_file = self.get_object()
        tag_ids = request.data.get('tag_ids', [])
        
        if not tag_ids:
            return Response(
                {"detail": "No tag IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify tags belong to the same organisation and project
        valid_tags = Tag.objects.filter(
            id__in=tag_ids,
            organisation=viewer_file.organisation,
            project=viewer_file.project
        )
        
        viewer_file.tags.add(*valid_tags)
        return Response(ViewerFileSerializer(viewer_file).data)

    @action(detail=True, methods=['post'])
    def remove_tags(self, request, pk=None):
        """
        Remove tags from a ViewerFile instance.
        """
        viewer_file = self.get_object()
        tag_ids = request.data.get('tag_ids', [])
        
        if not tag_ids:
            return Response(
                {"detail": "No tag IDs provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        viewer_file.tags.remove(*tag_ids)
        return Response(ViewerFileSerializer(viewer_file).data)

class ProjectAccessKeyViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    API endpoint for managing project access keys.
    """
    queryset = ProjectAccessKey.objects.all()
    serializer_class = ProjectAccessKeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter access keys by organisation and project if provided in query params.
        """
        queryset = ProjectAccessKey.objects.all()
        organisation_id = self.request.query_params.get('organisation_id')
        project_id = self.request.query_params.get('project_id')
        
        if organisation_id:
            queryset = queryset.filter(organisation_id=organisation_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
            
        return queryset

class Public360ImagesAPIView(APIView):
    """
    Public access to all 360 images for a project using access_key.
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
            "project": {
                "id": access.project.id,
                "name": access.project.name
            },
            "organisation": {
                "id": access.organisation.id,
                "name": access.organisation.name
            },
            "360_images": serializer.data
        })

class PublicSVGFilesAPIView(APIView):
    """
    Public access to all SVG files for a project using access_key.
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

        viewer_files = ViewerFile.objects.filter(
            project=access.project,
            organisation=access.organisation
        ).order_by('-view_date')

        serializer = ViewerFileSerializer(viewer_files, many=True, context={'request': request})
        
        return Response({
            "project": {
                "id": access.project.id,
                "name": access.project.name
            },
            "organisation": {
                "id": access.organisation.id,
                "name": access.organisation.name
            },
            "svg_files": serializer.data
        })

class PublicFileAccessAPIView(APIView):
    """
    Public access to individual files using access_key and file ID.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, access_key, file_type, file_id):
        try:
            access = ProjectAccessKey.objects.get(access_key=access_key)
        except ProjectAccessKey.DoesNotExist:
            return Response(
                {"detail": "Invalid access key."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if file_type == '360_image':
            try:
                viewer = Viewer.objects.get(
                    id=file_id,
                    project=access.project,
                    organisation=access.organisation
                )
                serializer = ViewerSerializer(viewer, context={'request': request})
                return Response(serializer.data)
            except Viewer.DoesNotExist:
                return Response(
                    {"detail": "File not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif file_type == 'svg_file':
            try:
                viewer_file = ViewerFile.objects.get(
                    id=file_id,
                    project=access.project,
                    organisation=access.organisation
                )
                serializer = ViewerFileSerializer(viewer_file, context={'request': request})
                return Response(serializer.data)
            except ViewerFile.DoesNotExist:
                return Response(
                    {"detail": "File not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        else:
            return Response(
                {"detail": "Invalid file type."},
                status=status.HTTP_400_BAD_REQUEST
            )