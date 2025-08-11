from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from .models import Question, QuestionCategory, Exam, Score
from .serializers import (
    QuestionSerializer,
    QuestionCategorySerializer,
    ExamSerializer,
    ScoreSerializer
)

# -------------------- CRUD ViewSets --------------------

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionCategoryViewSet(viewsets.ModelViewSet):
    queryset = QuestionCategory.objects.all()
    serializer_class = QuestionCategorySerializer


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer


# -------------------- Custom Quiz APIs --------------------

@api_view(['POST'])
def get_questions(request):
    """
    POST params:
    {
        "count": 5,
        "exam": 1,        # optional
        "category": 2     # optional
    }
    Returns non-repeating random questions for the session.
    """
    try:
        count = int(request.data.get('count', 5))
        count = max(1, count)  # Ensure at least 1
    except (ValueError, TypeError):
        count = 5

    exam_id = request.data.get('exam')
    category_id = request.data.get('category')

    queryset = Question.objects.all()
    if exam_id:
        queryset = queryset.filter(exam_id=exam_id)
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    total_questions = queryset.count()
    seen_ids = request.session.get('seen_question_ids', [])
    max_unique_limit = min(10, total_questions)

    unseen_questions = queryset.exclude(id__in=seen_ids)
    unseen_count = unseen_questions.count()

    if unseen_count >= count:
        questions = unseen_questions.order_by('?')[:count]
        seen_ids += [q.id for q in questions]
    else:
        questions = list(unseen_questions.order_by('?'))
        seen_ids = [q.id for q in questions]
        remaining_count = count - len(questions)
        refill_pool = queryset.exclude(id__in=seen_ids).order_by('?')[:remaining_count]
        questions += list(refill_pool)
        seen_ids += [q.id for q in refill_pool]

    if len(seen_ids) > max_unique_limit:
        seen_ids = seen_ids[-max_unique_limit:]

    request.session['seen_question_ids'] = seen_ids

    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def evaluate_quiz(request):
    """
    POST body example:
    {
        "question_1": "Option A",
        "question_2": "Option B"
    }
    Optional query params: ?exam=1&category=2
    Saves score if user is authenticated.
    """
    data = request.data
    total = 0
    correct_count = 0
    explanations = []

    exam_id = request.GET.get('exam')
    category_id = request.GET.get('category')

    for key, selected_option in data.items():
        if str(key).startswith("question_"):
            try:
                qid = int(key.split("_")[1])
                question = Question.objects.get(id=qid)
            except (Question.DoesNotExist, ValueError):
                continue

            total += 1
            is_correct = (selected_option == question.correct_option)
            if is_correct:
                correct_count += 1

            explanations.append({
                'id': question.id,
                'question': question.question_text,
                'selected': selected_option,
                'correct': question.correct_option,
                'explanation': question.explanation or '',
                'is_correct': is_correct
            })

            if not exam_id:
                exam_id = question.exam_id
            if not category_id:
                category_id = question.category_id

    percentage = (correct_count / total * 100) if total > 0 else 0
    percentage = round(percentage, 2)

    # Save score to DB via serializer
    if request.user.is_authenticated and exam_id and category_id:
        serializer = ScoreSerializer(data={
            'exam': exam_id,
            'category': category_id,
            'score': percentage
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

    return Response({
        'score': correct_count,
        'total': total,
        'percentage': percentage,
        'explanations': explanations
    })


# -------------------- Score ViewSet --------------------

class ScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allows a logged-in user to view their quiz scores.
    Supports list, retrieve, and custom filters.
    """
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only fetch current user's scores
        return Score.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Filter scores by category_id
        GET /scores/by_category/?category=1
        """
        category_id = request.GET.get('category')
        qs = self.get_queryset()
        if category_id:
            qs = qs.filter(category_id=category_id)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_exam(self, request):
        """
        Filter scores by exam_id
        GET /scores/by_exam/?exam=2
        """
        exam_id = request.GET.get('exam')
        qs = self.get_queryset()
        if exam_id:
            qs = qs.filter(exam_id=exam_id)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def datewise(self, request):
        """
        Get scores between two dates
        GET /scores/datewise/?start=2025-08-01&end=2025-08-10
        """
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        qs = self.get_queryset()
        if start_date and end_date:
            qs = qs.filter(created_at__date__range=[start_date, end_date])
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
