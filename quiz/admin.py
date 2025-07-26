from django.contrib import admin
from .models import Question, Exam, QuestionCategory

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

    # Remove this method to allow "+" add buttons
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     for field in ['exam', 'category']:
    #         if field in form.base_fields:
    #             form.base_fields[field].widget.can_add_related = False
    #     return form
