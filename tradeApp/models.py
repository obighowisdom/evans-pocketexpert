from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, BaseUserManager





# Create your models here.

class withdraw_request(models.Model):
    user = models.OneToOneField('tradeApp.CustomUser', null=True, on_delete=models.CASCADE)
    currency = models.CharField(max_length=2000, null=False, blank=False)
    amount = models.CharField(max_length=2000, null=False, blank=False)
    address = models.CharField(max_length=2000, null=False, blank=False)
    name = models.CharField(max_length=2000, null=False, blank=False)
    
     
   
    def __str__(self):
        return self.name

class contact_request(models.Model):
    user = models.OneToOneField('tradeApp.CustomUser', null=True, on_delete=models.CASCADE)
    subject = models.CharField(max_length=2000, null=False, blank=False)
    name = models.CharField(max_length=2000, null=False, blank=False)
    phone = models.CharField(max_length=20000, null=False, blank=False)
    message = models.CharField(max_length=2000, null=False, blank=False)
     
   
    def __str__(self):
        return self.name


class wallet(models.Model):
    user = models.OneToOneField('tradeApp.CustomUser', null=True, on_delete=models.CASCADE)
    amount = models.CharField(max_length=200, default='0.00')
       
    def __str__(self):
        return str(self.user)

# accounts/models.py

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# accounts/models.py
class CustomUser(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    # Add this method for compatibility with allauth
    def get_username(self):
        return self.email



# class Profile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
#     # Add other personal data fields
#     bio = models.TextField(max_length=500, blank=True)
#     birth_date = models.DateField(null=True, blank=True)
#     phone_number = models.CharField(max_length=15, blank=True)
#     address = models.CharField(max_length=255, blank=True)
    
#     def __str__(self):
#         return f"{self.user.email}'s profile"

# # Automatically create/update Profile when User is created/updated
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#     else:
#         instance.profile.save()