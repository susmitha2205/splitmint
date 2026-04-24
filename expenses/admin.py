from django.contrib import admin
from .models import Expense, ExpenseSplit


class ExpenseSplitInline(admin.TabularInline):
    model = ExpenseSplit
    extra = 0
    readonly_fields = ['settled_at']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'group', 'paid_by', 'split_type', 'category', 'date']
    list_filter = ['split_type', 'category', 'date']
    search_fields = ['title', 'note', 'paid_by__username', 'group__name']
    inlines = [ExpenseSplitInline]


@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ['expense', 'user', 'amount', 'is_settled', 'settled_at']
    list_filter = ['is_settled']
    search_fields = ['user__username', 'expense__title']
