from django.test import TestCase
from django.contrib.auth.models import User
from Staff.models import Staff
from django.urls import reverse
from allauth.socialaccount.models import SocialApp
from claims.settings import SOCIAL_AUTH_GOOGLE_CLIENT_ID, SOCIAL_AUTH_GOOGLE_SECRET
from django.contrib.messages import get_messages

class LoginUserTestCase(TestCase):
    def setUp(self):
        self.social_app = SocialApp.objects.create(provider='google', name='Google Auth', client_id=SOCIAL_AUTH_GOOGLE_CLIENT_ID, secret=SOCIAL_AUTH_GOOGLE_SECRET, key=SOCIAL_AUTH_GOOGLE_SECRET)

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
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your account is inactive. Please contact the admin.')

    def test_login_user_not_authenticated(self):
        response = self.client.post(reverse('login'), {'username': 'test', 'password': 'wrongpassword'})
        self.assertRedirects(response, reverse('login'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid username or password.')

    def test_login_user_next_param(self):
        response = self.client.get(reverse('login'), {'next': reverse('dashboard')})
        self.assertContains(response, "Your session has expired. Please log in again.")

