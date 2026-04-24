from django.contrib.auth.models import User
from decimal import Decimal
from .models import Group


def get_group_balances(group):
    """
    Calculate net balances for each member in a group.
    Returns dict: {user: net_balance}
    Positive = owed money, Negative = owes money
    """
    balances = {}
    for member in group.members.all():
        balances[member] = Decimal('0.00')

    # Also include creator
    balances[group.created_by] = balances.get(group.created_by, Decimal('0.00'))

    for expense in group.expenses.all():
        payer = expense.paid_by
        if payer not in balances:
            balances[payer] = Decimal('0.00')

        for split in expense.splits.all():
            user = split.user
            if user not in balances:
                balances[user] = Decimal('0.00')

            if user == payer:
                # Payer's portion doesn't create debt
                continue
            else:
                if not split.is_settled:
                    # Payer is owed this amount
                    balances[payer] += split.amount
                    # User owes this amount
                    balances[user] -= split.amount

    return balances


def get_settlement_suggestions(group):
    """
    Generate minimal settlement transactions using a greedy algorithm.
    Returns list of dicts: {debtor, creditor, amount}
    """
    balances = get_group_balances(group)

    debtors = [(user, -bal) for user, bal in balances.items() if bal < 0]
    creditors = [(user, bal) for user, bal in balances.items() if bal > 0]

    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    settlements = []
    i, j = 0, 0

    while i < len(debtors) and j < len(creditors):
        debtor, debt = debtors[i]
        creditor, credit = creditors[j]

        amount = min(debt, credit)
        if amount > Decimal('0.01'):
            settlements.append({
                'debtor': debtor,
                'creditor': creditor,
                'amount': round(amount, 2)
            })

        debtors[i] = (debtor, debt - amount)
        creditors[j] = (creditor, credit - amount)

        if debtors[i][1] < Decimal('0.01'):
            i += 1
        if creditors[j][1] < Decimal('0.01'):
            j += 1

    return settlements


def get_group_summary(group):
    """Return summary stats for a group."""
    expenses = group.expenses.all()
    total = sum(e.amount for e in expenses)
    settled = sum(
        split.amount
        for e in expenses
        for split in e.splits.filter(is_settled=True)
    )
    return {
        'total_expenses': total,
        'settled_amount': settled,
        'pending_amount': total - settled,
        'expense_count': expenses.count(),
        'member_count': group.members.count() + 1,
    }
