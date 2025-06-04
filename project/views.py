from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from django.http import HttpResponse
import csv
from io import TextIOWrapper
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Project, WorkLog, Deliverable
from .serializers import ProjectSerializer, WorkLogSerializer, DeliverableSerializer, OrganisationMembershipSerializer, UserDetailSerializer,UserOrganisationMembershipSerializer,  UserDeliverableSerializer, UserWorkLogSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import OrganisationMembership,Organisation, Project, Expense
from .serializers import OrganisationSerializer, SimpleProjectSerializer, ExpenseSerializer




User = get_user_model()

class MyMembershipsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = OrganisationMembership.objects.filter(user=request.user)
        serializer = OrganisationMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
    
    
class OrganisationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all organisations where user is a member
        memberships = OrganisationMembership.objects.filter(user=request.user)
        organisations = Organisation.objects.filter(memberships__in=memberships).distinct()
        serializer = OrganisationSerializer(organisations, many=True)
        return Response(serializer.data)

class OrganisationProjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, organisation_id):
        # Check if user is a member of this organisation
        if not OrganisationMembership.objects.filter(user=request.user, organisation_id=organisation_id).exists():
            return Response({'detail': 'Not authorized for this organisation.'}, status=403)

        # Get projects inside this organisation
        projects = Project.objects.filter(organisation_id=organisation_id)
        serializer = SimpleProjectSerializer(projects, many=True)
        return Response(serializer.data)
    

from django.db.models import F, Sum, ExpressionWrapper, DurationField
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Project, WorkLog
from .serializers import ProjectSerializer

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

        # Include assignee's name in deliverables
        deliverables = project.deliverables.select_related('assignee').values(
            'name',
            'stage',
            'status',
            'end_date',
            'assignee',
            'assignee__first_name',
            'assignee__last_name',
            'remarks'
        )

        # Add full name
        deliverables_list = []
        for d in deliverables:
            d['assignee_name'] = f"{d['assignee__first_name']} {d['assignee__last_name']}".strip() if d['assignee'] else None
            deliverables_list.append(d)

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
            'deliverables': deliverables_list
        })

