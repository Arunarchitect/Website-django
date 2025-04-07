from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from rest_framework import viewsets
from .models import Project, WorkLog, WorkType
from .serializers import ProjectSerializer, WorkLogSerializer, WorkTypeSerializer
from django.utils import timezone

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        project = self.get_object()
        logs = WorkLog.objects.filter(project=project, end_time__isnull=False)

        total = logs.aggregate(
            duration=Sum(ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField()))
        )['duration']

        work_summary = (
            logs.values('work_type__name')
            .annotate(
                duration=Sum(ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField()))
            )
        )

        return Response({
            'project': project.name,
            'total_duration': total,
            'work_types': [
                {'name': w['work_type__name'], 'duration': w['duration']} for w in work_summary
            ]
        })

class WorkTypeViewSet(viewsets.ModelViewSet):
    queryset = WorkType.objects.all()
    serializer_class = WorkTypeSerializer

class WorkLogViewSet(viewsets.ModelViewSet):
    queryset = WorkLog.objects.all()
    serializer_class = WorkLogSerializer
