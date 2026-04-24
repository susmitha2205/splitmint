from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('create/', views.create_group, name='create_group'),
    path('<int:pk>/', views.group_detail, name='group_detail'),
    path('<int:pk>/edit/', views.edit_group, name='edit_group'),
    path('<int:pk>/delete/', views.delete_group, name='delete_group'),
]
