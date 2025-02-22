from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import AnswerSubmissionListView, TriviaAnswerView, QuestionViewSet, TriviaRankingView, TriviaViewSet, TriviaStartView

router = DefaultRouter()
router.register(r'questions', QuestionViewSet)
router.register(r'trivias', TriviaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('trivia/start/', TriviaStartView.as_view(), name='trivia-start'),
    path('trivia/answer/', TriviaAnswerView.as_view(), name='trivia-answer'),
    path('trivia/<uuid:trivia_id>/ranking/', TriviaRankingView.as_view(), name='trivia-ranking'),
    
    # Funcionalidad extra: Permite a los usuarios ver la trivia con el resultado las respuestas buenas y malas
    path('answer_submissions/<uuid:trivia_id>/', AnswerSubmissionListView.as_view(), name='answer-submission-list'),
]
