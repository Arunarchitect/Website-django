from django.core.management.base import BaseCommand
from quiz.models import Question, Exam, QuestionCategory
from django.contrib.auth import get_user_model
User = get_user_model()

class Command(BaseCommand):
    help = 'Load sample architecture questions'

    def handle(self, *args, **kwargs):
        user = User.objects.get(id=2)  # ✅ Get user instance
        
        
        sample_questions = [
    # Building Regulations
    {
        "category": "Building Regulations",
        "question_text": "What is the minimum front setback for a residential plot in most urban municipalities?",
        "option_1": "0.5 meter",
        "option_2": "user meters",
        "option_3": "3 meters",
        "correct_option": "1 meter",
        "explanation": "Most municipalities require a minimum front setback of 1 meter for ventilation and safety.",
        "user": user
    },
    {
        "category": "Building Regulations",
        "question_text": "What is the maximum permissible ground coverage for a residential plot?",
        "option_1": "90%",
        "option_2": "25%",
        "option_3": "50%",
        "correct_option": "66.6%",
        "explanation": "Typically, 66.6% is the maximum allowed ground coverage to ensure open space and ventilation.",
        "user": user
    },

    # Design Principles
    {
        "category": "Design Principles",
        "question_text": "Which design principle ensures visual continuity?",
        "option_1": "Hierarchy",
        "option_2": "Contrast",
        "option_3": "Emphasis",
        "correct_option": "Rhythm",
        "explanation": "Rhythm in design creates a sense of flow and continuity, guiding the viewer’s eye.",
        "user": user
    },
    {
        "category": "Design Principles",
        "question_text": "Which principle is primarily concerned with the equal distribution of visual weight?",
        "option_1": "Movement",
        "option_2": "Proportion",
        "option_3": "Rhythm",
        "correct_option": "Balance",
        "explanation": "Balance creates a sense of stability in a composition by distributing visual elements evenly.",
        "user": user
    },

    # Materials
    {
        "category": "Materials",
        "question_text": "Which material is commonly used for thermal insulation in buildings?",
        "option_1": "Cement",
        "option_2": "Steel",
        "option_3": "Granite",
        "correct_option": "Glass wool",
        "explanation": "Glass wool has low thermal conductivity and is commonly used as insulation in walls and roofs.",
        "user": user
    },
    {
        "category": "Materials",
        "question_text": "What is the typical compressive strength of M20 concrete?",
        "option_1": "10 MPa",
        "option_2": "15 MPa",
        "option_3": "30 MPa",
        "correct_option": "20 MPa",
        "explanation": "M20 concrete has a characteristic compressive strength of 20 MPa after 28 days of curing.",
        "user": user
    },

    # Structures
    {
        "category": "Structures",
        "question_text": "Which structural element resists bending?",
        "option_1": "Column",
        "option_2": "Foundation",
        "option_3": "Slab",
        "correct_option": "Beam",
        "explanation": "Beams primarily resist bending moments and transfer loads horizontally to supports.",
        "user": user
    },
    {
        "category": "Structures",
        "question_text": "Which structure efficiently covers large column-free spaces?",
        "option_1": "Flat slab",
        "option_2": "Cantilever beam",
        "option_3": "Brick wall",
        "correct_option": "Space frame",
        "explanation": "Space frames use a 3D truss system to span large areas without internal supports.",
        "user": user
    },

    # History of Architecture
    {
        "category": "History of Architecture",
        "question_text": "Which architectural period is known for the use of flying buttresses?",
        "option_1": "Romanesque",
        "option_2": "Baroque",
        "option_3": "Neoclassical",
        "correct_option": "Gothic",
        "explanation": "Gothic architecture features flying buttresses to support tall structures and large stained glass windows.",
        "user": user
    },
    {
        "category": "History of Architecture",
        "question_text": "Who designed the Villa Savoye?",
        "option_1": "Frank Lloyd Wright",
        "option_2": "Ludwig Mies van der Rohe",
        "option_3": "Louis Kahn",
        "correct_option": "Le Corbusier",
        "explanation": "Villa Savoye, located in France, is a modernist masterpiece designed by Le Corbusier.",
        "user": user
    }
]

        exam, _ = Exam.objects.get_or_create(name="Architect")

        for item in sample_questions:
            category, _ = QuestionCategory.objects.get_or_create(name=item['category'])
            Question.objects.create(
                exam=exam,
                category=category,
                question_text=item['question_text'],
                option_1=item['option_1'],
                option_2=item['option_2'],
                option_3=item['option_3'],
                correct_option=item['correct_option'],
                explanation=item['explanation'],
                user=user  # ✅ Fix: Add the user here
            )

        self.stdout.write(self.style.SUCCESS("Sample questions loaded successfully."))