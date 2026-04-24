from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from groups.models import Group
from .parser import parse_expense_from_text, get_group_ai_summary, auto_categorize


@login_required
def parse_expense_view(request):
    """Natural language expense parser view."""
    groups = Group.objects.filter(members=request.user) | Group.objects.filter(created_by=request.user)
    groups = groups.distinct()
    parsed = None
    user_input = ''

    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        if user_input:
            parsed = parse_expense_from_text(user_input)
            if parsed.get('error') and not parsed.get('fallback'):
                messages.warning(request, f"AI unavailable — used smart fallback: {parsed['error']}")
            elif parsed.get('fallback'):
                messages.info(request, "Used rule-based parsing (AI key not configured).")
            else:
                messages.success(request, "MintSense parsed your expense!")
        else:
            messages.error(request, 'Please enter a description.')

    return render(request, 'ai_mintsense/parse_expense.html', {
        'groups': groups,
        'parsed': parsed,
        'user_input': user_input,
    })


@login_required
def group_summary_view(request, group_pk):
    """AI-generated group summary."""
    group = get_object_or_404(Group, pk=group_pk)
    summary = get_group_ai_summary(group)
    return JsonResponse({'summary': summary})


@login_required
def autocategorize_view(request):
    """AJAX endpoint: auto-categorize an expense title."""
    if request.method == 'POST':
        title = request.POST.get('title', '')
        category = auto_categorize(title) if title else 'other'
        return JsonResponse({'category': category})
    return JsonResponse({'error': 'POST required'}, status=400)


# URL config lives in ai_mintsense/urls.py
def urls():
    from django.urls import path
    return [
        path('parse/', parse_expense_view, name='parse_expense'),
        path('group/<int:group_pk>/summary/', group_summary_view, name='group_ai_summary'),
        path('autocategorize/', autocategorize_view, name='autocategorize'),
    ]
