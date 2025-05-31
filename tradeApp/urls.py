from django.urls import path
from . import views
from django.contrib.auth import views as auth_view
# from tradeApp.forms import UserLoginForm
from .views import CustomLoginView, SignUpView


app_name = 'tradeAppurl'

urlpatterns = [
    path('', views.index, name = 'index'),
    # path('register/', views.register, name = 'register'),
    # path('login/', auth_view.LoginView.as_view(template_name='home/login.html', authentication_form=UserLoginForm), name = 'login'),
    path('logout/', auth_view.LogoutView.as_view(template_name='logout.html'), name = 'logout'),
    path('about/', views.about, name = 'about'),
    path('demo/', views.demo, name = 'demo'),
    path('quick/', views.quick, name = 'quick'),
    path('policy/', views.policy, name = 'policy'),

    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('deposit/', views.deposit, name = 'deposit'),
    path('withdraw/', views.withdraw, name = 'withdraw'),
    # path('profile/', views.profile, name = 'profile'),
    path('contact/', views.contact, name = 'contact'),

    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', SignUpView.as_view(), name='register'),

    
]