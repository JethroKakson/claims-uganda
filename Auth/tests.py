from django.test import TestCase
from django.contrib.auth.models import User
from Staff.models import Staff

class LoginUserTestCase(TestCase):
    def test_login_user_active(self):
        user = User.objects.create_user('test', 'test@example.com', 'password')
        user.staff = Staff.objects.create(status='Active')
        user.save()
        response = self.client.post('/auth/login/', {'username': 'test', 'password': 'password'})
        self.assertRedirects(response, '/dashboard/')

    def test_login_user_inactive(self):
        user = User.objects.create_user('test', 'test@example.com', 'password')
        user.staff = Staff.objects.create(status='Inactive')
        user.save()
        response = self.client.post('/auth/login/', {'username': 'test', 'password': 'password'})
        self.assertRedirects(response, '/auth/login/')
        self.assertEqual(response.context['messages']._loaded_messages[0].message, 'Your account is inactive. Please contact the admin.')

    def test_login_user_not_authenticated(self):
        response = self.client.post('/auth/login/', {'username': 'test', 'password': 'wrongpassword'})
        self.assertRedirects(response, '/auth/login/')
        self.assertEqual(response.context['messages']._loaded_messages[0].message, 'Invalid username or password.')

    def test_login_user_next_param(self):
        response = self.client.get('/auth/login/', {'next': '/dashboard/'})
        self.assertContains(response, "Your session has expired. Please log in again.")
