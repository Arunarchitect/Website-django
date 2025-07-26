from django.core.management.base import BaseCommand
from quiz.models import Question, Exam, QuestionCategory

class Command(BaseCommand):
    help = 'Load sample architecture questions'

    def handle(self, *args, **kwargs):
        sample_questions = [
    # Building Regulations
    {
        "category": "Building Regulations",
        "question_text": "What is the minimum front setback for a residential plot in most urban municipalities?",
        "option_1": "1 meter",
        "option_2": "3 meters",
        "option_3": "4.5 meters",
        "correct_option": "4.5 meters",
        "explanation": "Urban regulations often mandate a 4.5m front setback to allow for ventilation and road widening."
    },
    {
        "category": "Building Regulations",
        "question_text": "What is the permissible FSI (Floor Space Index) in most Indian residential zones?",
        "option_1": "1.0",
        "option_2": "2.0",
        "option_3": "3.5",
        "correct_option": "2.0",
        "explanation": "FSI of 2.0 is typical in many Indian cities but may vary with local laws."
    },
    {
        "category": "Building Regulations",
        "question_text": "Which authority approves building plans in most Indian cities?",
        "option_1": "Municipal Corporation",
        "option_2": "RERA",
        "option_3": "Town Planning Committee",
        "correct_option": "Municipal Corporation",
        "explanation": "The Municipal Corporation or local authority grants construction approvals."
    },
    {
        "category": "Building Regulations",
        "question_text": "What is the minimum width of staircase in residential buildings as per NBC?",
        "option_1": "0.75 m",
        "option_2": "0.90 m",
        "option_3": "1.20 m",
        "correct_option": "0.90 m",
        "explanation": "NBC recommends a minimum 0.9m staircase width for residential buildings."
    },

    # Architectural History
    {
        "category": "Architectural History",
        "question_text": "Which architect is associated with the design of Chandigarh?",
        "option_1": "Frank Lloyd Wright",
        "option_2": "Le Corbusier",
        "option_3": "Zaha Hadid",
        "correct_option": "Le Corbusier",
        "explanation": "Le Corbusier planned the city of Chandigarh post-independence."
    },
    {
        "category": "Architectural History",
        "question_text": "What is the main architectural style of the Taj Mahal?",
        "option_1": "Gothic",
        "option_2": "Mughal",
        "option_3": "Dravidian",
        "correct_option": "Mughal",
        "explanation": "Taj Mahal is a classic example of Mughal architecture."
    },
    {
        "category": "Architectural History",
        "question_text": "Who was the pioneer of organic architecture?",
        "option_1": "Louis Kahn",
        "option_2": "Frank Lloyd Wright",
        "option_3": "Charles Correa",
        "correct_option": "Frank Lloyd Wright",
        "explanation": "Wright promoted harmony between human habitation and the natural world."
    },
    {
        "category": "Architectural History",
        "question_text": "Which of these structures is an example of Dravidian architecture?",
        "option_1": "Qutub Minar",
        "option_2": "Brihadeshwara Temple",
        "option_3": "Sanchi Stupa",
        "correct_option": "Brihadeshwara Temple",
        "explanation": "Dravidian style is prominent in South Indian temple architecture like Brihadeshwara."
    },

    # Sustainable Design
    {
        "category": "Sustainable Design",
        "question_text": "What is the main purpose of using fly ash in construction?",
        "option_1": "Reduce cost",
        "option_2": "Improve aesthetics",
        "option_3": "Enhance sustainability",
        "correct_option": "Enhance sustainability",
        "explanation": "Fly ash reduces cement consumption and enhances eco-friendliness."
    },
    {
        "category": "Sustainable Design",
        "question_text": "Which material has the highest thermal insulation?",
        "option_1": "Glass",
        "option_2": "Concrete",
        "option_3": "Cork",
        "correct_option": "Cork",
        "explanation": "Cork is a natural insulator with low thermal conductivity."
    },
    {
        "category": "Sustainable Design",
        "question_text": "What does LEED stand for?",
        "option_1": "Leadership in Environmental Energy Development",
        "option_2": "Leadership in Energy and Environmental Design",
        "option_3": "Legal Environmental Evaluation Directive",
        "correct_option": "Leadership in Energy and Environmental Design",
        "explanation": "LEED is a globally recognized green building certification system."
    },
    {
        "category": "Sustainable Design",
        "question_text": "Which roofing system best reduces heat gain?",
        "option_1": "Metal roof",
        "option_2": "White reflective roof",
        "option_3": "Clay tiles",
        "correct_option": "White reflective roof",
        "explanation": "Cool roofs reflect sunlight, reducing indoor heat gain."
    },

    # Construction Technology
    {
        "category": "Construction Technology",
        "question_text": "Which construction technique is used in earthquake-resistant design?",
        "option_1": "Reinforced brickwork",
        "option_2": "Base isolation",
        "option_3": "Flat slab",
        "correct_option": "Base isolation",
        "explanation": "Base isolators decouple the building from ground vibrations."
    },
    {
        "category": "Construction Technology",
        "question_text": "What is the typical size of a standard brick in India?",
        "option_1": "200 × 100 × 100 mm",
        "option_2": "190 × 90 × 90 mm",
        "option_3": "180 × 80 × 80 mm",
        "correct_option": "190 × 90 × 90 mm",
        "explanation": "This is the modular brick size as per IS code."
    },
    {
        "category": "Construction Technology",
        "question_text": "Which is not a non-destructive test for concrete?",
        "option_1": "Rebound Hammer",
        "option_2": "Ultrasonic Pulse Velocity",
        "option_3": "Slump test",
        "correct_option": "Slump test",
        "explanation": "Slump test is destructive and done on fresh concrete."
    },
    {
        "category": "Construction Technology",
        "question_text": "Which cement type is used for marine structures?",
        "option_1": "Rapid Hardening Cement",
        "option_2": "Portland Pozzolana Cement",
        "option_3": "Sulphate Resisting Cement",
        "correct_option": "Sulphate Resisting Cement",
        "explanation": "It prevents corrosion from sulphates in seawater."
    },

    # Design Principles
    {
        "category": "Design Principles",
        "question_text": "Which principle refers to the balance between void and solid?",
        "option_1": "Symmetry",
        "option_2": "Rhythm",
        "option_3": "Proportion",
        "correct_option": "Proportion",
        "explanation": "Proportion governs the spatial relationship of forms."
    },
    {
        "category": "Design Principles",
        "question_text": "What is the golden ratio approximately equal to?",
        "option_1": "1.414",
        "option_2": "1.618",
        "option_3": "3.14",
        "correct_option": "1.618",
        "explanation": "Golden ratio is ~1.618, often used for pleasing aesthetics."
    },
    {
        "category": "Design Principles",
        "question_text": "Which of these is NOT a principle of design?",
        "option_1": "Balance",
        "option_2": "Harmony",
        "option_3": "Digestion",
        "correct_option": "Digestion",
        "explanation": "Digestion is unrelated to architectural design."
    },
    {
        "category": "Design Principles",
        "question_text": "Which design principle ensures visual continuity?",
        "option_1": "Emphasis",
        "option_2": "Rhythm",
        "option_3": "Contrast",
        "correct_option": "Rhythm",
        "explanation": "Rhythm creates visual movement and flow in design."
    }
]

        exam, _ = Exam.objects.get_or_create(name="Architecture Basics")

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
            )

        self.stdout.write(self.style.SUCCESS("Sample questions loaded successfully."))