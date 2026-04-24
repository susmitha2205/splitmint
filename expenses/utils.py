from decimal import Decimal, ROUND_HALF_UP


def split_equal(amount, users):
    """Split amount equally among users. Returns {user: amount}."""
    n = len(users)
    if n == 0:
        return {}
    per_person = (Decimal(str(amount)) / n).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    splits = {user: per_person for user in users}

    # Handle rounding remainder — assign to first user
    total_assigned = per_person * n
    remainder = Decimal(str(amount)) - total_assigned
    if remainder != 0 and users:
        first = list(users)[0]
        splits[first] = splits[first] + remainder

    return splits


def split_by_percentage(amount, user_percentages):
    """
    Split amount by percentage.
    user_percentages: {user: percentage_decimal}  e.g. {u1: 40, u2: 60}
    Returns {user: amount}
    """
    amount = Decimal(str(amount))
    splits = {}
    total_assigned = Decimal('0.00')
    users = list(user_percentages.keys())

    for i, user in enumerate(users):
        pct = Decimal(str(user_percentages[user])) / Decimal('100')
        if i == len(users) - 1:
            # Last user gets the remainder to avoid rounding issues
            splits[user] = (amount - total_assigned).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            share = (amount * pct).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            splits[user] = share
            total_assigned += share

    return splits


def split_custom(user_amounts):
    """
    Custom split where each user amount is explicitly given.
    user_amounts: {user: amount}
    Returns same dict after validation.
    """
    return {user: Decimal(str(amt)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            for user, amt in user_amounts.items()}


def validate_split_total(splits, total_amount, tolerance=Decimal('0.05')):
    """Check that splits sum approximately equals total_amount."""
    splits_total = sum(Decimal(str(v)) for v in splits.values())
    return abs(splits_total - Decimal(str(total_amount))) <= tolerance
