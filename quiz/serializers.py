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
    class Meta:
        model = Score
        fields = ['id', 'user', 'exam', 'category', 'score', 'date']
        read_only_fields = ['id', 'date', 'user']

    def validate_score(self, value):
        """Ensure score is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Score must be between 0 and 100.")
        return value
