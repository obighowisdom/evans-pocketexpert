from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# from . forms import UserRegisterForm 



# accounts/views.py
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import withdraw_request, contact_request

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'home/login.html'

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index:dashboard')
    template_name = 'home/register.html'


def index(request):
    
    return render(request, 'home/index.html')

# def register(request):
#     if request.method == "POST":
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
            
#             messages.success(request, f'Hi {username}, your account was created successfully')
#             return redirect("index:login")
#     else:
#         form = UserRegisterForm()
    
#     return render(request, 'home/register.html', {'form':form})

# def login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password1 = request.POST['password1']
        
#         user = authenticate(username=username, password=password1)
        
#         if user is not None:
#             login(request, user)
#             fname = user.first_name
#             # messages.success(request, "Logged In Sucessfully!!")
#             return render(request, "index.html", {"fname":fname})
#         else:
#             messages.error(request, "Bad Credentials!!")
#             return redirect("index:register")
    
#     return render(request, 'home/login.html')

def about(request):
    
    return render(request, 'home/about.html')

def logout(request):
    
    return render(request, 'home/about.html')

def demo(request):
    
    return render(request, 'home/demo.html')

def quick(request):
    
    return render(request, 'home/quick.html')

def policy(request):
    
    return render(request, 'home/policy.html')


def dashboard(request):
    
    return render(request, 'dashboard/home.html')

@login_required()
def deposit(request):
    
    return render(request, 'dashboard/deposit.html')

@login_required()
def withdraw(request):
    if request.method == 'POST':
        currency = request.POST['currency']
        amount = request.POST['amount']
        address = request.POST['address']
        name = request.POST['name']
        
        user_request = withdraw_request(currency=currency, amount=amount, address=address, name=name)
        user_request.save()
        messages.success(request, f'Successfully submitted... You will be credited upon confirmation')
        return redirect("index:dashboard")

    
    return render(request, 'dashboard/withdraw.html')

def profile(request):
    
    return render(request, 'dashboard/profile.html')

@login_required()
def contact(request):
    if request.method == 'POST':
       subject = request.POST['subject']
       name = request.POST['name']
       phone = request.POST['phone']
       
       
       message = request.POST['message']


       user_contacts = contact_request(subject=subject, name=name, phone=phone, message=message)
       user_contacts.save()
       messages.success(request, f'Submitted successfully, you will be contacted shortly')
       return redirect("index:dashboard")
    
    return render(request, 'dashboard/contact.html')