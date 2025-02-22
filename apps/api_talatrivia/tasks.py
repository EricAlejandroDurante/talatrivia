from celery import shared_task

from .models import TriviaAttempt

@shared_task
def check_and_complete_trivia_attempt(trivia_attempt_id):
    """
    Revisa un intento de trivia y marca como completado si ha pasado más de 5 minutos.
    """
    try:
        attempt = TriviaAttempt.objects.get(id=trivia_attempt_id)

        if not attempt.completed:
            attempt.completed = True
            attempt.save()

    except TriviaAttempt.DoesNotExist:
        pass
