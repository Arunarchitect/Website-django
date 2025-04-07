from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField("Project Name", max_length=255)
    location = models.CharField("Location", max_length=255)
    client_name = models.CharField("Client Name", max_length=255)

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
    employee = models.ForeignKey(User, verbose_name="Employee", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name="Project", on_delete=models.CASCADE)
    work_type = models.ForeignKey(WorkType, verbose_name="Work Type", on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField("Start Time")
    end_time = models.DateTimeField("End Time", null=True, blank=True)

    class Meta:
        verbose_name = "Work Log"
        verbose_name_plural = "Work Logs"

    def __str__(self):
        return f"{self.employee.username} - {self.project.name} ({self.start_time.strftime('%Y-%m-%d')})"

    @property
    def duration(self):
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None
