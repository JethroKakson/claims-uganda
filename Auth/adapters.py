from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import messages

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        # Disable signup for social logins
        return False

    def pre_social_login(self, request, sociallogin):
        """
        This method is called before the social login is processed.
        If the user already exists, log them in directly.
        """
        email = sociallogin.user.email
        try:
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)  # Connect the existing user to the social account
        except User.DoesNotExist:
            messages.error(request, f"Contact admin for an account.")
            pass


     