from django.urls import path
from . import views

urlpatterns = [
    path('parse/', views.parse_expense_view, name='parse_expense'),
    path('group/<int:group_pk>/summary/', views.group_summary_view, name='group_ai_summary'),
    path('autocategorize/', views.autocategorize_view, name='autocategorize'),
]
