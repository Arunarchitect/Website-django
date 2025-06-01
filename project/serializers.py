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
        fields = ['id', 'project', 'name', 'stage', 'status', 'remarks', 'start_date', 'end_date', 'assignee']


class WorkLogSerializer(serializers.ModelSerializer):
    deliverable_name = serializers.SerializerMethodField()
    employee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = WorkLog
        fields = '__all__'
        read_only_fields = ['employee']  # Employee is set automatically on create

    def get_deliverable_name(self, obj):
        return obj.deliverable.name if obj.deliverable else None

    def validate(self, data):
        """
        Validate time ranges and other business logic
        """
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] > data['end_time']:
                raise serializers.ValidationError("End time must be after start time")
        
        # Add other validations as needed
        return data

    def create(self, validated_data):
        """Ensure employee is set to current user on creation"""
        validated_data['employee'] = self.context['request'].user
        return super().create(validated_data)



# Add these new serializers to your existing serializers.py
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone']

class UserOrganisationMembershipSerializer(serializers.ModelSerializer):
    organisation = OrganisationSerializer()
    
    class Meta:
        model = OrganisationMembership
        fields = ['id', 'organisation', 'role']

class UserDeliverableSerializer(serializers.ModelSerializer):
    project = SimpleProjectSerializer()
    stage_name = serializers.CharField(source='get_stage_display', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Deliverable
        fields = ['id', 'name', 'project', 'stage', 'stage_name', 'status', 'status_name', 
                 'start_date', 'end_date', 'validation_date']

class UserWorkLogSerializer(serializers.ModelSerializer):
    deliverable = serializers.StringRelatedField()
    project = serializers.SerializerMethodField()
    organisation = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = WorkLog
        fields = ['id', 'deliverable', 'project', 'organisation', 'start_time', 'end_time', 'duration', 'remarks']

    def get_project(self, obj):
        return obj.deliverable.project.name if obj.deliverable and obj.deliverable.project else None

    def get_organisation(self, obj):
        if obj.deliverable and obj.deliverable.project and obj.deliverable.project.organisation:
            return obj.deliverable.project.organisation.name
        return None

    def get_duration(self, obj):
        if obj.end_time and obj.start_time:
            return (obj.end_time - obj.start_time).total_seconds() / 3600  # in hours
        return None
