from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, TransactionForm
from .models import BankAccount, Transaction
import uuid

def home(request):
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            BankAccount.objects.create(
                user=user,
                account_number=str(uuid.uuid4())[:10]
            )
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    account, created = BankAccount.objects.get_or_create(
        user=request.user,
        defaults={
            'account_number': str(uuid.uuid4())[:10],
            'balance': 0.00
        }
    )
    
    transactions = Transaction.objects.filter(account=account).order_by('-timestamp')[:10]
    return render(request, 'accounts/dashboard.html', {
        'account': account,
        'transactions': transactions
    })

@login_required
def deposit(request):
    account, created = BankAccount.objects.get_or_create(
        user=request.user,
        defaults={
            'account_number': str(uuid.uuid4())[:10],
            'balance': 0.00
        }
    )
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            account.balance += amount
            account.save()
            
            Transaction.objects.create(
                account=account,
                transaction_type='DEPOSIT',
                amount=amount
            )
            messages.success(request, f'Successfully deposited ${amount}')
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'accounts/deposit.html', {'form': form})

@login_required
def withdraw(request):
    account, created = BankAccount.objects.get_or_create(
        user=request.user,
        defaults={
            'account_number': str(uuid.uuid4())[:10],
            'balance': 0.00
        }
    )
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if account.balance >= amount:
                account.balance -= amount
                account.save()
                
                Transaction.objects.create(
                    account=account,
                    transaction_type='WITHDRAWAL',
                    amount=amount
                )
                messages.success(request, f'Successfully withdrew ${amount}')
                return redirect('dashboard')
            else:
                messages.error(request, 'Insufficient funds!')
    else:
        form = TransactionForm()
    return render(request, 'accounts/withdraw.html', {'form': form})