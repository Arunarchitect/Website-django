# viewer/serializers.py

from rest_framework import serializers
from .models import Viewer
from django.contrib.auth import get_user_model
from project.models import Project, Organisation

User = get_user_model()

class ViewerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    organisation = serializers.PrimaryKeyRelatedField(queryset=Organisation.objects.all())
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Viewer
        fields = [
            'id',
            'user',
            'organisation',
            'project',
            'view_name',
            'view_date',
            'image_360',
            'created_at',
        ]
        read_only_fields = ['created_at']
