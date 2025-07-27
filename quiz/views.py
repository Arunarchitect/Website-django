from rest_framework import viewsets
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
    Returns non-repeating random questions per session.
    Will return all remaining unseen questions first, then reset and fill the rest.
    Repeats only after at least 10 questions served.
    """
    try:
        count = int(request.GET.get('count', 5))
        if count < 1:
            count = 1
    except ValueError:
        count = 5

    total_questions = Question.objects.count()
    seen_ids = request.session.get('seen_question_ids', [])

    # Reset if all seen (but do this only after extracting all remaining unseen below)
    max_unique_limit = min(10, total_questions)

    # 1. Get unseen questions
    unseen_questions = Question.objects.exclude(id__in=seen_ids)
    unseen_count = unseen_questions.count()

    if unseen_count >= count:
        # Enough unseen questions
        questions = unseen_questions.order_by('?')[:count]
        seen_ids += [q.id for q in questions]
    else:
        # 2. Take all unseen first
        questions = list(unseen_questions.order_by('?'))

        # 3. Reset seen_ids, but avoid repeating just-served ones
        seen_ids = [q.id for q in questions]

        remaining_count = count - len(questions)
        refill_pool = Question.objects.exclude(id__in=seen_ids).order_by('?')[:remaining_count]

        questions += list(refill_pool)
        seen_ids += [q.id for q in refill_pool]

    # Limit tracking to max unique count
    if len(seen_ids) > max_unique_limit:
        seen_ids = seen_ids[-max_unique_limit:]

    request.session['seen_question_ids'] = seen_ids

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
