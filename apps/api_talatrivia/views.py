from django.forms import ValidationError

from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView

from .models import AnswerSubmission, Question, Trivia
from .serializers import AnswerSubmissionSerializer, RankingSerializer, TriviaAnswerSerializer, QuestionSerializer, TriviaSerializer
from .models import TriviaAttempt
from .serializers import TriviaStartSerializer
from .tasks import check_and_complete_trivia_attempt


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class TriviaViewSet(viewsets.ModelViewSet):
    queryset = Trivia.objects.all().prefetch_related('questions__answers')
    serializer_class = TriviaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Trivia.objects.all().prefetch_related('questions__answers')
        else:
            return Trivia.objects.filter(users=user).prefetch_related('questions__answers')

    def get_object(self):
        """
        Sobrescribimos el método para obtener una trivia específica solo si está asignada al usuario.
        """
        obj = super().get_object()
        
        if self.request.method == 'DELETE' and self.request.user.is_superuser:
            return obj
        
        if self.request.user not in obj.users.all():
            raise PermissionDenied('No tienes permiso para ver esta trivia.')
        return obj

    @action(detail=True, methods=['get'])
    def specific_trivia(self, request, pk=None):
        """
        Acción personalizada para obtener una trivia específica, solo si está asignada al usuario.
        """
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

class TriviaRankingView(APIView):
    def get(self, request, trivia_id):
        attempts = TriviaAttempt.objects.filter(trivia_id=trivia_id).order_by('-total_score')

        if not attempts:
            return Response({"detail": "No attempts found for this trivia."}, status=404)

        serializer = RankingSerializer(attempts, many=True)
        return Response(serializer.data)

class TriviaStartView(generics.CreateAPIView):
    serializer_class = TriviaStartSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        trivia_id = request.data.get('trivia_id')

        try:
            trivia_attempt = TriviaAttempt.start_trivia(user, trivia_id)
            
            check_and_complete_trivia_attempt.apply_async(
                (trivia_attempt.id,),
                countdown=1 * 60
            )

        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Error inesperado: Porfavor intentelo mas tarde'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Trivia iniciada correctamente.'}, status=status.HTTP_201_CREATED)

class TriviaAnswerView(generics.CreateAPIView):
    serializer_class = TriviaAnswerSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            attempt_id = serializer.validated_data['attempt_id']
            answers_data = serializer.validated_data['answers']

            try:
                attempt = TriviaAttempt.objects.get(id=attempt_id, user=request.user, completed=False)
            except TriviaAttempt.DoesNotExist:
                return Response({"detail": "Intento de trivia no válido o ya completado."}, status=status.HTTP_400_BAD_REQUEST)

            result = attempt.submit_answers(answers_data)

            return Response({
                'message': 'Respuestas enviadas correctamente.',
                'correct_answers': result['correct_answers'],
                'total_questions': result['total_questions'],
                'total_score': result['total_score'],
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AnswerSubmissionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerSubmissionSerializer

    def get_queryset(self):
        return AnswerSubmission.objects.filter(attempt__user=self.request.user, attempt__trivia_id=self.kwargs['trivia_id'])