import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete
from django.dispatch import receiver

from project.models import Project, Organisation
from .validators import validate_360_image

User = get_user_model()


class Viewer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='viewer_entries'
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name='viewer_entries'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='viewer_entries'
    )

    view_name = models.CharField(max_length=255)
    view_date = models.DateField()

    image_360 = models.ImageField(
        upload_to='viewer/360_images/',
        validators=[validate_360_image],
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-view_date']

    def __str__(self):
        return f"{self.project.name} - {self.view_name} ({self.view_date})"

    def save(self, *args, **kwargs):
        """Delete old file when updating with a new one."""
        if self.pk:
            try:
                old_file = Viewer.objects.get(pk=self.pk).image_360
            except Viewer.DoesNotExist:
                old_file = None

            new_file = self.image_360
            if old_file and old_file != new_file:
                old_file.delete(save=False)

        super().save(*args, **kwargs)


# --- CLEANUP HANDLER ON DELETE (covers both instance.delete() & queryset.delete()) ---
@receiver(post_delete, sender=Viewer)
def delete_file_on_instance_delete(sender, instance, **kwargs):
    if instance.image_360:
        instance.image_360.delete(save=False)


class ProjectAccessKey(models.Model):
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE
    )

    access_key = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="Custom or auto-generated key to share viewer access."
    )

    def save(self, *args, **kwargs):
        if not self.access_key:
            # Generate a 10-character unique access key
            self.access_key = uuid.uuid4().hex[:10]
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ()
        # for org and project only have 1 access ke use this --- unique_together = ('organisation', 'project')

    def __str__(self):
        return f"{self.organisation.name} - {self.project.name} ({self.access_key})"
