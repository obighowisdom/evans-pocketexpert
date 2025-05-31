from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

from django.contrib.auth.forms import AuthenticationForm, UsernameField
from .models import CustomUser
from django.contrib.auth import get_user_model





# class UserLoginForm(AuthenticationForm):
#     def __init__(self, *args, **kwargs):
#         super(UserLoginForm, self).__init__(*args, **kwargs)

#     username = UsernameField(widget=forms.TextInput(
#         attrs={'class': 'form-control', 'placeholder': '', 'id': 'hello'}))
#     password = forms.CharField(widget=forms.PasswordInput(
#         attrs={
#             'class': 'form-control',
#             'placeholder': '',
#             'id': 'hi',
#         }
# ))


# # class UserRegisterForm(UserCreationForm):
# #     # email = forms.EmailField()
# #     username = forms.CharField(widget=forms.TextInput(attrs={
# #         "class": "form-control input",
# #         "type": "text",
# #         "placeholder": " enter username", 
# #     }), label="username")

# #     email = forms.EmailField(widget=forms.TextInput(attrs={
# #         "class": "form-control",
# #         "type": "email",
# #         "placeholder": " enter email ", 
# #     }))

# #     password1 = forms.CharField(widget=forms.TextInput(attrs={
# #         "class": "form-control js-f-pswd-input",
# #         "type": "password",
# #         "placeholder": " enter password ", 
# #     }))

# #     password2 = forms.CharField(widget=forms.TextInput(attrs={
# #         "class": "form-control",
# #         "type": "password",
# #         "placeholder": " re-enter password ", 
# #     }))


# #     class Meta:
# #         model = User
# #         fields = ['username', 'email', 'password1', 'password2']

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'password')
