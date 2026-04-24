from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
import json

from .models import Expense, ExpenseSplit
from .forms import ExpenseForm, ExpenseFilterForm
from .services import create_expense, update_expense, mark_split_settled, get_user_dashboard_data
from groups.models import Group


@login_required
def add_expense(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk)
    user = request.user
    if user != group.created_by and user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('group_list')

    if request.method == 'POST':
        form = ExpenseForm(request.POST, group=group)
        if form.is_valid():
            data = form.cleaned_data
            participants = list(data['participants'])
            custom_amounts = {}
            percentages = {}

            split_type = data['split_type']
            if split_type == 'custom':
                for p in participants:
                    val = request.POST.get(f'custom_{p.id}', '0')
                    custom_amounts[str(p.id)] = val or '0'
            elif split_type == 'percentage':
                for p in participants:
                    val = request.POST.get(f'pct_{p.id}', '0')
                    percentages[str(p.id)] = val or '0'

            expense = create_expense(
                title=data['title'],
                amount=data['amount'],
                group=group,
                paid_by=data['paid_by'],
                split_type=split_type,
                category=data['category'],
                note=data['note'],
                date=data['date'],
                participants=participants,
                custom_amounts=custom_amounts if custom_amounts else None,
                percentages=percentages if percentages else None,
            )
            messages.success(request, f'Expense "{expense.title}" added successfully!')
            return redirect('group_detail', pk=group.pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ExpenseForm(group=group, initial={'paid_by': user, 'date': timezone.now().date()})

    members = list(group.members.all())
    if group.created_by not in members:
        members = [group.created_by] + members

    return render(request, 'expenses/add_expense.html', {
        'form': form,
        'group': group,
        'members': members,
    })


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    group = expense.group
    user = request.user

    if user != group.created_by and user not in group.members.all():
        messages.error(request, 'Permission denied.')
        return redirect('group_list')

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, group=group)
        if form.is_valid():
            data = form.cleaned_data
            participants = list(data['participants'])
            custom_amounts = {}
            percentages = {}
            split_type = data['split_type']

            if split_type == 'custom':
                for p in participants:
                    val = request.POST.get(f'custom_{p.id}', '0')
                    custom_amounts[str(p.id)] = val or '0'
            elif split_type == 'percentage':
                for p in participants:
                    val = request.POST.get(f'pct_{p.id}', '0')
                    percentages[str(p.id)] = val or '0'

            update_expense(
                expense=expense,
                title=data['title'],
                amount=data['amount'],
                paid_by=data['paid_by'],
                split_type=split_type,
                category=data['category'],
                note=data['note'],
                date=data['date'],
                participants=participants,
                custom_amounts=custom_amounts if custom_amounts else None,
                percentages=percentages if percentages else None,
            )
            messages.success(request, 'Expense updated successfully!')
            return redirect('group_detail', pk=group.pk)
    else:
        current_participants = [s.user for s in expense.splits.all()]
        form = ExpenseForm(instance=expense, group=group,
                           initial={'participants': current_participants})

    members = list(group.members.all())
    if group.created_by not in members:
        members = [group.created_by] + members

    return render(request, 'expenses/edit_expense.html', {
        'form': form,
        'expense': expense,
        'group': group,
        'members': members,
    })


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    group = expense.group
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted.')
        return redirect('group_detail', pk=group.pk)
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})


@login_required
def expense_list(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk)
    expenses = group.expenses.all()

    form = ExpenseFilterForm(request.GET)
    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        split_type = form.cleaned_data.get('split_type')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if q:
            expenses = expenses.filter(Q(title__icontains=q) | Q(note__icontains=q))
        if category:
            expenses = expenses.filter(category=category)
        if split_type:
            expenses = expenses.filter(split_type=split_type)
        if date_from:
            expenses = expenses.filter(date__gte=date_from)
        if date_to:
            expenses = expenses.filter(date__lte=date_to)

    return render(request, 'expenses/expense_list.html', {
        'expenses': expenses,
        'group': group,
        'filter_form': form,
    })


@login_required
def settle_split(request, split_id):
    split = get_object_or_404(ExpenseSplit, id=split_id)
    group = split.expense.group
    user = request.user

    if user != group.created_by and user not in group.members.all():
        messages.error(request, 'Permission denied.')
        return redirect('group_list')

    mark_split_settled(split_id, settled=not split.is_settled)
    status = 'settled' if not split.is_settled else 'unsettled'
    messages.success(request, f'Split marked as {status}.')
    return redirect('group_detail', pk=group.pk)


@login_required
def dashboard(request):
    data = get_user_dashboard_data(request.user)
    return render(request, 'dashboard.html', data)
