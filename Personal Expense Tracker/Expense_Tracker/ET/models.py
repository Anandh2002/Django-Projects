from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"
    
    
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()  # You can just store any date in the month
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['user', 'month']  # One income per user per month

    def __str__(self):
        return f"{self.user.username} - {self.month.strftime('%B %Y')} - ₹{self.amount}"
