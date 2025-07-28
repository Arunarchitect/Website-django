import json
from django.core.management.base import BaseCommand
from quiz.models import Question, Exam, QuestionCategory
from django.contrib.auth import get_user_model
from pathlib import Path

User = get_user_model()

class Command(BaseCommand):
    help = 'Load sample architecture questions from JSON file'

    def handle(self, *args, **kwargs):
        user = User.objects.get(id=2)  # Replace with actual user ID if different

        # Get path to JSON file in the same directory as this Python file
        current_dir = Path(__file__).resolve().parent
        json_file = current_dir / "guide25to100mock1.json"

        if not json_file.exists():
            self.stderr.write(self.style.ERROR(f"{json_file} not found"))
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)

        exam, _ = Exam.objects.get_or_create(name="Architect")

        for q in questions_data:
            category, _ = QuestionCategory.objects.get_or_create(name=q['category'])
            Question.objects.create(
                exam=exam,
                category=category,
                question_text=q['question_text'],
                option_1=q['option_1'],
                option_2=q['option_2'],
                option_3=q['option_3'],
                correct_option=q['correct_option'],
                explanation=q['explanation'],
                user=user
            )

        self.stdout.write(self.style.SUCCESS("Sample questions loaded successfully from JSON."))
