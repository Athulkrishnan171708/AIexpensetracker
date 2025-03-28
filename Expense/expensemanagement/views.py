from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate,logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from expensemanagement.models import Income, Expense, Registration
import logging
import json
from django.http import JsonResponse
from django.db.models import Sum
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .models import Registration
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
import numpy as np
from django.contrib import messages
from .models import Group, GroupExpense, Registration
from sklearn.ensemble import IsolationForest
from datetime import datetime
from django.core.mail import EmailMessage
from django.conf import settings
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import xlsxwriter
from sklearn.preprocessing import RobustScaler
import random

# Configure logging
logger = logging.getLogger(__name__)

def welcome(request):
    return render(request,'welcome.html')

import random
from django.core.mail import send_mail
from django.http import JsonResponse

def send_otp_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP

        subject = "Your OTP Code"
        message = f"Hello,\n\nYour OTP code is: {otp}\n\nUse this code to complete your registration."
        sender_email = "athulkrishnan716@gmail.com"  # Must match `EMAIL_HOST_USER` in settings.py

        try:
            send_mail(subject, message, sender_email, [email])
            request.session["otp"] = otp  # Store OTP in session
            return JsonResponse({"success": "OTP sent successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")

        if entered_otp == stored_otp:
            request.session["otp_verified"] = True  # Mark OTP as verified in session
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Invalid OTP"})

@login_required(login_url='login')
def home(request):
    last_30_days = datetime.now() - timedelta(days=30)

    # Fetch and sum all incomes and expenses in the last 30 days
    total_income = Income.objects.filter(user=request.user, date__gte=last_30_days).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=request.user, date__gte=last_30_days).aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate balance
    balance = total_income - total_expense  

    # Fetch income transactions
    income_history = list(Income.objects.filter(user=request.user,date__gte=last_30_days).values('date', 'amount', 'category'))
    for income in income_history:
        income['type'] = 'Income'  # Mark as Income

    # Fetch expense transactions
    expense_history = list(Expense.objects.filter(user=request.user,date__gte=last_30_days).values('date', 'amount', 'category'))
    for expense in expense_history:
        expense['type'] = 'Expense'  # Mark as Expense

    # Merge transactions and sort by date
    transactions = income_history + expense_history
    transactions.sort(key=lambda x: x['date'], reverse=True)

    return render(request, 'home.html', {
        'transactions': transactions,  # Pass transactions with type
        'monthly_income': total_income,  
        'monthly_expense': total_expense,  
        'balance': balance  
    })


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        dob_str = request.POST.get('dob')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate all fields
        if not (name and phone and email and dob_str and password and confirm_password):
            return JsonResponse({"success": False, "error": "All fields are required."})

        # Validate password match
        if password != confirm_password:
            return JsonResponse({"success": False, "error": "Passwords do not match."})
        
        if not request.session.get("otp_verified"):
            return JsonResponse({"success": False, "error": "OTP verification is required."})

        # Validate unique email
        if Registration.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "error": "An account with this email already exists."})

        # Convert Date of Birth
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"success": False, "error": "Invalid date format."})

        # Create user
        user = Registration.objects.create_user(
            username=email,
            email=email,
            first_name=name,
            phone=phone,
            dob=dob
        )
        user.set_password(password)  # Hash password
        user.save()

        return JsonResponse({"success": True, "redirect_url": "/login"})  # Redirect to login page

    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)  # Log the user in
            return JsonResponse({"success": True, "redirect_url": "/home"})  # Redirect to home

        return JsonResponse({"success": False, "error": "Invalid email or password."})

    return render(request, 'login.html')


@login_required(login_url='login')
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required(login_url='login')
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.phone = request.POST.get('phone')
        user.dob = request.POST.get('dob')
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('home')

    return render(request, 'profile.html', {'user': user})

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Keep user logged in
            messages.success(request, "Password changed successfully!")
            return redirect('home')
        else:
            messages.error(request, "Old password is incorrect.")
            return redirect('profile')

    return render(request, 'profile.html')


