from django.db import models
from django.contrib.auth.models import User
from groups.models import Group
from decimal import Decimal


class Expense(models.Model):
    SPLIT_CHOICES = [
        ('equal', 'Equal Split'),
        ('custom', 'Custom Split'),
        ('percentage', 'Percentage Split'),
    ]

    CATEGORY_CHOICES = [
        ('food', 'Food & Dining'),
        ('transport', 'Transport'),
        ('accommodation', 'Accommodation'),
        ('entertainment', 'Entertainment'),
        ('shopping', 'Shopping'),
        ('utilities', 'Utilities'),
        ('medical', 'Medical'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paid_expenses')
    split_type = models.CharField(max_length=20, choices=SPLIT_CHOICES, default='equal')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    note = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} — ₹{self.amount}"

    def get_settled_amount(self):
        return sum(s.amount for s in self.splits.filter(is_settled=True))

    def get_pending_amount(self):
        return self.amount - self.get_settled_amount()

    def is_fully_settled(self):
        return all(s.is_settled for s in self.splits.exclude(user=self.paid_by))


class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_splits')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    is_settled = models.BooleanField(default=False)
    settled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['expense', 'user']

    def __str__(self):
        return f"{self.user.username} owes ₹{self.amount} for {self.expense.title}"
