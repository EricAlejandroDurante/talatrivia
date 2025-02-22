from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from oauth2_provider.models import Application, AccessToken
from oauth2_provider.settings import oauth2_settings

from .models import Question, Answer, Trivia


class QuestionViewSetTest(APITestCase):

    def setUp(self):
        """Configurar el entorno de pruebas"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        self.app = Application.objects.create(
            name="Test Application",
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            user=self.user
        )

        self.token = AccessToken.objects.create(
            user=self.user,
            scope='read write',
            expires=timezone.now() + timedelta(hours=1),
            token='testtoken',
            application=self.app
        )
        
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.token)
        
        self.question = Question.objects.create(
            text="¿Cuál es la capital de Francia?",
            difficulty="medium"
        )
        self.answers = [
            Answer.objects.create(question=self.question, text="París", is_correct=True),
            Answer.objects.create(question=self.question, text="Londres", is_correct=False),
            Answer.objects.create(question=self.question, text="Madrid", is_correct=False),
            Answer.objects.create(question=self.question, text="Berlín", is_correct=False),
        ]

    def test_create_question_authenticated(self):
        """Creación de una pregunta"""
        url = reverse('question-list')
        data = {
            "text": "Que numero es igual a 8x9",
            "difficulty": "hard",
            "answers": [
                {"text": "2", "is_correct": False},
                {"text": "2", "is_correct": False},
                {"text": "72", "is_correct": True},
                {"text": "2", "is_correct": False}
            ]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 2)
        self.assertEqual(Answer.objects.count(), 8)
    
    def test_create_question_without_authentication(self):
        """Creación de una pregunta sin autenticarse"""
        self.client.credentials()
        url = reverse('question-list')
        data = {
            "text": "Puedo hacer una pregunta sin estar autenticado?",
            "difficulty": "easy",
            "answers": [
                {"text": "Si", "is_correct": False},
                {"text": "No", "is_correct": True}
            ]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_question_list_authenticated(self):
        """obtener la lista de preguntas"""
        url = reverse('question-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_question_authenticated(self):
        """Eliminación de una pregunta"""
        url = reverse('question-detail', args=[self.question.id])
        response = self.client.delete(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Question.objects.count(), 0)
        self.assertEqual(Answer.objects.count(), 0)

class TriviaViewSetTest(APITestCase):

    def setUp(self):
        """Configura el entorno de pruebas con autenticación"""
        self.user1 = User.objects.create_user(username='user1', password='testpass1')
        self.user2 = User.objects.create_user(username='user2', password='testpass2')
        self.superuser = User.objects.create_superuser(username='admin', password='adminpass')

        self.app = Application.objects.create(
            name="Test Application",
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            user=self.user1
        )

        self.token_user1 = AccessToken.objects.create(
            user=self.user1,
            scope='read write',
            expires=timezone.now() + timedelta(hours=1),
            token='token_user1',
            application=self.app
        )
        
        self.token_superuser = AccessToken.objects.create(
            user=self.superuser,
            scope='read write',
            expires=timezone.now() + timedelta(hours=1),
            token='token_superuser',
            application=self.app
        )
        
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_user1.token)
        self.question1 = Question.objects.create(text="Pregunta 1", difficulty="easy")
        self.question2 = Question.objects.create(text="Pregunta 2", difficulty="medium")
        
        Answer.objects.create(question=self.question1, text="Respuesta 1", is_correct=True)
        Answer.objects.create(question=self.question1, text="Respuesta 2", is_correct=False)
        Answer.objects.create(question=self.question2, text="Respuesta 3", is_correct=True)
        Answer.objects.create(question=self.question2, text="Respuesta 4", is_correct=False)
        
        self.trivia = Trivia.objects.create(title="Trivia 1", description="Descripción 1")
        self.trivia.questions.set([self.question1, self.question2])
        self.trivia.users.set([self.user1])

    def test_create_trivia_authenticated(self):
        """Prueba la creación de una trivia autenticado como un usuario regular."""
        url = reverse('trivia-list')
        data = {
            "title": "Nueva Trivia",
            "description": "Descripción de la nueva trivia",
            "question_ids": [str(self.question1.id), str(self.question2.id)],
            "user_ids": [self.user1.id, self.user2.id]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trivia.objects.count(), 2)
    
    def test_create_trivia_without_authentication(self):
        """Creación de una trivia sin autenticarse"""
        self.client.credentials()
        url = reverse('trivia-list')
        data = {
            "title": "Trivia sin autenticación",
            "description": "Descripción",
            "question_ids": [str(self.question1.id)],
            "user_ids": [self.user1.id]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_trivia_as_superuser(self):
        """Superusuario pueda obtener todas las trivias."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_superuser.token)
        url = reverse('trivia-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Trivia.objects.count())

    def test_get_trivia_as_user(self):
        """Usuario solo obtenga las trivias asignadas a él."""
        url = reverse('trivia-list')
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Trivia 1")

    def test_access_restricted_trivia(self):
        """Usuario no pueda acceder a trivias no asignadas."""
        trivia = Trivia.objects.create(title="Trivia No Permitida", description="No asignada a user1")
        trivia.users.set([self.user2])
        
        url = reverse('trivia-detail', args=[trivia.id])
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
      
    def test_delete_trivia_as_superuser(self):
        """Eliminación de una trivia autenticado como superusuario."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_superuser.token)
        url = reverse('trivia-detail', args=[self.trivia.id])
        response = self.client.delete(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Trivia.objects.count(), 0)

    def test_delete_trivia_as_regular_user(self):
        """Usuario regular no pueda eliminar trivias."""
        url = reverse('trivia-detail', args=[self.trivia.id])
        response = self.client.delete(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Trivia.objects.count(), 1)

