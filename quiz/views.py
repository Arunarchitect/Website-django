from django.utils import timezone
from rest_framework import viewsets, permissions, status
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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class QuestionCategoryViewSet(viewsets.ModelViewSet):
    queryset = QuestionCategory.objects.all()
    serializer_class = QuestionCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# -------------------- Custom Quiz APIs --------------------

@api_view(['POST'])
def get_questions(request):
    """
    Get random questions with session-based non-repeating logic
    POST params:
    {
        "count": 5,       # required (1-50)
        "exam": 1,        # optional
        "category": 2     # optional
    }
    """
    # Validate count parameter
    try:
        count = int(request.data.get('count', 5))
        count = max(1, min(count, 50))  # Limit to 1-50 questions
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid count parameter. Must be an integer between 1-50."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Build base queryset with optional filters
    queryset = Question.objects.all()
    
    exam_id = request.data.get('exam')
    if exam_id:
        queryset = queryset.filter(exam_id=exam_id)
    
    category_id = request.data.get('category')
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    # Get seen question IDs from session
    seen_ids = request.session.get('seen_question_ids', [])
    
    # First try to get unseen questions
    unseen_questions = queryset.exclude(id__in=seen_ids).order_by('?')
    questions = list(unseen_questions[:count])
    
    # If we didn't get enough, fill with random questions (may repeat)
    if len(questions) < count:
        remaining = count - len(questions)
        questions += list(queryset.order_by('?')[:remaining])
    
    # Update seen questions in session (keep last 100 max)
    new_seen_ids = [q.id for q in questions]
    request.session['seen_question_ids'] = (seen_ids + new_seen_ids)[-100:]
    request.session.modified = True

    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def evaluate_quiz(request):
    """
    Evaluate quiz answers with negative marking and save score
    POST data:
    {
        "answers": {"question_1": "option_1", ...},
        "calculated_score": 5.33,
        "calculated_percentage": 53.3,
        "exam": 1,        # optional
        "category": 2     # optional
    }
    """
    data = request.data
    
    # Validate required fields
    if not isinstance(data.get('answers'), dict):
        return Response(
            {"error": "Answers must be provided as a dictionary"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        calculated_score = float(data.get('calculated_score', 0))
        calculated_percentage = float(data.get('calculated_percentage', 0))
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid score values"},
            status=status.HTTP_400_BAD_REQUEST
        )

    explanations = []
    exam_id = data.get('exam')
    category_id = data.get('category')

    # Process each answer
    for key, selected_option in data.get('answers', {}).items():
        if not key.startswith("question_"):
            continue
            
        try:
            qid = int(key.split("_")[1])
            question = Question.objects.get(id=qid)
        except (Question.DoesNotExist, ValueError, IndexError):
            continue

        is_correct = selected_option == question.correct_option
        
        explanations.append({
            'id': question.id,
            'question': question.question_text,
            'selected': selected_option,
            'correct': question.correct_option,
            'explanation': question.explanation or '',
            'is_correct': is_correct
        })

        # Auto-detect exam/category from questions if not provided
        if not exam_id:
            exam_id = question.exam_id
        if not category_id:
            category_id = question.category_id

    # Save score to DB if user is authenticated
    if request.user.is_authenticated:
        score_data = {
            'exam': exam_id,
            'category': category_id,
            'score': calculated_percentage,
            'date': timezone.now()
        }
        serializer = ScoreSerializer(data=score_data)
        if serializer.is_valid():
            serializer.save(user=request.user)
        # Silently fail if score save fails to not disrupt quiz experience

    return Response({
        'score': calculated_score,
        'total': len(data.get('answers', {})),
        'percentage': calculated_percentage,
        'explanations': explanations
    })
    
# views.py
@api_view(['GET'])
def get_exam_categories(request, exam_id):
    """
    Get categories that have questions in the specified exam
    GET /exam-categories/{exam_id}/
    """
    try:
        # Get distinct categories that have questions in this exam
        categories = QuestionCategory.objects.filter(
            question__exam_id=exam_id
        ).distinct()
        
        serializer = QuestionCategorySerializer(categories, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


# -------------------- Score ViewSet --------------------

class ScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allows authenticated users to view their quiz scores with filtering options
    """
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Score.objects.filter(user=self.request.user)
        
        # Apply filters if provided
        exam_id = self.request.query_params.get('exam')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
            
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        start_date = self.request.query_params.get('start')
        end_date = self.request.query_params.get('end')
        if start_date and end_date:
            queryset = queryset.filter(
                date__date__gte=start_date,
                date__date__lte=end_date
            )
            
        return queryset.order_by('-date')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get basic statistics about user's scores
        GET /scores/stats/
        """
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                'message': 'No scores available for this user'
            })
            
        average_score = queryset.aggregate(models.Avg('score'))['score__avg']
        highest_score = queryset.aggregate(models.Max('score'))['score__max']
        lowest_score = queryset.aggregate(models.Min('score'))['score__min']
        total_attempts = queryset.count()
        
        return Response({
            'average_score': round(average_score, 2),
            'highest_score': round(highest_score, 2),
            'lowest_score': round(lowest_score, 2),
            'total_attempts': total_attempts
        })
        
