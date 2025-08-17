from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Avg, Count, Max, Min

from .models import Question, QuestionCategory, Exam, Score
from .serializers import (
    QuestionSerializer,
    QuestionCategorySerializer,
    ExamSerializer,
    ScoreSerializer
)

import csv
from io import StringIO
from django.http import HttpResponse

@api_view(['GET'])
def download_questions_template(request):
    # Create in-memory CSV file
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    
    # Write headers
    writer.writerow([
        'exam_name',
        'category_name',
        'question_text',
        'option_1',
        'option_2',
        'option_3',
        'correct_option',
        'explanation'
    ])
    
    # Add sample data
    writer.writerow([
        'Architect',
        'test',
        'What service provides serverless compute?',
        'EC2',
        'Lambda',
        'EBS',
        'Lambda',
        'Lambda runs code without provisioning servers'
    ])
    
    response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="questions_template.csv"'
    return response


@api_view(['GET'])
def download_questions_csv(request):
    """
    Download all questions as CSV with specific fields
    GET /download-questions-csv/
    """
    # Create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="questions_export.csv"'},
    )

    # Create a CSV writer
    writer = csv.writer(response)
    
    # Write headers
    writer.writerow([
        'exam_name',
        'category_name',
        'question_text',
        'option_1',
        'option_2',
        'option_3',
        'correct_option',
        'explanation'
    ])
    
    # Get all questions with related exam and category
    questions = Question.objects.select_related('exam', 'category').all()
    
    # Write data rows
    for question in questions:
        writer.writerow([
            question.exam.name if question.exam else '',
            question.category.name if question.category else '',
            question.question_text,
            question.option_1,
            question.option_2,
            question.option_3,
            question.correct_option,
            question.explanation
        ])
    
    return response

@api_view(['POST'])
def upload_questions_csv(request):
    """
    Process CSV file directly without saving to media storage
    Expected CSV format:
    exam_name,category_name,question_text,option_1,option_2,option_3,correct_option,explanation
    """
    if not request.FILES.get('file'):
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    required_fields = [
        'exam_name', 'category_name', 'question_text',
        'option_1', 'option_2', 'option_3', 'correct_option'
    ]
    
    try:
        # Process file directly from memory
        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        # Validate headers
        missing_headers = [field for field in required_fields if field not in reader.fieldnames]
        if missing_headers:
            return Response(
                {'error': f'Missing required columns: {", ".join(missing_headers)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 for 1-based + header row
            try:
                # Validate required fields
                if not all(row.get(field) for field in required_fields):
                    raise ValueError("Missing required field values")
                
                exam, _ = Exam.objects.get_or_create(name=row['exam_name'])
                category, _ = QuestionCategory.objects.get_or_create(name=row['category_name'])
                
                Question.objects.create(
                    exam=exam,
                    category=category,
                    question_text=row['question_text'],
                    option_1=row['option_1'],
                    option_2=row['option_2'],
                    option_3=row['option_3'],
                    correct_option=row['correct_option'],
                    explanation=row.get('explanation', ''),
                    user=request.user
                )
                created_count += 1
                
            except Exception as e:
                errors.append({
                    'row': row_num,
                    'error': str(e),
                    'data': {k: v for k, v in row.items() if k in required_fields}
                })
        
        return Response({
            'status': 'success',
            'created': created_count,
            'failed': len(errors),
            'errors': errors,
            'total_rows_processed': row_num - 1  # Subtract header row
        }, status=status.HTTP_201_CREATED)
    
    except UnicodeDecodeError:
        return Response(
            {'error': 'File must be UTF-8 encoded'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except csv.Error as e:
        return Response(
            {'error': f'Invalid CSV format: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Unexpected error: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
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

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Max, Min
from django.db import models
from .models import Score
from .serializers import ScoreSerializer

class ScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allows authenticated users to view their quiz scores with filtering options
    Includes endpoints for:
    - Basic score listing with filters
    - Overall statistics
    - Breakdown by exam
    - Breakdown by category
    - Recent attempts
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
        Response:
        {
            "average_score": 75.5,
            "highest_score": 100.0,
            "lowest_score": 50.0,
            "total_attempts": 10,
            "last_attempt": "2023-06-15T14:30:00Z"
        }
        """
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({
                'message': 'No scores available for this user'
            }, status=status.HTTP_404_NOT_FOUND)
            
        stats = queryset.aggregate(
            average_score=Avg('score'),
            highest_score=Max('score'),
            lowest_score=Min('score'),
            total_attempts=Count('id'),
            last_attempt=Max('date')
        )
        
        return Response({
            'average_score': round(stats['average_score'], 2) if stats['average_score'] else 0,
            'highest_score': round(stats['highest_score'], 2) if stats['highest_score'] else 0,
            'lowest_score': round(stats['lowest_score'], 2) if stats['lowest_score'] else 0,
            'total_attempts': stats['total_attempts'],
            'last_attempt': stats['last_attempt']
        })

    @action(detail=False, methods=['get'])
    def by_exam(self, request):
        """
        Get score breakdown by exam
        GET /scores/by_exam/
        Response:
        [
            {
                "exam_id": 1,
                "exam_name": "Architecture",
                "average_score": 75.5,
                "highest_score": 100.0,
                "lowest_score": 50.0,
                "attempt_count": 5
            }
        ]
        """
        queryset = self.get_queryset().exclude(exam__isnull=True)
        
        breakdown = queryset.values(
            'exam__id', 
            'exam__name'
        ).annotate(
            average_score=Avg('score'),
            highest_score=Max('score'),
            lowest_score=Min('score'),
            attempt_count=Count('id')
        ).order_by('-average_score')
        
        # Transform to better format
        data = [{
            'exam_id': item['exam__id'],
            'exam_name': item['exam__name'],
            'average_score': round(item['average_score'], 2),
            'highest_score': round(item['highest_score'], 2),
            'lowest_score': round(item['lowest_score'], 2),
            'attempt_count': item['attempt_count']
        } for item in breakdown]
        
        return Response(data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get score breakdown by category
        GET /scores/by_category/
        Response:
        [
            {
                "category_id": 1,
                "category_name": "Design Patterns",
                "average_score": 80.0,
                "highest_score": 100.0,
                "lowest_score": 60.0,
                "attempt_count": 3
            }
        ]
        """
        queryset = self.get_queryset().exclude(category__isnull=True)
        
        breakdown = queryset.values(
            'category__id', 
            'category__name'
        ).annotate(
            average_score=Avg('score'),
            highest_score=Max('score'),
            lowest_score=Min('score'),
            attempt_count=Count('id')
        ).order_by('-average_score')
        
        # Transform to better format
        data = [{
            'category_id': item['category__id'],
            'category_name': item['category__name'],
            'average_score': round(item['average_score'], 2),
            'highest_score': round(item['highest_score'], 2),
            'lowest_score': round(item['lowest_score'], 2),
            'attempt_count': item['attempt_count']
        } for item in breakdown]
        
        return Response(data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent scores
        GET /scores/recent/?limit=5
        Response:
        [
            {
                "id": 1,
                "score": 85.0,
                "date": "2023-06-15T14:30:00Z",
                "exam": {"id": 1, "name": "Architecture"},
                "category": {"id": 1, "name": "Design Patterns"}
            }
        ]
        """
        limit = min(int(request.query_params.get('limit', 10)), 50)  # Max 50 results
        queryset = self.get_queryset()[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)