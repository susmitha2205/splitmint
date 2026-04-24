from django.urls import path
from . import views

urlpatterns = [
    path('group/<int:group_pk>/add/', views.add_expense, name='add_expense'),
    path('group/<int:group_pk>/list/', views.expense_list, name='expense_list'),
    path('<int:pk>/edit/', views.edit_expense, name='edit_expense'),
    path('<int:pk>/delete/', views.delete_expense, name='delete_expense'),
    path('settle/<int:split_id>/', views.settle_split, name='settle_split'),
    path('dashboard/', views.dashboard, name='expense_dashboard'),
]
