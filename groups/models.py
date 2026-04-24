from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='member_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='group_images/', blank=True, null=True)

    CATEGORY_CHOICES = [
        ('trip', 'Trip'),
        ('home', 'Home'),
        ('food', 'Food'),
        ('entertainment', 'Entertainment'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_total_expenses(self):
        return sum(e.amount for e in self.expenses.all())

    def get_member_count(self):
        return self.members.count()

    def get_expense_count(self):
        return self.expenses.count()