def user_logout(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        if not group_name:
            messages.error(request, "Group name is required.")
            return redirect('create_group')

        group = Group.objects.create(name=group_name, created_by=request.user)
        group.members.add(request.user)  # Add the creator as a member
        messages.success(request, f"Group '{group_name}' created successfully!")
        return redirect('view_group', group_id=group.id)

    return render(request, 'create_group.html')

@login_required(login_url='login')
def view_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user not in group.members.all():
        messages.error(request, "You are not a member of this group.")
        return redirect('home')

    if request.method == 'POST':
        member_email = request.POST.get('member_email')
        if not member_email:
            messages.error(request, "Member email is required.")
            return redirect('view_group', group_id=group.id)

        try:
            new_member = Registration.objects.get(email=member_email)
            if new_member in group.members.all(): 
                messages.warning(request, "User is already a member of this group.")
            else:
                group.members.add(new_member) 
                messages.success(request, f"{new_member.email} added to the group.")
        except Registration.DoesNotExist:
            messages.error(request, "User with this email does not exist.")

    return render(request, 'view_group.html', {'group': group})

@login_required(login_url='login')
def add_group_expense(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user not in group.members.all():
        messages.error(request, "You are not a member of this group.")
        return redirect('home')

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        if not amount or not description:
            messages.error(request, "Amount and description are required.")
            return redirect('add_group_expense', group_id=group.id)

        expense = GroupExpense.objects.create(
            group=group,
            amount=amount,
            description=description,
            paid_by=request.user
        )
        
        expense.split_among.set(group.members.all())  
        messages.success(request, "Expense added successfully!")
        return redirect('view_group', group_id=group.id)

    return render(request, 'add_group_expense.html', {'group': group})

@login_required(login_url='login')
def manage_group_expenses(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user not in group.members.all():
        messages.error(request, "You are not a member of this group.")
        return redirect('groups')

    return render(request, 'manage_group_expenses.html', {'group': group})

@login_required(login_url='login')
def edit_group_expense(request, expense_id):
    expense = get_object_or_404(GroupExpense, id=expense_id)

    if request.user not in expense.group.members.all():
        messages.error(request, "You are not authorized to edit this expense.")
        return redirect('manage_group_expenses', group_id=expense.group.id)

    if request.method == 'POST':
        expense.amount = request.POST.get('amount')
        expense.description = request.POST.get('description')
        expense.save()
        messages.success(request, "Expense updated successfully.")
        return redirect('manage_group_expenses', group_id=expense.group.id)

    return render(request, 'edit_group_expense.html', {'expense': expense})

@login_required(login_url='login')
def delete_group_expense(request, expense_id):
    expense = get_object_or_404(GroupExpense, id=expense_id)

    if request.user not in expense.group.members.all():
        messages.error(request, "You are not authorized to delete this expense.")
        return redirect('manage_group_expenses', group_id=expense.group.id)

    group_id = expense.group.id
    expense.delete()
    messages.success(request, "Expense deleted successfully.")
    return redirect('manage_group_expenses', group_id=group_id)

@login_required(login_url='login')
def split_group_expense(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user not in group.members.all():
        messages.error(request, "You are not authorized to split expenses in this group.")
        return redirect('groups')

    total_expense = sum(exp.amount for exp in group.expenses.all())
    num_members = group.members.count()
    share_per_member = total_expense / num_members if num_members > 0 else 0

    return render(request, 'split_group_expense.html', {
        'group': group,
        'total_expense': total_expense,
        'share_per_member': share_per_member,
    })

@login_required(login_url='login')
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user != group.created_by:
        messages.error(request, "Only the group creator can delete the group.")
        return redirect('manage_group_expenses', group_id=group.id)

    group.delete()
    messages.success(request, "Group deleted successfully.")
    return redirect('groups')

@login_required(login_url='login')
def groups(request):
    user_groups = Group.objects.filter(members=request.user)
    return render(request, 'groups.html', {'groups': user_groups})


@login_required(login_url='login')
def income(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')
        category = request.POST.get('category')

        if not amount or not date or not category:
            messages.error(request, "Please fill in all required fields.")
            return redirect('income')

        try:
            Income.objects.create(
                user=request.user,
                amount=amount,
                date=date,
                description=description,
                category=category
            )
            messages.success(request, "Income record added successfully!")
        except Exception as e:
            logger.error(f"Error adding income: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('display_income')

    return render(request, 'income.html')

def edit_income(request, income_id):
    income = get_object_or_404(Income, id=income_id)
    if request.method == 'POST':
        income.amount = request.POST.get('amount')
        income.date = request.POST.get('date')
        income.description = request.POST.get('description')
        income.category = request.POST.get('category')
        income.save()
        messages.success(request, "Income record updated successfully!")
        return redirect('display_income')

    return render(request, 'edit_income.html', {'income': income})

def delete_income(request, income_id):
    try:
        income = get_object_or_404(Income, id=income_id)
        income.delete()
        messages.success(request, "Income record deleted successfully!")
    except Exception as e:
        logger.error(f"Error deleting income record with ID {income_id}: {str(e)}")
        messages.error(request, "An error occurred while trying to delete the income record.")
    return redirect('display_income')

@login_required(login_url='login')
def expense(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')
        category = request.POST.get('category')

        if not amount or not date or not category:
            messages.error(request, "Please fill in all required fields.")
            return redirect('expense')

        try:
            Expense.objects.create(
                user=request.user,  # ✅ Assign the logged-in user
                amount=amount,
                date=date,
                description=description,
                category=category
            )
            messages.success(request, "Expense record added successfully!")
        except Exception as e:
            logger.error(f"Error adding expense: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('display_expenses')

    return render(request, 'expense.html')


@login_required(login_url='login')
def display_income(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    return render(request, 'display_income.html', {'income_records': incomes})

@login_required(login_url='login')
def display_expenses(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'display_expenses.html', {'expenses': expenses})


def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    if request.method == 'POST':
        expense.amount = request.POST.get('amount')
        expense.date = request.POST.get('date')
        expense.description = request.POST.get('description')
        expense.category = request.POST.get('category')
        expense.save()
        messages.success(request, "Expense record updated successfully!")
        return redirect('display_expenses')

    return render(request, 'edit_expense.html', {'expense': expense})


def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    messages.success(request, "Expense record deleted successfully!")
    return redirect('display_expenses')

@login_required(login_url='login')
def charts(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    incomes = Income.objects.filter(user=request.user)

    if start_date and end_date:
        incomes = incomes.filter(date__range=[start_date, end_date])  # Apply filter here

    income_data = incomes.values('category').annotate(total_amount=Sum('amount'))  # Use filtered data
    income_data_json = json.dumps(list(income_data), default=str)

    return render(request, 'charts.html', {
        'income_data': income_data_json,
        'start_date': start_date if start_date else "",
        'end_date': end_date if end_date else ""
    })

@login_required(login_url='login')
def excharts(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    expenses = Expense.objects.filter(user=request.user)

    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])  # Apply filter here

    expense_data = expenses.values('category').annotate(total_amount=Sum('amount'))  # Use filtered data
    expense_data_json = json.dumps(list(expense_data), default=str)

    return render(request, 'excharts.html', {
        'expense_data': expense_data_json,
        'start_date': start_date if start_date else "",
        'end_date': end_date if end_date else ""
    })


def export_report(request):
    if request.method == 'POST':
        # Get form data
        report_type = request.POST.get('report_type')
        date_range = request.POST.get('date_range')
        export_format = request.POST.get('export_format')
        recipient_email = request.POST.get('recipient_email')
        
        # Calculate date range
        end_date = datetime.now()
        if date_range == '7days':
            start_date = end_date - timedelta(days=7)
        elif date_range == '30days':
            start_date = end_date - timedelta(days=30)
        elif date_range == '90days':
            start_date = end_date - timedelta(days=90)
        elif date_range == 'custom':
            start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')
        else:
            start_date = end_date - timedelta(days=30)  # Default to 30 days
        
        # Generate report data based on type
        report_data = generate_report_data(request.user, report_type, start_date, end_date)
        
        # Generate the file based on format
        if export_format == 'pdf':
            file_data, filename = generate_pdf_report(report_data, report_type, start_date, end_date)
            content_type = 'application/pdf'
        else:  # excel
            file_data, filename = generate_excel_report(report_data, report_type, start_date, end_date)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        # Send email with attachment
        success = send_report_email(recipient_email, file_data, filename, content_type, report_type)
        
        if success:
            messages.success(request, f"Report has been sent to {recipient_email}")
        else:
            messages.error(request, "Failed to send report. Please try again later.")
        
        return redirect('profile')
    
    return redirect('profile')

from .models import Expense, Income, Registration  # Import necessary models

def generate_report_data(user, report_type, start_date, end_date):
    data = {
        'headers': [],
        'rows': []
    }
    
    if report_type == 'financial':
        # Retrieve financial transactions from Expense and Income tables
        data['headers'] = ['Date', 'Transaction Type', 'Category', 'Amount']
        data['title'] = 'Financial Transactions Report'
        
        expenses = Expense.objects.filter(user=user, date__range=[start_date, end_date])
        incomes = Income.objects.filter(user=user, date__range=[start_date, end_date])
        
        transactions = [
            [exp.date, 'Expense', exp.category, f'-${exp.amount:.2f}'] for exp in expenses
        ] + [
            [inc.date, 'Income', inc.category , f'+${inc.amount:.2f}'] for inc in incomes
        ]
        
        # Sort transactions by date
        data['rows'] = sorted(transactions, key=lambda x: x[0], reverse=True)
    
    elif report_type == 'user_data':
        # Retrieve user details from Registration table
        data['headers'] = ['Field', 'Value']
        data['title'] = 'User Data Report'
        
        registration = Registration.objects.get(email=user.email)
        
        age = (datetime.today().date() - registration.dob).days // 365 if registration.dob else 'N/A'
        
        data['rows'] = [
            ['Full Name', f"{registration.first_name} {registration.last_name if registration.last_name else ''}".strip()],
            ['Email', registration.email],
            ['Phone', registration.phone],
            ['Date of Birth', registration.dob],
            ['Age', age],
            ['Date Joined', registration.date_joined],
        ]
    
    data['report_type'] = report_type
    data['start_date'] = start_date
    data['end_date'] = end_date
    data['user'] = user
    
    return data


def generate_pdf_report(data, report_type, start_date, end_date):
    """Generate a PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Add styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    
    # Add title
    elements.append(Paragraph(data['title'], title_style))
    
    # Add date range
    date_range_text = f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
    elements.append(Paragraph(date_range_text, subtitle_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph(f"User: {data['user'].username} ({data['user'].email})", styles['Normal']))
    elements.append(Paragraph(" ", styles['Normal']))  # Add some space
    
    # Create table
    table_data = [data['headers']]  # Add headers
    for row in data['rows']:
        formatted_row = []
        for cell in row:
            if isinstance(cell, datetime):
                formatted_row.append(cell.strftime('%Y-%m-%d %H:%M'))
            else:
                formatted_row.append(str(cell))
        table_data.append(formatted_row)
    
    # Create the table
    table = Table(table_data)
    
    # Add style to table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ])
    table.setStyle(style)
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Create filename
    filename = f"{report_type}_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
    
    return pdf_data, filename

def generate_excel_report(data, report_type, start_date, end_date):
    """Generate an Excel report"""
    buffer = io.BytesIO()
    
    # Create workbook
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet(report_type.capitalize() + ' Report')
    
    # Add formats
    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1
    })
    
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm', 'border': 1})
    cell_format = workbook.add_format({'border': 1})
    
    # Add title
    worksheet.merge_range('A1:D1', data['title'], workbook.add_format({
        'bold': True,
        'font_size': 16,
        'align': 'center'
    }))
    
    # Add date range
    date_range_text = f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
    worksheet.merge_range('A2:D2', date_range_text, workbook.add_format({'align': 'center'}))
    
    # Add generated info
    generation_info = f"Generated on: {datetime.now().strftime('%B %d, %Y %H:%M')}"
    worksheet.merge_range('A3:D3', generation_info, workbook.add_format({'align': 'center'}))
    
    user_info = f"User: {data['user'].username} ({data['user'].email})"
    worksheet.merge_range('A4:D4', user_info, workbook.add_format({'align': 'center'}))
    
    # Add headers
    for col, header in enumerate(data['headers']):
        worksheet.write(5, col, header, header_format)
    
    # Add data
    for row_idx, row_data in enumerate(data['rows']):
        for col_idx, cell_data in enumerate(row_data):
            if isinstance(cell_data, datetime):
                worksheet.write_datetime(row_idx + 6, col_idx, cell_data, date_format)
            else:
                worksheet.write(row_idx + 6, col_idx, cell_data, cell_format)
    
    # Auto-fit columns
    for i, _ in enumerate(data['headers']):
        worksheet.set_column(i, i, 20)
    
    workbook.close()
    
    excel_data = buffer.getvalue()
    buffer.close()
    
    # Create filename
    filename = f"{report_type}_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"
    
    return excel_data, filename

def send_report_email(recipient_email, file_data, filename, content_type, report_type):
    """Send the report via email"""
    try:
        # Create email
        subject = f"{report_type.capitalize()} Report"
        message = "Please find attached your requested report."
        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email]
        )
        
        # Attach file
        email.attach(filename, file_data, content_type)
        
        # Send email
        email.send()
        return True
    except Exception as e:
        # Log the error
        print(f"Error sending email: {str(e)}")
        return False


# List of important events
events = {
    "January": ["New Year's Day", "Makar Sankranti / Pongal", "Republic Day"],
    "March": ["Holi"],
    "April": ["Ram Navami", "Mahavir Jayanti", "Tamil New Year / Vishu", "Good Friday"],
    "May": ["Labour Day", "Buddha Purnima"],
    "June": ["Eid-ul-Fitr"],
    "August": ["Independence Day", "Raksha Bandhan", "Janmashtami"],
    "October": ["Gandhi Jayanti", "Dussehra", "Diwali"],
    "December": ["Christmas"]
}

def get_upcoming_events():
    """Returns the list of upcoming events for next month."""
    today = datetime.today()
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    return events.get(next_month.strftime("%B"), [])

def fetch_data(user):
    """Fetch expenses and incomes from both database and Excel files."""
    # **Fetch from database**
    db_expenses = Expense.objects.filter(user=user).values('date', 'amount', 'category')
    db_incomes = Income.objects.filter(user=user).values('date', 'amount')

    df_db_expenses = pd.DataFrame(db_expenses)
    df_db_incomes = pd.DataFrame(db_incomes)

    # **Fetch from Excel**
    try:
        df_excel_expenses = pd.read_excel('D:\\project\\expenses.xlsx')
    except Exception:
        df_excel_expenses = pd.DataFrame()

    try:
        df_excel_incomes = pd.read_excel('D:\\project\\incomes.xlsx')
    except Exception:
        df_excel_incomes = pd.DataFrame()

    # **Combine database and Excel data**
    df_expenses = pd.concat([df_db_expenses, df_excel_expenses], ignore_index=True)
    df_incomes = pd.concat([df_db_incomes, df_excel_incomes], ignore_index=True)

    return df_expenses, df_incomes

def preprocess_data(df, is_income=False):
    """Preprocess expenses or income for analysis."""
    if df.empty:
        return df

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['amount'] = df['amount'].astype(float)
    df['month'] = df['date'].dt.to_period('M').dt.to_timestamp()

    return df

def detect_anomalies(expenses, incomes, essential_categories):
    """Detect anomalies in expenses considering incomes."""
    expenses = preprocess_data(expenses)
    incomes = preprocess_data(incomes, is_income=True)

    if expenses.empty or incomes.empty:
        return [], None

    # Consider only the last 60 days of transactions
    cutoff_date = datetime.today() - timedelta(days=60)
    recent_expenses = expenses[expenses['date'] >= cutoff_date]

    if recent_expenses.empty or len(recent_expenses) < 10:
        return [], None

    # Exclude essential expenses
    non_essential = recent_expenses[~recent_expenses['category'].isin(essential_categories)].copy()

    if non_essential.empty:
        return [], None

    # Calculate monthly income
    monthly_income = incomes.groupby('month')['amount'].sum()
    non_essential['income'] = non_essential['date'].apply(lambda x: monthly_income.get(x.to_period('M').to_timestamp(), 0))
    
    # Calculate expense-to-income ratio
    non_essential['expense_ratio'] = np.where(non_essential['income'] > 0, 
                                              non_essential['amount'] / non_essential['income'], 
                                              non_essential['amount'])

    # Focus on high-value transactions
    expense_75th_percentile = np.percentile(non_essential['expense_ratio'], 75)  # Based on ratio
    high_value_expenses = non_essential[non_essential['expense_ratio'] > expense_75th_percentile]

    if high_value_expenses.empty:
        return [], None

    # Apply IsolationForest for anomaly detection
    scaler = RobustScaler()
    high_value_expenses['scaled_ratio'] = scaler.fit_transform(high_value_expenses[['expense_ratio']])

    contamination_rate = max(0.02, min(0.07, 5 / len(high_value_expenses)))

    iso_model = IsolationForest(contamination=contamination_rate, random_state=42)
    high_value_expenses['anomaly'] = iso_model.fit_predict(high_value_expenses[['scaled_ratio']])

    anomalies = high_value_expenses[high_value_expenses['anomaly'] == -1]

    if anomalies.empty:
        return [], None

    # Identify the most unusual transaction
    most_unwanted_expense = anomalies.loc[anomalies['expense_ratio'].idxmax()].to_dict()

    return anomalies[['date', 'amount', 'category']].to_dict(orient='records'), most_unwanted_expense

def predict_next_month_expense(expense_data, income_data, essential_categories):
    """Predict next month's expenses based on past trends and incomes."""
    expense_data = preprocess_data(expense_data)
    income_data = preprocess_data(income_data, is_income=True)

    if expense_data.empty or income_data.empty:
        return 0, False

    # Aggregate monthly totals
    monthly_expense = expense_data.groupby('month')['amount'].sum()
    essential_expense = expense_data[expense_data['category'].isin(essential_categories)].groupby('month')['amount'].sum()
    non_essential_expense = expense_data[~expense_data['category'].isin(essential_categories)].groupby('month')['amount'].sum()
    avg_monthly_income = income_data.groupby('month')['amount'].sum().mean()

    avg_essential = essential_expense.mean() if not essential_expense.empty else 0

    # Forecast non-essential expenses
    if non_essential_expense.empty or len(non_essential_expense) < 2:
        forecast_non_essential = non_essential_expense.sum() if not non_essential_expense.empty else 0
    else:
        ts = non_essential_expense.sort_index()
        t = np.arange(len(ts)).reshape(-1, 1)
        model = LinearRegression()
        model.fit(t, ts.values)
        forecast_non_essential = model.predict([[len(ts)]])[0]

    forecast = avg_essential + forecast_non_essential

    # Event adjustment
    event_adjust = len(get_upcoming_events()) * 0.01 * avg_monthly_income
    forecast += event_adjust

    budget_exceeded = forecast > avg_monthly_income
    return forecast, budget_exceeded

@login_required(login_url='login')
def predict_expenses(request):
    """View to predict next month's expenses and detect anomalies."""
    user = request.user

    # Fetch data from database + Excel
    df_expenses, df_income = fetch_data(user)

    if df_income.empty:
        messages.error(request, "No income data available.")
        return render(request, 'predictive_analysis.html', {})

    essential_categories = ['groceries', 'rent', 'utilities', 'health']

    # Detect anomalies
    anomalies, most_unwanted_expense = detect_anomalies(df_expenses, df_income, essential_categories)

    # Category breakdown
    category_breakdown = df_expenses.groupby('category')['amount'].sum().to_dict() if not df_expenses.empty else {}

    # Predict next month's expense
    predicted_expense, budget_exceeded = predict_next_month_expense(df_expenses, df_income, essential_categories)

    # Build recommendations
    recommendations = []
    if budget_exceeded:
        recommendations.append("Your predicted spending exceeds your income. Consider adjusting expenses.")
    if anomalies:
        recommendations.append("Unusual spending detected. Review transactions to manage unnecessary expenses.")
    if most_unwanted_expense:
        recommendations.append(f"You spent ₹{most_unwanted_expense['amount']} on {most_unwanted_expense['category']}. Consider reducing this expense.")

    return render(request, 'predictive_analysis.html', {
        "predictions": predicted_expense,
        "anomalies": anomalies,
        "exceeding_budget": budget_exceeded,
        "category_breakdown": category_breakdown,
        "recommendations": recommendations,
        "upcoming_events": get_upcoming_events()
    })
