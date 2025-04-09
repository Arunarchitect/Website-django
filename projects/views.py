from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from rest_framework import viewsets
from .models import Project, WorkLog, WorkType, Deliverable
from .serializers import ProjectSerializer, WorkLogSerializer, WorkTypeSerializer, DeliverableSerializer


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

        deliverables = project.deliverables.values('name', 'stage', 'status', 'remarks')

        return Response({
            'project': project.name,
            'current_stage': project.current_stage,
            'total_duration': total.total_seconds() if total else 0,
            'work_types': [
                {
                    'name': w['work_type__name'],
                    'duration': w['duration'].total_seconds() if w['duration'] else 0
                }
                for w in work_summary
            ],
            'deliverables': list(deliverables)
        })


class WorkTypeViewSet(viewsets.ModelViewSet):
    queryset = WorkType.objects.all()
    serializer_class = WorkTypeSerializer


class WorkLogViewSet(viewsets.ModelViewSet):
    queryset = WorkLog.objects.all()
    serializer_class = WorkLogSerializer


class DeliverableViewSet(viewsets.ModelViewSet):
    queryset = Deliverable.objects.all()
    serializer_class = DeliverableSerializer
