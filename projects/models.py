from django.db import models
from django.contrib.auth import get_user_model  # Import get_user_model()

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

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return f"{self.name} ({self.client_name})"


class WorkType(models.Model):
    name = models.CharField("Work Type", max_length=100)

    class Meta:
        verbose_name = "Work Type"
        verbose_name_plural = "Work Types"

    def __str__(self):
        return self.name


class WorkLog(models.Model):
    employee = models.ForeignKey(get_user_model(), verbose_name="Employee", on_delete=models.CASCADE)  # Use get_user_model()
    project = models.ForeignKey(Project, verbose_name="Project", on_delete=models.CASCADE)
    work_type = models.ForeignKey(WorkType, verbose_name="Work Type", on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField("Start Time")
    end_time = models.DateTimeField("End Time", null=True, blank=True)

    class Meta:
        verbose_name = "Work Log"
        verbose_name_plural = "Work Logs"

    def __str__(self):
        return f"{self.employee.email} - {self.project.name} ({self.start_time.strftime('%Y-%m-%d')})"

    @property
    def duration(self):
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None


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
    work_type = models.ForeignKey(WorkType, verbose_name="Deliverable Name", on_delete=models.CASCADE)
    stage = models.CharField("Stage", max_length=1, choices=STAGE_CHOICES)
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default='not_started')
    remarks = models.TextField("Remarks", blank=True, null=True)

    class Meta:
        verbose_name = "Deliverable"
        verbose_name_plural = "Deliverables"
        unique_together = ('project', 'work_type', 'stage')  # updated to use work_type

    def __str__(self):
        return f"{self.project.name} - {self.work_type.name} (Stage {self.stage}) - {self.get_status_display()}"

    @property
    def name(self):
        return f"{self.work_type.name} - Stage {self.stage}"
