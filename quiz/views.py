from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Question, QuestionCategory, Exam
from .serializers import QuestionSerializer, QuestionCategorySerializer, ExamSerializer

# ----------- ViewSets for CRUD -----------

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class QuestionCategoryViewSet(viewsets.ModelViewSet):
    queryset = QuestionCategory.objects.all()
    serializer_class = QuestionCategorySerializer

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

# ----------- Custom Quiz API Views -----------

@api_view(['GET'])
def get_questions(request):
    """
    Returns random questions. Use ?count=5 to limit number.
    """
    try:
        count = int(request.GET.get('count', 5))
        if count < 1:
            count = 1
    except ValueError:
        count = 5

    questions = Question.objects.order_by('?')[:count]
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def evaluate_quiz(request):
    """
    Accepts user answers and returns score and explanations.
    Format: { "question_1": "Option A", "question_2": "Option B" }
    """
    data = request.data
    total = 0
    score = 0
    explanations = []

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
                score += 1

            explanations.append({
                'id': question.id,
                'question': question.question_text,
                'selected': selected_option,
                'correct': question.correct_option,
                'explanation': question.explanation or '',
                'is_correct': is_correct
            })

    return Response({
        'score': score,
        'total': total,
        'explanations': explanations
    })
