from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Task


class TaskAPITestCase(APITestCase):

    def setUp(self):
        # runs before every test
        self.client = APIClient()

        # create two users
        self.user1 = User.objects.create_user(username='user1', password='pass1234')
        self.user2 = User.objects.create_user(username='user2', password='pass1234')

        # get tokens
        response = self.client.post('/api/v1/token/', {'username': 'user1', 'password': 'pass1234'})
        self.token1 = response.data['access']

        response = self.client.post('/api/v1/token/', {'username': 'user2', 'password': 'pass1234'})
        self.token2 = response.data['access']

        # create a task for user1
        self.task = Task.objects.create(
            owner=self.user1,
            title='Test Task',
            status='pending',
            priority='medium'
        )

    def test_user_can_create_task(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.post('/api/v1/tasks/', {
            'title': 'New Task',
            'status': 'pending',
            'priority': 'high'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_list_own_tasks(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_see_other_users_tasks(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        response = self.client.get(f'/api/v1/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_access_tasks(self):
        response = self.client.get('/api/v1/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_update_own_task(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        response = self.client.patch(f'/api/v1/tasks/{self.task.id}/', {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_delete_other_users_task(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        response = self.client.delete(f'/api/v1/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)