class WorkLogViewSet(viewsets.ModelViewSet):
    queryset = WorkLog.objects.all()
    serializer_class = WorkLogSerializer

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    @action(detail=False, methods=['get'])
    def download_csv(self, request):
        logs = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="worklogs.csv"'

        writer = csv.writer(response)
        writer.writerow(['Employee', 'Project', 'Deliverable', 'Start Time', 'End Time', 'remarks'])

        for log in logs:
            writer.writerow([
                log.employee.email if log.employee else '',
                log.deliverable.project.name if log.deliverable and log.deliverable.project else '',
                log.deliverable.name if log.deliverable else '',
                log.start_time,
                log.end_time,
            ])

        return response

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        # Check file size (e.g., max 5MB)
        if request.FILES['file'].size > 5 * 1024 * 1024:
            return Response({'error': 'File size exceeds the 5MB limit.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
        reader = csv.DictReader(csv_file)

        required_fields = ['Employee', 'Project', 'Deliverable', 'Start Time']
        if not all(field in reader.fieldnames for field in required_fields):
            return Response(
                {'error': f'CSV file must contain these columns: {", ".join(required_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_count = 0
        updated_count = 0
        errors = []

        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                try:
                    employee_email = row['Employee'].strip()
                    project_name = row['Project'].strip()
                    deliverable_name = row['Deliverable'].strip()
                    start_time_str = row['Start Time'].strip()
                    end_time_str = row.get('End Time', '').strip()

                    # Validate employee
                    try:
                        employee = User.objects.get(email=employee_email)
                    except User.DoesNotExist:
                        errors.append(f"Row {row_num}: Employee with email '{employee_email}' not found")
                        continue

                    # Validate project
                    try:
                        project = Project.objects.get(name=project_name)
                    except Project.DoesNotExist:
                        errors.append(f"Row {row_num}: Project '{project_name}' not found")
                        continue

                    # Get or create deliverable
                    deliverable, _ = Deliverable.objects.get_or_create(
                        project=project,
                        name=deliverable_name,
                        defaults={'stage': project.current_stage, 'status': 'ongoing'}
                    )

                    # Parse timestamps
                    try:
                        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S%z')
                    except ValueError:
                        try:
                            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            errors.append(f"Row {row_num}: Invalid Start Time format. Use 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD HH:MM:SS+TZ'")
                            continue

                    end_time = None
                    if end_time_str:
                        try:
                            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S%z')
                        except ValueError:
                            try:
                                end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                errors.append(f"Row {row_num}: Invalid End Time format. Use 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD HH:MM:SS+TZ'")
                                continue

                    # Create or update worklog
                    _, created = WorkLog.objects.update_or_create(
                        employee=employee,
                        deliverable=deliverable,
                        start_time=start_time,
                        defaults={'end_time': end_time}
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    continue

        response_data = {
            'message': 'CSV import completed',
            'created': created_count,
            'updated': updated_count,
        }

        if errors:
            response_data['error_count'] = len(errors)
            response_data['errors'] = errors
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

        return Response(response_data, status=status.HTTP_201_CREATED)

class DeliverableViewSet(viewsets.ModelViewSet):
    queryset = Deliverable.objects.all()
    serializer_class = DeliverableSerializer

    @action(detail=False, methods=['get'])
    def download_csv(self, request):
        deliverables = self.get_queryset()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="deliverables.csv"'

        writer = csv.writer(response)
        writer.writerow(['Project', 'Name', 'Stage', 'Status', 'Remarks', 'Start Date', 'End Date'])

        for deliverable in deliverables:
            writer.writerow([
                deliverable.project.name if deliverable.project else '',
                deliverable.name,
                deliverable.stage,
                deliverable.status,
                deliverable.remarks,
                deliverable.start_date.strftime('%Y-%m-%d') if deliverable.start_date else '',
                deliverable.end_date.strftime('%Y-%m-%d') if deliverable.end_date else '',
            ])

        return response

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        # Check file size (e.g., max 5MB)
        if request.FILES['file'].size > 5 * 1024 * 1024:
            return Response({'error': 'File size exceeds the 5MB limit.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
        reader = csv.DictReader(csv_file)

        required_fields = ['Project', 'Name', 'Stage']
        if not all(field in reader.fieldnames for field in required_fields):
            return Response(
                {'error': f'CSV file must contain these columns: {", ".join(required_fields)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_count = 0
        updated_count = 0
        errors = []

        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                try:
                    project_name = row['Project'].strip()
                    name = row['Name'].strip()
                    stage = row['Stage'].strip()
                    status_val = row.get('Status', 'not_started').strip()
                    remarks = row.get('Remarks', '').strip()
                    start_date_str = row.get('Start Date', '').strip()
                    end_date_str = row.get('End Date', '').strip()

                    # Validate project
                    try:
                        project = Project.objects.get(name=project_name)
                    except Project.DoesNotExist:
                        errors.append(f"Row {row_num}: Project '{project_name}' not found")
                        continue

                    # Parse dates
                    try:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
                        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid date format. Use 'YYYY-MM-DD'")
                        continue

                    # Create or update deliverable
                    deliverable, created = Deliverable.objects.update_or_create(
                        project=project,
                        name=name,
                        defaults={'stage': stage, 'status': status_val, 'remarks': remarks, 'start_date': start_date, 'end_date': end_date}
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    continue

        response_data = {
            'message': 'CSV import completed',
            'created': created_count,
            'updated': updated_count,
        }

        if errors:
            response_data['error_count'] = len(errors)
            response_data['errors'] = errors
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

        return Response(response_data, status=status.HTTP_201_CREATED)

# Add this class to your views.py
class OrganisationMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, organisation_id):
        # Check if user is a member of this organisation
        if not OrganisationMembership.objects.filter(
            user=request.user, 
            organisation_id=organisation_id
        ).exists():
            return Response(
                {'detail': 'Not authorized for this organisation.'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Get all members of this organisation
        members = OrganisationMembership.objects.filter(
            organisation_id=organisation_id
        ).select_related('user')
        
        serializer = OrganisationMembershipSerializer(members, many=True)
        return Response(serializer.data)
    
    
    
    
# Add these new views to your existing views.py
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Check if requesting user has permission to view this user's details
        # For simplicity, we'll allow if they share any organization
        if not OrganisationMembership.objects.filter(
            user=request.user,
            organisation__in=OrganisationMembership.objects.filter(user_id=user_id).values('organisation')
        ).exists():
            return Response({'detail': 'Not authorized to view this user.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

class UserOrganisationMembershipsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Similar permission check as above
        if not OrganisationMembership.objects.filter(
            user=request.user,
            organisation__in=OrganisationMembership.objects.filter(user_id=user_id).values('organisation')
        ).exists():
            return Response({'detail': 'Not authorized to view this user.'}, status=status.HTTP_403_FORBIDDEN)

        memberships = OrganisationMembership.objects.filter(user_id=user_id).select_related('organisation')
        serializer = UserOrganisationMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

class UserAssignedDeliverablesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Similar permission check
        if not OrganisationMembership.objects.filter(
            user=request.user,
            organisation__in=OrganisationMembership.objects.filter(user_id=user_id).values('organisation')
        ).exists():
            return Response({'detail': 'Not authorized to view this user.'}, status=status.HTTP_403_FORBIDDEN)

        deliverables = Deliverable.objects.filter(assignee_id=user_id).select_related('project', 'project__organisation')
        serializer = UserDeliverableSerializer(deliverables, many=True)
        return Response(serializer.data)

class UserWorkLogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Check if request.user shares any organisation with the user_id
        if not OrganisationMembership.objects.filter(
            user=request.user,
            organisation__in=OrganisationMembership.objects.filter(user_id=user_id).values('organisation')
        ).exists():
            return Response({'detail': 'Not authorized to view this user.'}, status=status.HTTP_403_FORBIDDEN)

        worklogs = WorkLog.objects.filter(employee_id=user_id).select_related(
            'deliverable',
            'deliverable__project',
            'deliverable__project__organisation'
        )
        serializer = UserWorkLogSerializer(worklogs, many=True)
        return Response(serializer.data)

    
    
    
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns different querysets based on user role:
        - Regular users see only their own expenses
        - Admin users see all expenses
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Expense.objects.all().select_related('user', 'project')
        return Expense.objects.filter(user=user).select_related('user', 'project')

    def perform_create(self, serializer):
        """Automatically set the user to the current user when creating an expense"""
        serializer.save(user=self.request.user)

    def get_permissions(self):
        """
        Only allow admin users to use the 'admin_list' action
        """
        if self.action == 'admin_list':
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='admin-list')
    def admin_list(self, request):
        """
        Special endpoint for admin users to view all expenses with additional filtering options
        """
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(
                {'detail': 'You do not have permission to access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Provides summary statistics about expenses
        """
        user = request.user
        queryset = self.get_queryset()

        # Basic summary stats
        total_expenses = queryset.aggregate(total=Sum('amount'))['total'] or 0
        expense_count = queryset.count()

        # If admin, provide breakdown by user
        user_breakdown = None
        if user.is_staff or user.is_superuser:
            user_breakdown = (
                Expense.objects.values('user__email', 'user__first_name', 'user__last_name')
                .annotate(total=Sum('amount'), count=Count('id'))
                .order_by('-total')
            )

        # Category breakdown
        category_breakdown = (
            queryset.values('category')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('-total')
        )

        return Response({
            'total_expenses': total_expenses,
            'expense_count': expense_count,
            'user_breakdown': user_breakdown,
            'category_breakdown': category_breakdown,
        })