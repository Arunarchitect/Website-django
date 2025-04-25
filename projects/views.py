from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.db.models import Sum, F, ExpressionWrapper, DurationField

from .models import Project, WorkLog, WorkType, Deliverable
from .serializers import ProjectSerializer, WorkLogSerializer, WorkTypeSerializer, DeliverableSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        project = self.get_object()
        logs = WorkLog.objects.filter(project=project, end_time__isnull=False)

        total_duration = logs.aggregate(
            duration=Sum(
                ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
            )
        )['duration']

        work_summary = logs.values('work_type__name').annotate(
            duration=Sum(
                ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
            )
        )

        deliverables = project.deliverables.values('work_type__name', 'stage', 'status', 'remarks')

        return Response({
            'project': project.name,
            'current_stage': project.current_stage,
            'total_duration_seconds': total_duration.total_seconds() if total_duration else 0,
            'work_types': [
                {
                    'name': item['work_type__name'],
                    'duration_seconds': item['duration'].total_seconds() if item['duration'] else 0
                }
                for item in work_summary
            ],
            'deliverables': [
                {
                    'name': d['work_type__name'],
                    'stage': d['stage'],
                    'status': d['status'],
                    'remarks': d['remarks']
                }
                for d in deliverables
            ]
        })


class WorkTypeViewSet(viewsets.ModelViewSet):
    queryset = WorkType.objects.all()
    serializer_class = WorkTypeSerializer


class WorkLogViewSet(viewsets.ModelViewSet):
    queryset = WorkLog.objects.all()
    serializer_class = WorkLogSerializer

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)  # Automatically sets the logged-in user


class DeliverableViewSet(viewsets.ModelViewSet):
    queryset = Deliverable.objects.all()
    serializer_class = DeliverableSerializer
