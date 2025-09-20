from rest_framework import serializers
from django.contrib.auth import get_user_model
from project.models import Project, Organisation
from .models import Viewer, ProjectAccessKey, Tag, ViewerFile

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'organisation', 'project']
        read_only_fields = ['id']


class ViewerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    organisation = serializers.PrimaryKeyRelatedField(queryset=Organisation.objects.all())
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    image_360_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Viewer
        fields = [
            'id', 'user', 'organisation', 'project', 'view_name', 'view_date',
            'image_360', 'image_360_url', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_image_360_url(self, obj):
        if obj.image_360:
            return obj.image_360.url
        return None

    def validate(self, data):
        """Validate that project belongs to organisation."""
        organisation = data.get('organisation')
        project = data.get('project')
        
        if project and organisation and project.organisation != organisation:
            raise serializers.ValidationError(
                "Project does not belong to the specified organisation."
            )
        return data


class ViewerFileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    organisation = serializers.PrimaryKeyRelatedField(queryset=Organisation.objects.all())
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)
    tag_names = serializers.SerializerMethodField(read_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ViewerFile
        fields = [
            'id', 'user', 'organisation', 'project', 'view_name', 'view_date',
            'file', 'file_url', 'description', 'tags', 'tag_names', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_tag_names(self, obj):
        return list(obj.tags.values_list('name', flat=True))

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None

    def validate(self, data):
        """Validate that project belongs to organisation and tags belong to same org/project."""
        organisation = data.get('organisation')
        project = data.get('project')
        tags = data.get('tags', [])
        
        if project and organisation and project.organisation != organisation:
            raise serializers.ValidationError(
                "Project does not belong to the specified organisation."
            )
        
        for tag in tags:
            if tag.organisation != organisation or tag.project != project:
                raise serializers.ValidationError(
                    f"Tag '{tag.name}' does not belong to the same organisation and project."
                )
        
        return data


class ProjectAccessKeySerializer(serializers.ModelSerializer):
    organisation = serializers.PrimaryKeyRelatedField(queryset=Organisation.objects.all())
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    organisation_name = serializers.CharField(source='organisation.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = ProjectAccessKey
        fields = [
            'id', 'organisation', 'organisation_name', 'project', 
            'project_name', 'access_key'
        ]
        read_only_fields = ['access_key']


# Public serializers (for unauthenticated access)
class PublicTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class PublicViewerSerializer(serializers.ModelSerializer):
    image_360_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Viewer
        fields = ['id', 'view_name', 'view_date', 'image_360_url', 'created_at']

    def get_image_360_url(self, obj):
        if obj.image_360:
            return obj.image_360.url
        return None


class PublicViewerFileSerializer(serializers.ModelSerializer):
    tags = PublicTagSerializer(many=True, read_only=True)
    tag_names = serializers.SerializerMethodField(read_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ViewerFile
        fields = [
            'id', 'view_name', 'view_date', 'file_url', 
            'description', 'tags', 'tag_names', 'created_at'
        ]

    def get_tag_names(self, obj):
        return list(obj.tags.values_list('name', flat=True))

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None