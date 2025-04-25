from rest_framework import serializers
from .models import (
    Organisation,
    OrganisationMembership,
    Project,
    WorkType,
    WorkLog,
    Deliverable
)
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['id', 'name']


class OrganisationMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')

    class Meta:
        model = OrganisationMembership
        fields = ['id', 'organisation', 'user', 'user_id', 'role']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = '__all__'


class WorkLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLog
        fields = '__all__'
        read_only_fields = ['employee']


class DeliverableSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='work_type.name', read_only=True)

    class Meta:
        model = Deliverable
        fields = ['id', 'project', 'work_type', 'name', 'stage', 'status', 'remarks']
        read_only_fields = ['project', 'work_type']
