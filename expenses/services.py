from decimal import Decimal
from django.utils import timezone
from .models import Expense, ExpenseSplit
from .utils import split_equal, split_by_percentage, split_custom


def create_expense(title, amount, group, paid_by, split_type, category, note, date,
                   participants, custom_amounts=None, percentages=None):
    """
    Create an expense and its splits.

    participants: list of User objects
    custom_amounts: {user.id: amount} for custom split
    percentages: {user.id: percentage} for percentage split
    """
    expense = Expense.objects.create(
        title=title,
        amount=amount,
        group=group,
        paid_by=paid_by,
        split_type=split_type,
        category=category,
        note=note,
        date=date,
    )

    _create_splits(expense, participants, custom_amounts, percentages)
    return expense


def update_expense(expense, title, amount, paid_by, split_type, category, note, date,
                   participants, custom_amounts=None, percentages=None):
    """Update expense and recalculate splits."""
    expense.title = title
    expense.amount = amount
    expense.paid_by = paid_by
    expense.split_type = split_type
    expense.category = category
    expense.note = note
    expense.date = date
    expense.save()

    # Remove old splits and recreate
    expense.splits.all().delete()
    _create_splits(expense, participants, custom_amounts, percentages)
    return expense


def _create_splits(expense, participants, custom_amounts, percentages):
    """Internal helper: create ExpenseSplit records."""
    if expense.split_type == 'equal':
        splits = split_equal(expense.amount, participants)

    elif expense.split_type == 'percentage':
        pct_map = {}
        for user in participants:
            pct_map[user] = Decimal(str(percentages.get(str(user.id), 0)))
        splits = split_by_percentage(expense.amount, pct_map)

    elif expense.split_type == 'custom':
        amt_map = {}
        for user in participants:
            amt_map[user] = Decimal(str(custom_amounts.get(str(user.id), 0)))
        splits = split_custom(amt_map)

    else:
        splits = split_equal(expense.amount, participants)

    for user, amount in splits.items():
        is_settled = (user == expense.paid_by)
        ExpenseSplit.objects.create(
            expense=expense,
            user=user,
            amount=amount,
            percentage=percentages.get(str(user.id), Decimal('0')) if percentages else Decimal('0'),
            is_settled=is_settled,
        )


def mark_split_settled(split_id, settled=True):
    """Mark a single split as settled."""
    split = ExpenseSplit.objects.get(id=split_id)
    split.is_settled = settled
    split.settled_at = timezone.now() if settled else None
    split.save()
    return split


def get_user_dashboard_data(user):
    """Aggregate dashboard data for a user."""
    from groups.models import Group
    from django.db.models import Q, Sum

    groups = Group.objects.filter(Q(created_by=user) | Q(members=user)).distinct()

    total_owed = Decimal('0.00')      # others owe me
    total_owing = Decimal('0.00')     # I owe others

    for split in ExpenseSplit.objects.filter(user=user, is_settled=False).select_related('expense'):
        if split.expense.paid_by != user:
            total_owing += split.amount

    for split in ExpenseSplit.objects.filter(
            expense__paid_by=user, is_settled=False
    ).exclude(user=user):
        total_owed += split.amount

    recent_expenses = Expense.objects.filter(
        Q(paid_by=user) | Q(splits__user=user)
    ).distinct().order_by('-date')[:5]

    return {
        'groups': groups,
        'group_count': groups.count(),
        'total_owed': total_owed,
        'total_owing': total_owing,
        'net_balance': total_owed - total_owing,
        'recent_expenses': recent_expenses,
    }
