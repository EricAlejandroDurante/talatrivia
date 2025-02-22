from rest_framework import serializers

from .models import AnswerSubmission, Question, Answer, Trivia, TriviaAttempt

from ..core.serializers import UserSerializer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('request').user

        if not user.is_superuser:
            representation.pop('is_correct', None)

        return representation


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'difficulty', 'answers']
    
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        return question
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('request').user

        if not user.is_superuser:
            for answer in representation.get('answers', []):
                answer.pop('is_correct', None)

        return representation


class TriviaSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    users = UserSerializer(many=True, read_only=True)
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    question_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

    class Meta:
        model = Trivia
        fields = ['id', 'title', 'description', 'questions', 'users', 'user_ids', 'question_ids']

    def create(self, validated_data):
        user_ids = validated_data.pop('user_ids', [])
        question_ids = validated_data.pop('question_ids', [])

        trivia = Trivia.objects.create(**validated_data)

        trivia.users.set(user_ids)

        questions = Question.objects.filter(id__in=question_ids)
        trivia.questions.set(questions)

        return trivia

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('request').user

        if not user.is_superuser:
            representation.pop('users', None)

        return representation


class RankingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username')
    total_score = serializers.IntegerField()

    class Meta:
        model = TriviaAttempt
        fields = ['user_name', 'total_score']


class TriviaStartSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = TriviaAttempt
        fields = ['id', 'trivia', 'start_time', 'questions']

    def get_questions(self, obj):
        questions = obj.trivia.questions.all()
        return [{
            'id': q.id,
            'text': q.text,
            'answers': [{'id': a.id, 'text': a.text} for a in q.answers.all()]
        } for q in questions]


class TriviaAnswerSerializer(serializers.Serializer):
    attempt_id = serializers.UUIDField()
    answers = serializers.ListField(
        child=serializers.DictField(child=serializers.UUIDField())
    )

    def validate(self, data):
        attempt_id = data.get('attempt_id')
        try:
            attempt = TriviaAttempt.objects.get(id=attempt_id, completed=False)
            if attempt.is_time_expired():
                raise serializers.ValidationError("El tiempo para responder la trivia ha expirado.")
        except TriviaAttempt.DoesNotExist:
            raise serializers.ValidationError("Intento de trivia no válido o ya completado.")

        return data
      
        
class AnswerSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerSubmission
        fields = ['id', 'attempt', 'question', 'answer', 'is_correct']