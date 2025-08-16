from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuestionViewSet,
    QuestionCategoryViewSet,
    ExamViewSet,
    get_questions,
    evaluate_quiz,
    get_exam_categories,
    ScoreViewSet
)

router = DefaultRouter()
router.register(r'questions', QuestionViewSet)
router.register(r'categories', QuestionCategoryViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'scores', ScoreViewSet, basename='score')

urlpatterns = [
    path('', include(router.urls)),
    path('get-quiz/', get_questions, name='get_quiz'),
    path('evaluate/', evaluate_quiz, name='evaluate_quiz'),
    path('exam-categories/<int:exam_id>/', get_exam_categories, name='exam-categories'),
]


# GET/POST /questions/ → all questions

# GET /questions/{id}/ → single question

# GET /categories/ → all categories

# GET /exams/ → all exams

# GET /get-quiz/ → get random quiz questions (with count, exam, category filters)

# POST /evaluate/ → send answers, get score


# Endpoint	Method	Description
# /scores/	GET	All scores of logged-in user (latest first)
# /scores/{id}/	GET	Details of one score
# /scores/by_category/?category=1	GET	Scores filtered by category
# /scores/by_exam/?exam=2	GET	Scores filtered by exam
# /scores/datewise/?start=2025-08-01&end=2025-08-10	GET	Scores between two dates