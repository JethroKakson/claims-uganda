from django.test import TestCase
from django.contrib.auth.models import User
from Staff.models import Staff
from django.urls import reverse
from allauth.socialaccount.models import SocialApp

class LoginUserTestCase(TestCase):
    def setUp(self):
        self.social_app = SocialApp.objects.create(provider='google', name='google', client_id='1234567890', secret='1234567890')

    def test_login_user_active(self):
        user = User.objects.create_user('test', 'test@example.com', 'password')
        user.staff = Staff.objects.create(status='Active', user=user)
        user.save()
        response = self.client.post(reverse('login'), {'username': 'test', 'password': 'password'})
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_user_inactive(self):
        user = User.objects.create_user('test', 'test@example.com', 'password')
        user.staff = Staff.objects.create(status='Inactive', user=user)
        user.save()
        response = self.client.post(reverse('login'), {'username': 'test', 'password': 'password'})
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(response.context['messages']._loaded_messages[0].message, 'Your account is inactive. Please contact the admin.')

    def test_login_user_not_authenticated(self):
        response = self.client.post(reverse('login'), {'username': 'test', 'password': 'wrongpassword'})
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(response.context['messages']._loaded_messages[0].message, 'Invalid username or password.')

    def test_login_user_next_param(self):
        response = self.client.get(reverse('login'), {'next': reverse('dashboard')})
        self.assertContains(response, "Your session has expired. Please log in again.")

    def test_social_login(self):
        response = self.client.get(reverse('socialaccount_login', args=['google']))
        self.assertContains(response, "Google")
        self.assertContains(response, "Login with Google")

