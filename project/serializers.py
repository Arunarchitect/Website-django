from rest_framework import serializers
from .models import (
    Organisation,
    OrganisationMembership,
    Project,
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
        
class SimpleProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'location', 'client_name', 'current_stage']



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


class DeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliverable
        fields = ['id', 'project', 'name', 'stage', 'status', 'remarks', 'start_date', 'end_date']


class WorkLogSerializer(serializers.ModelSerializer):
    deliverable_name = serializers.SerializerMethodField()

    class Meta:
        model = WorkLog
        fields = '__all__'
        read_only_fields = ['employee']

    def get_deliverable_name(self, obj):
        return obj.deliverable.name if obj.deliverable else None
