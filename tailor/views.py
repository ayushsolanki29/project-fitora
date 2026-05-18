from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta, date
import random
import calendar
from decimal import Decimal

# Import correct models - USE THE CORRECT NAMES
from .models import (
    Tailor, 
    TailorCustomer, 
    TailorOrder,      # Changed from Order
    TailorPayment,    # Changed from Payment
    TailorMeasurement  # Changed from MeasurementRecord
)
from .forms import (
    TailorRegistrationForm, 
    TailorProfileForm, 
    TailorShopDetailsForm,
    TailorCustomerForm, 
    TailorMeasurementForm, 
    TailorOrderForm, 
    TailorPaymentForm
)


# ==================== AUTHENTICATION VIEWS ====================

def register(request):
    if request.method == "POST":
        form = TailorRegistrationForm(request.POST)
        if form.is_valid():
            tailor = form.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('tailor:login')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = TailorRegistrationForm()
    
    return render(request, 'tailor/register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            tailor = Tailor.objects.get(email=email)
            if check_password(password, tailor.password):
                # Generate OTP
                otp = random.randint(100000, 999999)
                request.session['login_otp'] = str(otp)
                request.session['temp_tailor_id'] = tailor.id
                
                # Send OTP via email
                send_mail(
                    'Login OTP - Tailor Panel',
                    f'Your OTP for login is: {otp}\n\nThis OTP is valid for 10 minutes.',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, f"OTP sent to {email}")
                return redirect('tailor:verifyotp')
            else:
                messages.error(request, "Invalid password")
        except Tailor.DoesNotExist:
            messages.error(request, "Email not found")
    
    return render(request, 'tailor/login.html')


def verifyotp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        
        if otp == request.session.get('login_otp'):
            tailor_id = request.session.get('temp_tailor_id')
            tailor = Tailor.objects.get(id=tailor_id)
            
            # Set session
            request.session['tailor_id'] = tailor.id
            request.session['tailor_name'] = tailor.username
            request.session['tailor_email'] = tailor.email
            
            # Clear temp data
            request.session.pop('login_otp', None)
            request.session.pop('temp_tailor_id', None)
            
            messages.success(request, f"Welcome back, {tailor.username}!")
            return redirect('tailor:tailor_dashboard')
        else:
            messages.error(request, "Invalid OTP")
    
    return render(request, 'tailor/verifyotp.html')


def forget_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        
        try:
            tailor = Tailor.objects.get(email=email)
            otp = random.randint(100000, 999999)
            
            request.session['reset_email'] = email
            request.session['reset_otp'] = str(otp)
            
            send_mail(
                'Password Reset OTP - Tailor Panel',
                f'Your OTP for password reset is: {otp}\n\nThis OTP is valid for 10 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, "OTP sent to your email")
            return redirect('tailor:verifyreset')
        except Tailor.DoesNotExist:
            messages.error(request, "Email not found")
    
    return render(request, 'tailor/forget_password.html')


def verifyreset(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        
        if otp == request.session.get('reset_otp'):
            return redirect('tailor:new_password')
        else:
            messages.error(request, "Invalid OTP")
    
    return render(request, 'tailor/verifyreset.html')


def new_password(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'tailor/new_password.html')
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return render(request, 'tailor/new_password.html')
        
        email = request.session.get('reset_email')
        
        try:
            tailor = Tailor.objects.get(email=email)
            tailor.password = make_password(password)
            tailor.save()
            
            request.session.flush()
            messages.success(request, "Password changed successfully! Please login.")
            return redirect('tailor:login')
        except Tailor.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('tailor:forget_password')
    
    return render(request, 'tailor/new_password.html')


def logout_view(request):
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect('tailor:login')


# ==================== DASHBOARD ====================

def tailor_dashboard(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor_id = request.session.get('tailor_id')
    tailor = Tailor.objects.get(id=tailor_id)
    
    # Stats - USE TailorOrder instead of Order
    total_orders = TailorOrder.objects.filter(tailor=tailor).count()
    pending_orders = TailorOrder.objects.filter(tailor=tailor, status='Pending').count()
    completed_orders = TailorOrder.objects.filter(tailor=tailor, status='Delivered').count()
    total_earnings = TailorPayment.objects.filter(tailor=tailor, status='Success').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Recent orders
    recent_orders = TailorOrder.objects.filter(tailor=tailor).order_by('-created_at')[:5]
    
    # Chart data for last 6 months
    chart_labels = []
    chart_data = []
    for i in range(5, -1, -1):
        month_date = timezone.now() - timedelta(days=30*i)
        count = TailorOrder.objects.filter(
            tailor=tailor,
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()
        chart_labels.append(month_date.strftime('%b'))
        chart_data.append(count)
    
    context = {
        'tailor': tailor,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_earnings': total_earnings,
        'recent_orders': recent_orders,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'tailor/dashboard.html', context)


# ==================== PROFILE MANAGEMENT ====================

def view_profile(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    
    # Stats for profile
    total_orders = TailorOrder.objects.filter(tailor=tailor).count()
    completed_orders = TailorOrder.objects.filter(tailor=tailor, status='Delivered').count()
    pending_orders = TailorOrder.objects.filter(tailor=tailor, status='Pending').count()
    
    context = {
        'tailor': tailor,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
    }
    return render(request, 'tailor/Profile Management/view_profile.html', context)


def edit_profile(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    
    if request.method == "POST":
        form = TailorProfileForm(request.POST, request.FILES, instance=tailor)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('tailor:view_profile')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = TailorProfileForm(instance=tailor)
    
    context = {'form': form, 'tailor': tailor}
    return render(request, 'tailor/Profile Management/edit_profile.html', context)


def shop_details(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    
    if request.method == "POST":
        form = TailorShopDetailsForm(request.POST, instance=tailor)
        if form.is_valid():
            form.save()
            messages.success(request, "Shop details updated successfully!")
            return redirect('tailor:view_profile')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = TailorShopDetailsForm(instance=tailor)
    
    context = {'form': form, 'tailor': tailor}
    return render(request, 'tailor/Profile Management/shop_details.html', context)


def change_password(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not check_password(old_password, tailor.password):
            messages.error(request, "Current password is incorrect")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match")
        elif len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters")
        else:
            tailor.password = make_password(new_password)
            tailor.save()
            messages.success(request, "Password changed successfully!")
            return redirect('tailor:view_profile')
    
    return render(request, 'tailor/Profile Management/change_password.html')


# ==================== CUSTOMER MANAGEMENT ====================

def view_customers(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    customers = TailorCustomer.objects.filter(tailor=tailor).order_by('-created_at')
    
    # Add order count for each customer
    for customer in customers:
        customer.order_count = customer.orders.count()
        last_order = customer.orders.order_by('-created_at').first()
        customer.last_order_date = last_order.created_at if last_order else None
    
    context = {'customers': customers}
    return render(request, 'tailor/Customer Management/view_customers.html', context)


def add_new_customer(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    
    if request.method == "POST":
        form = TailorCustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.tailor = tailor
            customer.save()
            messages.success(request, f"Customer {customer.get_full_name()} added successfully!")
            return redirect('tailor:view_customers')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = TailorCustomerForm()
    
    context = {'form': form}
    return render(request, 'tailor/Customer Management/add_new_customer.html', context)


def customer_measurement_records(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    customer_id = request.GET.get('id')
    
    if not customer_id:
        messages.error(request, "Customer ID required")
        return redirect('tailor:view_customers')
    
    customer = get_object_or_404(TailorCustomer, id=customer_id, tailor=tailor)
    measurements = TailorMeasurement.objects.filter(customer=customer, tailor=tailor).order_by('-measurement_date').first()
    
    if request.method == "POST":
        form = TailorMeasurementForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.customer = customer
            record.tailor = tailor
            record.save()
            
            # Update customer measurements JSON
            customer.customer_measurements = record.get_all_measurements() if hasattr(record, 'get_all_measurements') else {}
            customer.save()
            
            messages.success(request, "Measurements saved successfully!")
            return redirect(f'/tailor/customer-measurement-records/?id={customer_id}')
    else:
        form = TailorMeasurementForm()
    
    context = {
        'customer': customer,
        'measurements': measurements,
        'form': form,
    }
    return render(request, 'tailor/Customer Management/customer_measurement_records.html', context)


def customer_order_history(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    customer_id = request.GET.get('id')
    
    if not customer_id:
        messages.error(request, "Customer ID required")
        return redirect('tailor:view_customers')
    
    customer = get_object_or_404(TailorCustomer, id=customer_id, tailor=tailor)
    orders = TailorOrder.objects.filter(customer=customer, tailor=tailor).order_by('-created_at')
    
    total_revenue = orders.aggregate(Sum('amount'))['amount__sum'] or 0
    pending_count = orders.filter(status='Pending').count()
    
    context = {
        'customer': customer,
        'customer_orders': orders,
        'total_revenue': total_revenue,
        'pending_count': pending_count,
    }
    return render(request, 'tailor/Customer Management/customer_order_history.html', context)


# ==================== ORDER MANAGEMENT ====================

def create_new_orders(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    customers = TailorCustomer.objects.filter(tailor=tailor)
    
    if request.method == "POST":
        form = TailorOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.tailor = tailor
            order.save()
            messages.success(request, f"Order #{order.order_number} created successfully!")
            return redirect('tailor:view_all_orders')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = TailorOrderForm()
        form.fields['customer'].queryset = customers
    
    context = {'form': form, 'customers': customers}
    return render(request, 'tailor/Order Management/create_new_orders.html', context)


def view_all_orders(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    orders_list = TailorOrder.objects.filter(tailor=tailor).order_by('-created_at')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        orders_list = orders_list.filter(
            Q(order_number__icontains=search) |
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search)
        )
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders_list = orders_list.filter(status=status_filter)
    
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'tailor/Order Management/view_all_orders.html', context)


def order_detail(request, order_id):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    order = get_object_or_404(TailorOrder, id=order_id, tailor=tailor)
    payments = TailorPayment.objects.filter(order=order)
    
    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in dict(TailorOrder.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to {new_status}")
            return redirect('tailor:order_detail', order_id=order_id)
    
    context = {'order': order, 'payments': payments}
    return render(request, 'tailor/Order Management/order_detail.html', context)


def pending_orders(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    orders = TailorOrder.objects.filter(tailor=tailor, status='Pending').order_by('delivery_date')
    
    context = {'orders': orders}
    return render(request, 'tailor/Order Management/pending_orders.html', context)


def delivered_orders(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    orders = TailorOrder.objects.filter(tailor=tailor, status='Delivered').order_by('-updated_at')
    
    context = {'orders': orders, 'is_delivered': True}
    return render(request, 'tailor/Order Management/delivered_orders.html', context)


def cancelled_orders(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    orders = TailorOrder.objects.filter(tailor=tailor, status='Cancelled').order_by('-updated_at')
    
    context = {'orders': orders}
    return render(request, 'tailor/Order Management/cancelled_orders.html', context)


# ==================== PAYMENT MANAGEMENT ====================

def add_payments(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    active_orders = TailorOrder.objects.filter(tailor=tailor).exclude(status='Delivered').exclude(status='Cancelled')
    
    if request.method == "POST":
        form = TailorPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.tailor = tailor
            payment.customer = payment.order.customer
            payment.status = 'Success'
            payment.save()
            
            # Update order advance payment
            order = payment.order
            order.advance_paid += payment.amount
            order.balance_due = order.amount - order.advance_paid
            order.save()
            
            # Update tailor earnings
            tailor.total_earnings += payment.amount
            tailor.save()
            
            messages.success(request, f"Payment of ₹{payment.amount} recorded successfully!")
            return redirect('tailor:payment_history')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = TailorPaymentForm()
        form.fields['order'].queryset = active_orders
    
    context = {'form': form, 'active_orders': active_orders}
    return render(request, 'tailor/Payment Management/add_payments.html', context)


def view_payments(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    payments = TailorPayment.objects.filter(tailor=tailor).order_by('-created_at')
    
    context = {'payments': payments}
    return render(request, 'tailor/Payment Management/view_payments.html', context)


def pending_payments(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    orders_with_balance = TailorOrder.objects.filter(
        tailor=tailor,
        balance_due__gt=0
    ).exclude(status='Cancelled')
    
    total_pending = orders_with_balance.aggregate(Sum('balance_due'))['balance_due__sum'] or 0
    overdue_amount = orders_with_balance.filter(delivery_date__lt=date.today()).aggregate(Sum('balance_due'))['balance_due__sum'] or 0
    
    context = {
        'payments': orders_with_balance,
        'total_pending': total_pending,
        'overdue_amount': overdue_amount,
        'today': date.today(),
    }
    return render(request, 'tailor/Payment Management/pending_payments.html', context)


def payment_history(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    payments = TailorPayment.objects.filter(tailor=tailor, status='Success').order_by('-created_at')
    
    # Filter by date range
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if start_date:
        payments = payments.filter(created_at__date__gte=start_date)
    if end_date:
        payments = payments.filter(created_at__date__lte=end_date)
    
    total_earnings = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    today_earnings = payments.filter(created_at__date=date.today()).aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'payments': payments,
        'total_earnings': total_earnings,
        'today_earnings': today_earnings,
    }
    return render(request, 'tailor/Payment Management/payment_history.html', context)


def generate_receipt(request, payment_id):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    payment = get_object_or_404(TailorPayment, id=payment_id, tailor=tailor)
    
    context = {'payment': payment, 'tailor': tailor}
    return render(request, 'tailor/Payment Management/generate_receipt.html', context)


# ==================== DELIVERY SCHEDULE ====================

def delivery_calender(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    
    # Get current month and year
    now = timezone.now()
    current_month = int(request.GET.get('month', now.month))
    current_year = int(request.GET.get('year', now.year))
    
    # Get calendar days
    cal = calendar.monthcalendar(current_year, current_month)
    
    # Get orders for this month
    orders_in_month = TailorOrder.objects.filter(
        tailor=tailor,
        delivery_date__year=current_year,
        delivery_date__month=current_month
    )
    
    # Prepare calendar data
    calendar_days = []
    for week in cal:
        week_days = []
        for day in week:
            if day == 0:
                week_days.append({'date': None, 'orders': []})
            else:
                order_date = date(current_year, current_month, day)
                day_orders = orders_in_month.filter(delivery_date=order_date)
                week_days.append({
                    'date': day,
                    'orders': day_orders,
                    'is_today': order_date == date.today()
                })
        calendar_days.append(week_days)
    
    context = {
        'calendar_days': calendar_days,
        'current_month': current_month,
        'current_year': current_year,
        'month_name': calendar.month_name[current_month],
        'prev_month': current_month - 1 if current_month > 1 else 12,
        'prev_year': current_year if current_month > 1 else current_year - 1,
        'next_month': current_month + 1 if current_month < 12 else 1,
        'next_year': current_year if current_month < 12 else current_year + 1,
    }
    return render(request, 'tailor/Delivery Schedule/delivery_calender.html', context)


def upcoming_deliveries(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    upcoming_orders = TailorOrder.objects.filter(
        tailor=tailor,
        delivery_date__gte=date.today(),
        status__in=['Pending', 'In Progress', 'Cutting', 'Stitching']
    ).order_by('delivery_date')
    
    for order in upcoming_orders:
        order.completion_pct = order.completion_pct if hasattr(order, 'completion_pct') else 0
    
    context = {'upcoming_orders': upcoming_orders}
    return render(request, 'tailor/Delivery Schedule/upcoming_deliveries.html', context)


# ==================== REPORTS ====================

def monthly_reports(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    
    # Current month stats
    current_month = date.today().month
    current_year = date.today().year
    
    monthly_orders = TailorOrder.objects.filter(
        tailor=tailor,
        created_at__year=current_year,
        created_at__month=current_month
    )
    
    monthly_stats = {
        'total_orders': monthly_orders.count(),
        'completed_orders': monthly_orders.filter(status='Delivered').count(),
        'pending_orders': monthly_orders.filter(status='Pending').count(),
        'total_revenue': TailorPayment.objects.filter(
            tailor=tailor,
            created_at__year=current_year,
            created_at__month=current_month,
            status='Success'
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    
    # Weekly breakdown
    weekly_breakdown = []
    today = date.today()
    for i in range(4):
        week_start = today - timedelta(days=today.weekday() + 7*i)
        week_end = week_start + timedelta(days=6)
        week_orders = TailorOrder.objects.filter(
            tailor=tailor,
            delivery_date__range=[week_start, week_end]
        )
        weekly_breakdown.append({
            'number': 4 - i,
            'total': week_orders.count(),
            'on_time': week_orders.filter(delivery_date__gte=date.today()).count() if i == 0 else week_orders.count(),
        })
    
    context = {
        'monthly_stats': monthly_stats,
        'weekly_breakdown': weekly_breakdown,
    }
    return render(request, 'tailor/Reports/monthly_reports.html', context)


def income_reports(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    
    # Income stats
    total_earnings = TailorPayment.objects.filter(tailor=tailor, status='Success').aggregate(Sum('amount'))['amount__sum'] or 0
    this_month_earnings = TailorPayment.objects.filter(
        tailor=tailor,
        created_at__year=date.today().year,
        created_at__month=date.today().month,
        status='Success'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    pending_balance = TailorOrder.objects.filter(tailor=tailor).exclude(status='Cancelled').aggregate(Sum('balance_due'))['balance_due__sum'] or 0
    
    # Recent payments
    recent_payments = TailorPayment.objects.filter(tailor=tailor, status='Success').order_by('-created_at')[:10]
    
    context = {
        'income_stats': {
            'total_earnings': total_earnings,
            'this_month': this_month_earnings,
            'pending_balance': pending_balance,
        },
        'recent_payments': recent_payments,
    }
    return render(request, 'tailor/Reports/income_reports.html', context)


def customer_reports(request):
    if not request.session.get('tailor_id'):
        return redirect('tailor:login')
    
    tailor = Tailor.objects.get(id=request.session['tailor_id'])
    
    # Customer loyalty data
    customers = TailorCustomer.objects.filter(tailor=tailor)
    client_reports = []
    
    for customer in customers:
        orders = TailorOrder.objects.filter(customer=customer)
        client_reports.append({
            'id': customer.id,
            'name': customer.get_full_name(),
            'profile_pic': customer.profile_pic,
            'joined': customer.created_at,
            'order_count': orders.count(),
            'total_revenue': orders.aggregate(Sum('amount'))['amount__sum'] or 0,
            'last_order': orders.order_by('-created_at').first().created_at if orders.exists() else None,
        })
    
    # Sort by total revenue
    client_reports.sort(key=lambda x: x['total_revenue'], reverse=True)
    
    context = {'client_reports': client_reports}
    return render(request, 'tailor/Reports/customer_reports.html', context)