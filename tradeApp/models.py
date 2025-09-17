from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import uuid






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
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)   # <— changed
    locked = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    available = models.DecimalField(max_digits=12, decimal_places=2, default=0) # <— changed

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
    
    objects = CustomUserManager()
    # Add this method for compatibility with allauth
    def get_username(self):
        return self.email





class Trade(models.Model):
    DIRECTION_CHOICES = (
        ('up', 'Buy Up'),
        ('down', 'Buy Down'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trade_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    coin = models.CharField(max_length=50)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    amount = models.FloatField()
    profit_percentage = models.FloatField()
    duration = models.IntegerField()  # seconds
    price = models.FloatField(default=0)
    status = models.CharField(max_length=20, default='running')  # running/completed
    created_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.end_time and self.duration:
            self.end_time = timezone.now() + timezone.timedelta(seconds=self.duration)
        super().save(*args, **kwargs)



class Deposit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coin = models.CharField(max_length=50, choices=[('bitcoin', 'Bitcoin'), ('ethereum', 'Ethereum')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_address = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.coin} - ${self.amount}"



class Withdrawal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coin = models.CharField(max_length=50, choices=[('bitcoin', 'Bitcoin'), ('ethereum', 'Ethereum')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_address = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending', choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.coin} - ${self.amount} - {self.status}"

    class Meta:
        verbose_name = "Withdrawal"
        verbose_name_plural = "Withdrawals"