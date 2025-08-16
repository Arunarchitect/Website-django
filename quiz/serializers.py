# serializers.py
from rest_framework import serializers
from .models import Question, QuestionCategory, Exam, Score


class QuestionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = '__all__'


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class ScoreSerializer(serializers.ModelSerializer):
    exam = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Score
        fields = ['id', 'user', 'exam', 'category', 'score', 'date']
        read_only_fields = ['id', 'date', 'user']

    def get_exam(self, obj):
        return {
            'id': obj.exam.id if obj.exam else None,
            'name': obj.exam.name if obj.exam else "All Exams"
        }

    def get_category(self, obj):
        return {
            'id': obj.category.id if obj.category else None,
            'name': obj.category.name if obj.category else "All Categories"
        }

    def validate_score(self, value):
        """Ensure score is between -100 and 100"""
        if not (-100 <= value <= 100):
            raise serializers.ValidationError("Score must be between -100 and 100.")
        return value