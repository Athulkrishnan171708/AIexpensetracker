"""URL configuration for Expense project."""

from django.urls import path
from . import views
from .views import (
    manage_group_expenses, edit_group_expense, delete_group_expense, 
    split_group_expense, delete_group
)
urlpatterns = [
    path('', views.welcome,name='welcome'), 
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('charts/', views.charts, name='charts'),
    path('excharts/', views.excharts, name='excharts'),
    path('prediction/', views.predict_expenses, name='predict_expenses'),
    path('expense/', views.expense, name='expense'),  # URL for adding an expense
    path('income/', views.income, name='income'),
    path('income/edit/<int:income_id>/', views.edit_income, name='edit_income'),
    path('income/delete/<int:income_id>/', views.delete_income, name='delete_income'),
    path('display_expenses/', views.display_expenses, name='display_expenses'),  # URL for displaying expenses
    path('display_income/', views.display_income, name='display_income'),
    path('expenses/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('export-report/', views.export_report, name='export_report'),
    path('create_group/', views.create_group, name='create_group'),
    path('group/<int:group_id>/', views.view_group, name='view_group'),
    path('group/<int:group_id>/add_expense/', views.add_group_expense, name='add_group_expense'),
    path('group/<int:group_id>/expenses/', manage_group_expenses, name='manage_group_expenses'),
    path('group/expense/<int:expense_id>/edit/', edit_group_expense, name='edit_group_expense'),
    path('group/expense/<int:expense_id>/delete/', delete_group_expense, name='delete_group_expense'),
    path('group/<int:group_id>/split/', split_group_expense, name='split_group_expense'),
    path('group/<int:group_id>/delete/', delete_group, name='delete_group'),
    path('groups/', views.groups, name='groups'),
    path("send-otp/", views.send_otp_email, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
]
