import csv
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Project, WorkLog, Deliverable
from .serializers import ProjectSerializer, WorkLogSerializer, DeliverableSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class WorkLogViewSet(viewsets.ModelViewSet):
    queryset = WorkLog.objects.all()
    serializer_class = WorkLogSerializer

    @action(detail=False, methods=['get'])
    def download_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="worklogs.csv"'

        writer = csv.writer(response)
        writer.writerow(['Employee', 'Deliverable', 'Project', 'Start Time', 'End Time', 'Duration (seconds)'])

        for worklog in self.get_queryset().select_related('employee', 'deliverable__project'):
            writer.writerow([
                worklog.employee.email,
                worklog.deliverable.name if worklog.deliverable else '',
                worklog.deliverable.project.name if worklog.deliverable and worklog.deliverable.project else '',
                worklog.start_time,
                worklog.end_time,
                worklog.duration if worklog.duration else '',
            ])

        return response


class DeliverableViewSet(viewsets.ModelViewSet):
    queryset = Deliverable.objects.all()
    serializer_class = DeliverableSerializer

    @action(detail=False, methods=['get'])
    def download_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="deliverables.csv"'

        writer = csv.writer(response)
        writer.writerow(['Project', 'Deliverable Name', 'Stage', 'Status', 'Remarks', 'Start Date', 'End Date'])

        for deliverable in self.get_queryset().select_related('project'):
            writer.writerow([
                deliverable.project.name if deliverable.project else '',
                deliverable.name,
                deliverable.get_stage_display(),
                deliverable.get_status_display(),
                deliverable.remarks,
                deliverable.start_date,
                deliverable.end_date,
            ])

        return response
