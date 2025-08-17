from django.db import models
from django.conf import settings  # Recommended way to refer to custom user model
from django.utils import timezone

class QuestionCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Exam(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE)
    
    question_text = models.TextField()
    
    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    option_3 = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=255)

    explanation = models.TextField(blank=True, null=True)
    
    # Add these new fields with auto_now_add and auto_now
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 👈 Correctly added

    def __str__(self):
        return self.question_text[:80]



class Score(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey('QuestionCategory', on_delete=models.CASCADE, null=True, blank=True)
    
    score = models.DecimalField(max_digits=5, decimal_places=2)  # e.g. 99.99%
    date = models.DateTimeField(default=timezone.now)  # Automatically records when entry is created

    class Meta:
        verbose_name = "Score"
        verbose_name_plural = "Scores"
        ordering = ["-date"]  # Most recent scores first

    def __str__(self):
        exam_name = self.exam.name if self.exam else "All Exams"
        category_name = self.category.name if self.category else "All Categories"
        return f"{self.user} - {exam_name} - {category_name} : {self.score}%"