# accounts/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        """
        Override the default behavior because our user model doesn't use usernames
        """
        user.username = None  # No username field
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Set email as the primary identifier and don't use username
        """
        user = super().populate_user(request, sociallogin, data)
        user.username = None  # Make sure username is None
        user.email = data.get('email')
        return user