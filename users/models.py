from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_total_owed(self):
        """Total amount this user owes others."""
        from expenses.models import ExpenseSplit
        splits = ExpenseSplit.objects.filter(user=self.user, is_settled=False)
        total = sum(s.amount for s in splits if s.expense.paid_by != self.user)
        return total

    def get_total_owed_to_me(self):
        """Total amount others owe this user."""
        from expenses.models import ExpenseSplit
        splits = ExpenseSplit.objects.filter(
            expense__paid_by=self.user,
            is_settled=False
        ).exclude(user=self.user)
        return sum(s.amount for s in splits)
