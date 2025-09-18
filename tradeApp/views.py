from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import requests
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Deposit, Withdrawal


# from . forms import UserRegisterForm 



# accounts/views.py
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import withdraw_request, contact_request, Trade

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

@login_required()
def dashboard(request):
    
    return render(request, 'dashboard/home.html')



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

def balance(request):
    
    return render(request, 'home/balance.html')

def market_table(request):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 20,   # fetch top 20 coins
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        coins = response.json()
    except requests.RequestException:
        coins = []  # fallback if API fails

    return render(request, "dashboard/markets.html", {"coins": coins})

def chart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        # parse inputs (defensive)
        try:
            amount = Decimal(str(data.get('amount', 0)))
            price = Decimal(str(data.get('price', 0)))
            profit_percentage = Decimal(str(data.get('profit', 0)))
            duration = int(data.get('duration', 0))
        except (InvalidOperation, ValueError, TypeError):
            return JsonResponse({'error': 'Invalid numeric input'}, status=400)

        coin = data.get('coin')
        direction = data.get('direction')

        if amount < Decimal('10'):
            return JsonResponse({'error': 'Minimum trade is $10'}, status=400)

        # Normalize wallet amounts to Decimal
        try:
            wallet_amount = Decimal(str(user.wallet.amount))
        except (InvalidOperation, TypeError):
            wallet_amount = Decimal('0')

        if wallet_amount < amount:
            return JsonResponse({'error': 'Insufficient balance'}, status=400)

        # Deduct stake from available (do NOT add to locked here)
        user.wallet.amount = wallet_amount - amount
        # save using Decimal or cast back depending on your Wallet field type
        user.wallet.save()

        # Create trade (status running, end_time set in save())
        trade = Trade.objects.create(
            user=user,
            coin=coin or '',
            direction=direction or '',
            price=float(price),  # store as float in model (or Decimal if model uses DecimalField)
            amount=float(amount),
            profit_percentage=float(profit_percentage),
            duration=duration,
            status='running'
        )

        # return current available and current locked (locked not yet changed)
        try:
            locked_val = Decimal(str(user.wallet.locked))
        except (InvalidOperation, TypeError):
            locked_val = Decimal('0')

        return JsonResponse({
            'success': True,
            'trade_id': trade.id,
            'new_balance': float(user.wallet.amount),
            'locked_balance': float(locked_val)
        })

    # GET → render page
    return render(request, 'dashboard/charts.html')



# finalize_trade view - call when countdown ends
@require_POST
def finalize_trade(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        print("Invalid JSON in finalize_trade")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    trade_id = data.get('trade_id')
    if not trade_id:
        print("No trade_id provided")
        return JsonResponse({'error': 'No trade_id provided'}, status=400)

    trade = get_object_or_404(Trade, id=trade_id, user=request.user)
    print(f"Found trade: {trade.id}, status: {trade.status}")

    if trade.status != 'running':
        print(f"Trade {trade.id} already finalized or not running")
        return JsonResponse({'error': 'Trade already finalized or not running'}, status=400)

    now = timezone.now()
    if trade.end_time and now < trade.end_time:
        seconds_left = int((trade.end_time - now).total_seconds())
        print(f"Trade {trade.id} still running, seconds left: {seconds_left}")
        return JsonResponse({'error': 'Trade still running', 'seconds_left': seconds_left}, status=400)

    # Compute profit and total to credit
    amount_dec = Decimal(str(trade.amount))
    profit_pct_dec = Decimal(str(trade.profit_percentage))
    profit_dec = (amount_dec * profit_pct_dec) / Decimal('100')
    total_to_credit = amount_dec + profit_dec
    print(f"Trade {trade.id}: amount={amount_dec}, profit={profit_dec}, total_to_credit={total_to_credit}")

    # Update locked balance
    try:
        locked_val = Decimal(str(request.user.wallet.locked))
    except (InvalidOperation, TypeError):
        print("Invalid locked value, setting to 0")
        locked_val = Decimal('0')

    request.user.wallet.locked = locked_val + total_to_credit
    print(f"Updating locked balance: {locked_val} + {total_to_credit} = {request.user.wallet.locked}")
    request.user.wallet.save()

    # Mark trade as completed
    trade.status = 'completed'
    trade.save()
    print(f"Trade {trade.id} marked as completed")

    # Return updated balances
    try:
        available_val = Decimal(str(request.user.wallet.amount))
    except (InvalidOperation, TypeError):
        print("Invalid available value, setting to 0")
        available_val = Decimal('0')

    response = {
        'success': True,
        'available': float(available_val),
        'locked': float(request.user.wallet.locked)
    }
    print(f"Returning response: {response}")
    return JsonResponse(response)


@login_required
def get_trades(request):
    if request.method == "GET":
        # temporarily show all trades to verify
        trades = Trade.objects.filter(user=request.user).order_by('-created_at')
        trade_data = [
            {
                'trade_id': str(trade.trade_id),
                'coin': trade.coin,
                'direction': trade.direction,
                'amount': trade.amount,
                'price': trade.price,
                'profit': trade.profit_percentage,
                'duration': trade.duration,
                'status': trade.status,
                'created_at': trade.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for trade in trades
        ]
        return JsonResponse({'trades': trade_data})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def trades_page(request):
    return render(request, 'dashboard/order.html')


@login_required
def deposit_view(request):
    if request.method == 'POST':
        coin = request.POST.get('coin')
        amount = request.POST.get('amount')
        
        if not coin or not amount:
            messages.error(request, 'Please select a coin and enter a valid amount.')
            return redirect('/deposit')
        
        try:
            amount = float(amount)
            if amount < 10:
                messages.error(request, 'Amount must be at least $10.')
                return redirect('/deposit')
                
            wallet_addresses = {
                'bitcoin': 'bc1qkzhzvfm4rhlgx9lu9yz8nltspcs6k6ydk9dvwe',
                'ethereum': '0xc78abb708DB9D615e4A19aC36B51cDEa139031bC'
            }
            wallet_address = wallet_addresses.get(coin, '')
            
            Deposit.objects.create(
                user=request.user,
                coin=coin,
                amount=amount,
                wallet_address=wallet_address
            )
            
            messages.success(request, f'Deposit of ${amount} in {coin.capitalize()} submitted successfully!')
            return redirect('/deposit')
            
        except ValueError:
            messages.error(request, 'Invalid amount entered.')
            return redirect('deposit')
    
    return render(request, 'dashboard/deposit.html')

@login_required
def withdrawal_view(request):
    if request.method == 'POST':
        coin = request.POST.get('coin')
        amount = request.POST.get('amount')
        wallet_address = request.POST.get('wallet_address')
        
        # Validate input
        if not coin or not amount or not wallet_address:
            messages.error(request, 'Please select a coin, enter a valid amount, and provide a wallet address.')
            return redirect('/withdraw')
        
        try:
            amount = float(amount)
            if amount < 10:
                messages.error(request, 'Amount must be at least $10.')
                return redirect('/withdraw')
                
            # Basic wallet address validation (length check as an example)
            if len(wallet_address) < 20:
                messages.error(request, 'Invalid wallet address.')
                return redirect('/withdraw')
                
            # Save withdrawal
            Withdrawal.objects.create(
                user=request.user,
                coin=coin,
                amount=amount,
                wallet_address=wallet_address,
                status='pending'
            )
            
            messages.success(request, 'Withdrawal request submitted. Status: pending.')
            return redirect('/withdraw')
            
        except ValueError:
            messages.error(request, 'Invalid amount entered.')
            return redirect('/withdraw')
    
    return render(request, 'dashboard/withdrawal.html')