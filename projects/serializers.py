from rest_framework import serializers
from .models import Project, WorkType, WorkLog, Deliverable

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


class DeliverableSerializer(serializers.ModelSerializer):
    # Reference to work_type.name as the name field
    name = serializers.CharField(source='work_type.name', read_only=True)  # this makes name show up like before

    class Meta:
        model = Deliverable
        fields = ['id', 'project', 'work_type', 'name', 'stage', 'status', 'remarks']
        # Optionally, you can specify read_only=True for related fields if they shouldn't be directly modifiable
        read_only_fields = ['project', 'work_type']
