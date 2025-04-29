from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from django.http import HttpResponse
import csv

from .models import Project, WorkLog, Deliverable
from .serializers import ProjectSerializer, WorkLogSerializer, DeliverableSerializer, OrganisationMembershipSerializer
# views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import OrganisationMembership

class MyMembershipsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = OrganisationMembership.objects.filter(user=request.user)
        serializer = OrganisationMembershipSerializer(memberships, many=True)
        return Response(serializer.data)





class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        project = self.get_object()

        logs = WorkLog.objects.filter(deliverable__project=project, end_time__isnull=False)

        total_duration = logs.aggregate(
            duration=Sum(
                ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
            )
        )['duration']

        work_summary = logs.values('deliverable__name').annotate(
            duration=Sum(
                ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())
            )
        )

        deliverables = project.deliverables.values('name', 'stage', 'status', 'remarks')

        return Response({
            'project': project.name,
            'current_stage': project.current_stage,
            'total_duration_seconds': total_duration.total_seconds() if total_duration else 0,
            'deliverables_summary': [
                {
                    'name': item['deliverable__name'],
                    'duration_seconds': item['duration'].total_seconds() if item['duration'] else 0
                }
                for item in work_summary
            ],
            'deliverables': list(deliverables)
        })


class WorkLogViewSet(viewsets.ModelViewSet):
    queryset = WorkLog.objects.all()
    serializer_class = WorkLogSerializer

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    @action(detail=False, methods=['get'], url_path='download-csv')
    def download_csv(self, request):
        logs = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="worklogs.csv"'

        writer = csv.writer(response)
        writer.writerow(['Employee', 'Deliverable', 'Start Time', 'End Time', 'Remarks'])

        for log in logs:
            writer.writerow([
                log.employee.username if log.employee else '',
                log.deliverable.name if log.deliverable else '',
                log.start_time,
                log.end_time,
                log.remarks,
            ])

        return response


class DeliverableViewSet(viewsets.ModelViewSet):
    queryset = Deliverable.objects.all()
    serializer_class = DeliverableSerializer

    @action(detail=False, methods=['get'], url_path='download-csv')
    def download_csv(self, request):
        deliverables = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="deliverables.csv"'

        writer = csv.writer(response)
        writer.writerow(['Project', 'Name', 'Stage', 'Status', 'Remarks'])

        for deliverable in deliverables:
            writer.writerow([
                deliverable.project.name if deliverable.project else '',
                deliverable.name,
                deliverable.stage,
                deliverable.status,
                deliverable.remarks,
            ])

        return response
