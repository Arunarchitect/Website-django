from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuestionViewSet,
    QuestionCategoryViewSet,
    ExamViewSet,
    get_questions,
    evaluate_quiz,
)

router = DefaultRouter()
router.register(r'questions', QuestionViewSet)
router.register(r'categories', QuestionCategoryViewSet)
router.register(r'exams', ExamViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get-quiz/', get_questions, name='get_quiz'),
    path('evaluate/', evaluate_quiz, name='evaluate_quiz'),
]
