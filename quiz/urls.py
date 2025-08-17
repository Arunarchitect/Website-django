from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuestionViewSet,
    QuestionCategoryViewSet,
    ExamViewSet,
    get_questions,
    evaluate_quiz,
    get_exam_categories,
    ScoreViewSet,
    download_questions_template, 
    upload_questions_csv,
    download_questions_csv
)

router = DefaultRouter()
router.register(r'questions', QuestionViewSet)
router.register(r'categories', QuestionCategoryViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'scores', ScoreViewSet, basename='score')

urlpatterns = [
    path('', include(router.urls)),
    
    # Quiz endpoints
    path('get-quiz/', get_questions, name='get_quiz'),
    path('evaluate/', evaluate_quiz, name='evaluate_quiz'),
    
    # Category endpoints
    path('exam-categories/<int:exam_id>/', get_exam_categories, name='exam-categories'),
    
    # CSV import/export
    path('download-template/', download_questions_template, name='download-template'),
     path('download-csv/', download_questions_csv, name='download-csv'),
    path('upload-csv/', upload_questions_csv, name='upload-csv'),
]

# API Endpoint Documentation:
#
# Questions:
#   GET /questions/              - List all questions
#   POST /questions/             - Create new question
#   GET /questions/{id}/         - Get specific question
#   PUT /questions/{id}/         - Update question
#   DELETE /questions/{id}/      - Delete question
#
# Categories:
#   GET /categories/             - List all categories
#   POST /categories/            - Create new category
#   GET /categories/{id}/        - Get specific category
#   PUT /categories/{id}/        - Update category
#   DELETE /categories/{id}/     - Delete category
#
# Exams:
#   GET /exams/                  - List all exams
#   POST /exams/                 - Create new exam
#   GET /exams/{id}/             - Get specific exam
#   PUT /exams/{id}/             - Update exam
#   DELETE /exams/{id}/          - Delete exam
#
# Quiz Management:
#   POST /get-quiz/              - Get random quiz questions
#   POST /evaluate/              - Submit and evaluate quiz answers
#
# Exam Categories:
#   GET /exam-categories/{exam_id}/ - Get categories for specific exam
#
# CSV Operations:
#   GET /download-template/      - Download questions CSV template
#   POST /upload-csv/            - Upload questions CSV file
#
# Scores:
#   GET /scores/                 - List all scores (latest first)
#   GET /scores/{id}/            - Get specific score details
#   GET /scores/stats/           - Get user's score statistics
#   GET /scores/by_exam/         - Get scores breakdown by exam
#   GET /scores/by_category/     - Get scores breakdown by category
#   GET /scores/recent/          - Get recent scores (default: last 10)
#
# Score Filters:
#   /scores/?exam=1              - Filter by exam ID
#   /scores/?category=2          - Filter by category ID
#   /scores/?start=2023-01-01&end=2023-12-31 - Filter by date range