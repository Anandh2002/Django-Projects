from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,logout
from .models import Expense, Income
from .forms import ExpenseForm, IncomeForm
from django.db.models.functions import TruncMonth
from django.db.models import Sum

from datetime import date
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.http import require_http_methods

@login_required
def dashboard(request):
    today = date.today()
    this_month = today.replace(day=1)

    expenses = Expense.objects.filter(user=request.user, date__month=today.month, date__year=today.year)
    income_qs = Income.objects.filter(user=request.user, month__year=today.year, month__month=today.month)

    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    income_amount = income_qs.first().amount if income_qs.exists() else 0
    remaining = income_amount - total_expense

    return render(request, 'expenses/dashboard.html', {
        'expenses': expenses,
        'total': total_expense,
        'income': income_amount,
        'remaining': remaining,
    })

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/add_expense.html', {'form': form})


@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('dashboard')
    else:
        form = IncomeForm()
    return render(request, 'expenses/add_income.html', {'form': form})

@login_required
def delete_expense(request, id):
    Expense.objects.filter(id=id, user=request.user).delete()
    return redirect('dashboard')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@require_http_methods(["GET", "POST"])
def custom_logout(request):
    logout(request)
    # return render(request, 'registration/logged_out.html')
    return redirect('login')

