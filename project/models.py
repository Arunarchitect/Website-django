from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Organisation(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def get_admins(self):
        return self.memberships.filter(role='admin').select_related('user')

    def get_managers(self):
        return self.memberships.filter(role='manager').select_related('user')

    def get_members(self):
        return self.memberships.filter(role='member').select_related('user')


class OrganisationMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('member', 'Member'),
    ]

    organisation = models.ForeignKey(Organisation, related_name='memberships', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='organisation_memberships', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('organisation', 'user')

    def __str__(self):
        return f"{self.user.email} - {self.organisation.name} ({self.role})"


class Project(models.Model):
    STAGE_CHOICES = [
        ('1', 'Stage 1'),
        ('2', 'Stage 2'),
        ('3', 'Stage 3'),
        ('4', 'Stage 4'),
        ('5', 'Stage 5'),
    ]

    name = models.CharField("Project Name", max_length=255)
    location = models.CharField("Location", max_length=255)
    client_name = models.CharField("Client Name", max_length=255)
    current_stage = models.CharField("Current Stage", max_length=1, choices=STAGE_CHOICES, default='1')
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='projects')

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return f"{self.name} ({self.client_name})"


class Deliverable(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('ongoing', 'Ongoing'),
        ('ready', 'Ready for Validation'),
        ('passed', 'Passed Validation'),
        ('failed', 'Failed Validation'),
        ('discrepancy', 'Site Discrepancy'),
    ]

    STAGE_CHOICES = Project.STAGE_CHOICES

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='deliverables')
    name = models.CharField("Deliverable Name", max_length=255)
    stage = models.CharField("Stage", max_length=1, choices=STAGE_CHOICES)
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default='not_started')
    remarks = models.TextField("Remarks", blank=True, null=True)
    start_date = models.DateField("Start Date", null=True, blank=True)
    end_date = models.DateField("End Date", null=True, blank=True)

    class Meta:
        verbose_name = "Deliverable"
        verbose_name_plural = "Deliverables"
        unique_together = ('project', 'name', 'stage')

    def __str__(self):
        return f"{self.project.name} - {self.name} (Stage {self.stage}) - {self.get_status_display()}"

    @property
    def stage_name(self):
        return dict(self.STAGE_CHOICES).get(self.stage)


class WorkLog(models.Model):
    employee = models.ForeignKey(User, verbose_name="Employee", on_delete=models.CASCADE)
    deliverable = models.ForeignKey(Deliverable, verbose_name="Deliverable", on_delete=models.CASCADE)
    start_time = models.DateTimeField("Start Time")
    end_time = models.DateTimeField("End Time", null=True, blank=True)

    class Meta:
        verbose_name = "Work Log"
        verbose_name_plural = "Work Logs"

    def __str__(self):
        deliverable_name = self.deliverable.name if self.deliverable else "No Deliverable"
        return f"{self.employee.email} - {deliverable_name} ({self.start_time.strftime('%Y-%m-%d')})"

    @property
    def duration(self):
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds()
        return None

    @property
    def project(self):
        """Access the project via deliverable"""
        return self.deliverable.project if self.deliverable else None
