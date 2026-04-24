from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Group
from .forms import GroupForm
from .services import get_group_balances, get_settlement_suggestions, get_group_summary


@login_required
def group_list(request):
    user = request.user
    groups = Group.objects.filter(
        Q(created_by=user) | Q(members=user)
    ).distinct().order_by('-created_at')

    query = request.GET.get('q', '')
    if query:
        groups = groups.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request, 'groups/group_list.html', {'groups': groups, 'query': query})


@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, current_user=request.user)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            form.save_m2m()
            group.members.add(request.user)
            messages.success(request, f'Group "{group.name}" created successfully!')
            return redirect('group_detail', pk=group.pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = GroupForm(current_user=request.user)
    return render(request, 'groups/create_group.html', {'form': form, 'title': 'Create Group'})


@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    user = request.user
    if user != group.created_by and user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('group_list')

    expenses = group.expenses.all().order_by('-created_at')
    balances = get_group_balances(group)
    settlements = get_settlement_suggestions(group)
    summary = get_group_summary(group)

    return render(request, 'groups/group_detail.html', {
        'group': group,
        'expenses': expenses,
        'balances': balances,
        'settlements': settlements,
        'summary': summary,
    })


@login_required
def edit_group(request, pk):
    group = get_object_or_404(Group, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=group, current_user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group updated successfully!')
            return redirect('group_detail', pk=group.pk)
    else:
        form = GroupForm(instance=group, current_user=request.user)
    return render(request, 'groups/create_group.html', {'form': form, 'title': 'Edit Group', 'group': group})


@login_required
def delete_group(request, pk):
    group = get_object_or_404(Group, pk=pk, created_by=request.user)
    if request.method == 'POST':
        name = group.name
        group.delete()
        messages.success(request, f'Group "{name}" deleted.')
        return redirect('group_list')
    return render(request, 'groups/group_confirm_delete.html', {'group': group})
