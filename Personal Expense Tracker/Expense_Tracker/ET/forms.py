from django import forms
from .models import Expense,Income
from datetime import datetime

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['month', 'amount']
        widgets = {
            'month': forms.DateInput(attrs={'type': 'date'}),  # HTML5 month picker
        }
        
    def clean_month(self):
        month_input = self.cleaned_data['month']
        # If month_input is a string like "2025-06", convert it to full date
        if isinstance(month_input, str):
            month_input = datetime.strptime(month_input, "%Y-%m")
        return month_input.replace(day=1)  # always use 1st of the month