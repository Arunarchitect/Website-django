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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 👈 Correctly added

    def __str__(self):
        return self.question_text[:80]



class Score(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE)
    
    score = models.DecimalField(max_digits=5, decimal_places=2)  # e.g. 99.99%
    date = models.DateTimeField(default=timezone.now)  # Automatically records when entry is created

    class Meta:
        verbose_name = "Score"
        verbose_name_plural = "Scores"
        ordering = ["-date"]  # Most recent scores first

    def __str__(self):
        return f"{self.user} - {self.exam} - {self.category} : {self.score}%"
