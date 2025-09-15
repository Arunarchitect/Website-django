# viewer/models.py

from django.db import models
from django.contrib.auth import get_user_model
from project.models import Project
from .validators import validate_360_image  # Optional: if you validate 360° image types

User = get_user_model()

class Viewer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewer_entries')
    organisation = models.ForeignKey('project.Organisation', on_delete=models.CASCADE, related_name='viewer_entries')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='viewer_entries')
    
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
