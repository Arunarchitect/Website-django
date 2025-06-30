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
        ('client', 'Client'),
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



from django.core.exceptions import ValidationError


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
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_deliverables")
    validator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="validated_deliverables")
    validation_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Deliverable"
        verbose_name_plural = "Deliverables"
        unique_together = ('project', 'name', 'stage')
        ordering = ['project', 'stage', 'name']

    def __str__(self):
        return f"{self.project.name} - {self.name} (Stage {self.stage}) - {self.get_status_display()}"

    @property
    def stage_name(self):
        return dict(self.STAGE_CHOICES).get(self.stage)

    def clean(self):
        """Add model-level validation"""
        super().clean()
        
        # Check if status requires work logs
        if self.status in ['ready', 'passed', 'failed', 'discrepancy']:
            if not self.pk or not self.worklogs.exists():
                raise ValidationError(
                    "Please add work logs before setting status to '%(status)s'.",
                    params={'status': self.get_status_display()},
                    code='invalid_status'
                )

    def save(self, *args, **kwargs):
        """Custom save method with validation"""
        # Run full validation before saving
        self.full_clean()
        
        # Set end_date if validation_date is set but end_date isn't
        if self.validation_date and not self.end_date:
            self.end_date = self.validation_date.date()
        
        super().save(*args, **kwargs)

    def update_status_based_on_worklogs(self):
        """Updates status to 'ongoing' if worklogs exist, else 'not_started'"""
        has_worklogs = self.worklogs.exists()
        
        if has_worklogs:
            if self.status == 'not_started':
                self.status = 'ongoing'
            # Update start_date if not set
            if not self.start_date:
                first_worklog = self.worklogs.earliest('start_time')
                self.start_date = first_worklog.start_time.date()
        elif self.status == 'ongoing':
            self.status = 'not_started'
        
        if has_worklogs or self.status != 'not_started':
            update_fields = ['status']
            if not self.start_date and has_worklogs:
                update_fields.append('start_date')
            self.save(update_fields=update_fields)
            
            
from django.utils import timezone
from django.db import models

class WorkLog(models.Model):
    # Existing fields
    employee = models.ForeignKey(User, verbose_name="Employee", on_delete=models.CASCADE)
    deliverable = models.ForeignKey(Deliverable, verbose_name="Deliverable", on_delete=models.CASCADE, related_name='worklogs')
    start_time = models.DateTimeField("Start Time")
    end_time = models.DateTimeField("End Time", null=True, blank=True)
    remarks = models.TextField("Remarks", blank=True, null=True)
    
    # New fields with temporary defaults (will be overridden)
    entered_time = models.DateTimeField("Record Time", default=timezone.now)
    edited_time = models.DateTimeField("Last Edited Time", default=timezone.now)

    class Meta:
        verbose_name = "Work Log"
        verbose_name_plural = "Work Logs"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize time fields for existing records when model is loaded
        self._initialize_time_fields()

    def _initialize_time_fields(self):
        """Set fallback values only if missing."""
        if self.pk:
            if self.entered_time is None:
                self.entered_time = self.start_time
            if self.edited_time is None:
                self.edited_time = self.end_time or self.start_time


    def save(self, *args, **kwargs):
        
        # Ensure time fields are properly set before saving
        self._initialize_time_fields()
        
        # Track if this is a new record
        is_new = self._state.adding
        
        # For new records, let Django handle auto_now_add/auto_now behavior
        if is_new:
            self.entered_time = timezone.now()
            self.edited_time = timezone.now()
        else:
            # For existing records, update edited_time on each save
            self.edited_time = timezone.now()

        super().save(*args, **kwargs)
        
        # Original deliverable status update logic
        if is_new:
            if not self.deliverable.start_date:
                self.deliverable.start_date = self.start_time.date()
                update_fields = ['start_date']
                if self.deliverable.status == 'not_started':
                    self.deliverable.status = 'ongoing'
                    update_fields.append('status')
                self.deliverable.save(update_fields=update_fields)
            else:
                self.deliverable.update_status_based_on_worklogs()

    # Rest of your existing methods remain unchanged
    def delete(self, *args, **kwargs):
        deliverable = self.deliverable
        super().delete(*args, **kwargs)
        deliverable.update_status_based_on_worklogs()

    @property
    def duration(self):
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds()
        return None

    @property
    def project(self):
        return self.deliverable.project if self.deliverable else None

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('travel', 'Travel'),
        ('food', 'Food'),
        ('accommodation', 'Accommodation'),
        ('stationery', 'Stationery'),
        ('others', 'Others'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    remarks = models.TextField(blank=True, null=True)
    date = models.DateField()  # Changed to regular DateField (not auto_now_add)
    created_at = models.DateTimeField(auto_now_add=True)  # For record keeping

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.get_category_display()} - {self.amount} ({self.date})"

    def clean(self):
        """Add validation for amount"""
        if self.amount <= 0:
            raise ValidationError("Amount must be greater than zero.")