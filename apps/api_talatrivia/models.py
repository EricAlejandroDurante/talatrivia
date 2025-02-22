from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError

from ..core.models import BaseModel

class Question(BaseModel):
    DIFFICULTY_CHOICES = [
        ('easy', 'Fácil'),
        ('medium', 'Medio'),
        ('hard', 'Difícil'),
    ]

    text = models.TextField()
    difficulty = models.CharField(choices=DIFFICULTY_CHOICES, max_length=6)
    
    def save(self, *args, **kwargs):
        if self.difficulty == 'easy':
            self.score = 1
        elif self.difficulty == 'medium':
            self.score = 2
        else:
            self.score = 3
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pregunta: {self.text}"

class Answer(BaseModel):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Trivia(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    questions = models.ManyToManyField(Question)
    users = models.ManyToManyField(User, related_name='trivias', blank=True)

class TriviaAttempt(BaseModel):
    user = models.ForeignKey(User, related_name='trivia_attempts', on_delete=models.CASCADE)
    trivia = models.ForeignKey(Trivia, related_name='attempts', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    total_score = models.IntegerField(default=0)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'trivia'], name='unique_user_trivia_attempt')
        ]

    def is_time_expired(self):
        return timezone.now() > self.start_time + timedelta(minutes=5)

    def __str__(self):
        return f"Intento de {self.user.name} en {self.trivia.title}"
    
    @classmethod
    def start_trivia(cls, user, trivia_id):
        from .models import Trivia
        
        if not trivia_id:
            raise ValidationError('Ha ocurrido un error al comenzar la trivia.')

        try:
            trivia = Trivia.objects.get(id=trivia_id)
        except Trivia.DoesNotExist:
            raise ValidationError('Trivia no encontrada.')

        if trivia.users.filter(id=user.id).count() == 0:
            raise ValidationError('No estás asignado a esta trivia.')

        if cls.objects.filter(user=user, trivia=trivia).exists():
            raise ValidationError('Ya has iniciado esta trivia.')

        return cls.objects.create(user=user, trivia=trivia)
    
    def submit_answers(self, answers_data):
        """
        Procesa las respuestas de un intento de trivia y actualiza el puntaje.
        """
        correct_answers = 0
        total_questions = self.trivia.questions.count()

        for answer_data in answers_data:
            question_id = answer_data.get('question')
            answer_id = answer_data.get('answer')

            try:
                question = Question.objects.get(id=question_id)
                answer = Answer.objects.get(id=answer_id, question=question)
                is_correct = answer.is_correct

                AnswerSubmission.objects.create(
                    attempt=self,
                    question=question,
                    answer=answer,
                    is_correct=is_correct
                )

                if is_correct:
                    correct_answers += 1
            except (Question.DoesNotExist, Answer.DoesNotExist):
                continue

        self.total_score = correct_answers
        self.completed = True
        self.save()

        return {
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'total_score': self.total_score,
        }
    
class AnswerSubmission(BaseModel):
    attempt = models.ForeignKey(TriviaAttempt, related_name='answer_submissions', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answer_submissions', on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, related_name='answer_submissions', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Respuesta de {self.attempt.user.name} para la pregunta: {self.question.text}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
