from django.core.management.base import BaseCommand
from quiz.models import Question

class Command(BaseCommand):
    help = 'Delete questions with ID from 11 to 30'

    def handle(self, *args, **kwargs):
        deleted_count, _ = Question.objects.filter(id__gte=11, id__lte=30).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} questions with IDs from 11 to 30."))
