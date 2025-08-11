from django.contrib import admin
from .models import Question, Exam, QuestionCategory, Score


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question_text', 'exam', 'category']
    search_fields = ['question_text', 'correct_option']
    list_filter = ['exam', 'category']
    ordering = ['exam', 'category']


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'exam', 'category', 'score', 'date']
    search_fields = ['user__username', 'exam__name', 'category__name']
    list_filter = ['exam', 'category', 'date']
    ordering = ['-date']
