from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import random
import json
from .models import AdminProfile, AdminTailor, AdminCustomer, AdminOrder, AdminPayment, AdminTransactionRecord
from .forms import (
    AdminTailorForm, 
    AdminCustomerForm, 
    AdminOrderForm, 
    AdminPaymentForm, 
    AdminProfileForm, 
    AdminUserUpdateForm
)
# Helper function to check if user is admin
def is_admin(user):
    return user.is_authenticated and user.is_staff

# ==================== AUTHENTICATION VIEWS ====================

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('adminsite:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('adminsite:register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True
        )
        
        # Create admin profile
        AdminProfile.objects.create(user=user)

        messages.success(request, "Registration Successful! Please login.")
        return redirect('adminsite:login')

    return render(request, 'adminsite/register.html')


def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, "Login Successful!")
            return redirect('adminsite:adminsite_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an admin")

    return render(request, 'adminsite/login_page.html')


def logout_user(request):
    logout(request)
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect('adminsite:login')


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)

            request.session['reset_email'] = email
            request.session['reset_otp'] = str(otp)

            send_mail(
                'Password Reset OTP - Admin Panel',
                f'Your OTP for password reset is: {otp}\n\nThis OTP is valid for 10 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, "OTP sent to your email")
            return redirect('adminsite:verify_reset')

        except User.DoesNotExist:
            messages.error(request, "Email not found")

    return render(request, 'adminsite/forgot_password.html')


def verify_reset(request):
    if request.method == "POST":
        otp = request.POST.get('otp')

        if otp == request.session.get('reset_otp'):
            return redirect('adminsite:new_password')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'adminsite/verify_reset.html')


def new_password(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'adminsite/new_password.html')

        email = request.session.get('reset_email')

        try:
            user = User.objects.get(email=email)
            user.password = make_password(password)
            user.save()

            request.session.flush()
            messages.success(request, "Password changed successfully! Please login.")
            return redirect('adminsite:login')

        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('adminsite:forgot_password')

    return render(request, 'adminsite/new_password.html')


# ==================== DASHBOARD ====================

@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def adminsite_dashboard(request):
    total_orders = AdminOrder.objects.count()
    total_customers = AdminCustomer.objects.count()
    total_tailors = AdminTailor.objects.filter(is_active=True).count()
    total_revenue = AdminPayment.objects.filter(status='Success').aggregate(Sum('amount'))['amount__sum'] or 0
    
    recent_orders = AdminOrder.objects.all().order_by('-created_at')[:5]
    
    # Order status counts
    pending_orders = AdminOrder.objects.filter(status='Pending').count()
    completed_orders = AdminOrder.objects.filter(status='Completed').count()
    cancelled_orders = AdminOrder.objects.filter(status='Cancelled').count()
    
    context = {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_tailors': total_tailors,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
    }
    return render(request, 'adminsite/dashboard.html', context)


# ==================== TAILOR MANAGEMENT ====================

@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def view_all_tailors(request):
    tailors_list = AdminTailor.objects.all().order_by('-created_at')
    
    search = request.GET.get('search', '')
    if search:
        tailors_list = tailors_list.filter(
            Q(name__icontains=search) | 
            Q(email__icontains=search) |
            Q(specialty__icontains=search)
        )
    
    paginator = Paginator(tailors_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'adminsite/TailorManagement/view_all_tailors.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def add_new_tailor(request):
    if request.method == "POST":
        form = AdminTailorForm(request.POST, request.FILES)
        if form.is_valid():
            tailor = form.save()
            from .sync import sync_admin_tailor_to_portal
            sync_admin_tailor_to_portal(tailor)
            messages.success(request, f"Tailor {tailor.name} added successfully!")
            return redirect('adminsite:view_all_tailors')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = AdminTailorForm()
    
    return render(request, 'adminsite/TailorManagement/add_new_tailor.html', {'form': form})


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def edit_tailor(request, tailor_id):
    tailor = get_object_or_404(AdminTailor, id=tailor_id)
    
    if request.method == "POST":
        form = AdminTailorForm(request.POST, request.FILES, instance=tailor)
        if form.is_valid():
            form.save()
            from .sync import sync_admin_tailor_to_portal
            sync_admin_tailor_to_portal(tailor)
            messages.success(request, f"Tailor {tailor.name} updated successfully!")
            return redirect('adminsite:view_all_tailors')
    else:
        form = AdminTailorForm(instance=tailor)
    
    return render(request, 'adminsite/TailorManagement/edit_tailor.html', {'form': form, 'tailor': tailor})


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def delete_tailor(request, tailor_id):
    tailor = get_object_or_404(AdminTailor, id=tailor_id)
    tailor_name = tailor.name
    tailor.delete()
    messages.success(request, f"Tailor {tailor_name} deleted successfully!")
    return redirect('adminsite:view_all_tailors')


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def toggle_tailor_status(request, tailor_id):
    tailor = get_object_or_404(AdminTailor, id=tailor_id)
    tailor.is_active = not tailor.is_active
    tailor.save()
    from .sync import sync_admin_tailor_to_portal
    sync_admin_tailor_to_portal(tailor)
    status = "activated" if tailor.is_active else "deactivated"
    messages.success(request, f"Tailor {tailor.name} {status}!")
    return redirect('adminsite:view_all_tailors')


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def tailor_performance(request):
    tailors = AdminTailor.objects.filter(is_active=True)
    
    # Calculate performance metrics
    for tailor in tailors:
        tailor.completed_orders = AdminOrder.objects.filter(tailor=tailor, status='Completed').count()
        tailor.total_earnings = AdminPayment.objects.filter(
            order__tailor=tailor, 
            status='Success'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calculate average rating from completed orders
        ratings = AdminOrder.objects.filter(tailor=tailor, status='Completed', rating__gt=0).values_list('rating', flat=True)
        if ratings:
            tailor.avg_rating = sum(ratings) / len(ratings)
        else:
            tailor.avg_rating = 0
        
        tailor.efficiency = tailor.efficiency
    
    # Find top performer
    top_performer = tailors.order_by('-completed_orders').first() if tailors.exists() else None
    
    # Monthly data for chart
    last_6_months = []
    for i in range(5, -1, -1):
        month = timezone.now() - timedelta(days=30*i)
        count = AdminOrder.objects.filter(
            tailor__in=tailors,
            created_at__year=month.year,
            created_at__month=month.month
        ).count()
        last_6_months.append({'month': month, 'count': count})
    
    context = {
        'tailors': tailors,
        'top_performer': top_performer,
        'monthly_data': last_6_months,
    }
    return render(request, 'adminsite/TailorManagement/tailor_performance.html', context)


# ==================== CUSTOMERMANAGEMENT ====================

@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def view_all_customers(request):
    customers_list = AdminCustomer.objects.all().order_by('-created_at')
    
    search = request.GET.get('search', '')
    if search:
        customers_list = customers_list.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Calculate total spent for each customer
    for customer in customers_list:
        customer.total_spent = AdminPayment.objects.filter(
            customer=customer, 
            status='Success'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    paginator = Paginator(customers_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'adminsite/CustomerManagement/view_all_customers.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def customer_details(request, customer_id):
    customer = get_object_or_404(AdminCustomer, id=customer_id)
    
    # Calculate total spent
    customer.total_spent = AdminPayment.objects.filter(
        customer=customer, 
        status='Success'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {'customer': customer}
    return render(request, 'adminsite/CustomerManagement/customer_details.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def customer_order_history(request, customer_id):
    customer = get_object_or_404(AdminCustomer, id=customer_id)
    orders = AdminOrder.objects.filter(customer=customer).order_by('-created_at')
    
    context = {
        'customer': customer,
        'orders': orders,
    }
    return render(request, 'adminsite/CustomerManagement/customer_order_history.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def toggle_customer_status(request, customer_id):
    customer = get_object_or_404(AdminCustomer, id=customer_id)
    customer.is_active = not customer.is_active
    customer.save()
    
    # Also update user active status
    customer.user.is_active = customer.is_active
    customer.user.save()
    
    status = "activated" if customer.is_active else "blocked"
    messages.success(request, f"Customer {customer.get_full_name()} {status}!")
    return redirect('adminsite:view_all_customers')


# ==================== ORDERMANAGEMENT ====================

@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def view_all_orders(request):
    orders_list = AdminOrder.objects.all().order_by('-created_at')
    
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        orders_list = orders_list.filter(
            Q(order_number__icontains=search) |
            Q(customer__user__first_name__icontains=search) |
            Q(customer__user__last_name__icontains=search) |
            Q(tailor__name__icontains=search)
        )
    
    if status_filter:
        orders_list = orders_list.filter(status=status_filter)
    
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'adminsite/OrderManagement/view_all_orders.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def order_details(request, order_id):
    order = get_object_or_404(AdminOrder, id=order_id)
    payments = AdminPayment.objects.filter(order=order)
    
    context = {
        'order': order,
        'payments': payments,
    }
    return render(request, 'adminsite/OrderManagement/order_details.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def pending_orders(request):
    orders = AdminOrder.objects.filter(status='Pending').order_by('created_at')
    
    for order in orders:
        order.pending_duration = order.pending_duration
    
    context = {'orders': orders}
    return render(request, 'adminsite/OrderManagement/pending_orders.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def completed_orders(request):
    orders = AdminOrder.objects.filter(status='Completed').order_by('-updated_at')
    context = {'orders': orders}
    return render(request, 'adminsite/OrderManagement/completed_orders.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def cancelled_orders(request):
    orders = AdminOrder.objects.filter(status='Cancelled').order_by('-updated_at')
    context = {'orders': orders}
    return render(request, 'adminsite/OrderManagement/cancelled_orders.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def approve_order(request, order_id):
    order = get_object_or_404(AdminOrder, id=order_id)
    order.status = 'Approved'
    order.save()
    messages.success(request, f"Order #{order.order_number} approved!")
    return redirect('adminsite:pending_orders')


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def assign_tailor(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(AdminOrder, id=order_id)
        tailor_id = request.POST.get('tailor_id')
        order.tailor_id = tailor_id
        order.status = 'In Progress'
        order.save()
        messages.success(request, f"Tailor assigned to order #{order.order_number}!")
        return redirect('adminsite:pending_orders')
    
    order = get_object_or_404(AdminOrder, id=order_id)
    tailors = AdminTailor.objects.filter(is_active=True)
    context = {'order': order, 'tailors': tailors}
    return render(request, 'adminsite/OrderManagement/assign_tailor.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def update_order_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(AdminOrder, id=order_id)
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f"Order #{order.order_number} status updated to {new_status}!")
        return redirect('adminsite:view_all_orders')
    
    order = get_object_or_404(AdminOrder, id=order_id)
    context = {'order': order}
    return render(request, 'adminsite/OrderManagement/update_order_status.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def cancel_order(request, order_id):
    order = get_object_or_404(AdminOrder, id=order_id)
    if request.method == "POST":
        reason = request.POST.get('reason', '')
        order.status = 'Cancelled'
        order.cancellation_reason = reason
        order.save()
        
        # Update related payment
        AdminPayment.objects.filter(order=order, status='Pending').update(status='Failed')
        
        messages.success(request, f"Order #{order.order_number} cancelled!")
        return redirect('adminsite:view_all_orders')
    
    context = {'order': order}
    return render(request, 'adminsite/OrderManagement/cancel_order.html', context)


# ==================== PAYMENT MANAGEMENT ====================

@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def all_payments(request):
    payments = AdminPayment.objects.all().order_by('-created_at')
    
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        payments = payments.filter(
            Q(transaction_ref__icontains=search) |
            Q(customer__user__email__icontains=search) |
            Q(order__order_number__icontains=search)
        )
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    total_revenue = payments.filter(status='Success').aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'payments': payments,
        'total_revenue': total_revenue,
    }
    return render(request, 'adminsite/Payment Management/all_payments.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def pending_payments(request):
    pending_payments = AdminPayment.objects.filter(status='Pending').order_by('created_at')
    
    context = {'pending_payments': pending_payments}
    return render(request, 'adminsite/Payment Management/pending_payments.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def verify_payment(request, payment_id):
    payment = get_object_or_404(AdminPayment, id=payment_id)
    payment.status = 'Success'
    payment.save()
    
    # Create transaction record
    AdminTransactionRecord.objects.create(
        payment=payment,
        gateway_id=f"GATEWAY_{payment.transaction_ref}",
        gateway_fee=payment.amount * 0.02,  # 2% fee
        net_amount=payment.amount * 0.98,
        is_verified=True
    )
    
    messages.success(request, f"Payment {payment.transaction_ref} verified!")
    return redirect('adminsite:pending_payments')


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def decline_payment(request, payment_id):
    payment = get_object_or_404(AdminPayment, id=payment_id)
    payment.status = 'Failed'
    payment.save()
    messages.warning(request, f"Payment {payment.transaction_ref} declined!")
    return redirect('adminsite:pending_payments')


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def transaction_records(request):
    transactions = AdminTransactionRecord.objects.all().order_by('-processed_date')
    
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        transactions = transactions.filter(
            Q(gateway_id__icontains=search) |
            Q(payment__transaction_ref__icontains=search)
        )
    
    if status_filter == 'verified':
        transactions = transactions.filter(is_verified=True)
    elif status_filter == 'unverified':
        transactions = transactions.filter(is_verified=False)
    
    context = {'transactions': transactions}
    return render(request, 'adminsite/Payment Management/transaction_records.html', context)


# ==================== REPORTS ====================

@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def order_reports(request):
    total_orders = AdminOrder.objects.count()
    completed_count = AdminOrder.objects.filter(status='Completed').count()
    pending_count = AdminOrder.objects.filter(status='Pending').count()
    cancelled_count = AdminOrder.objects.filter(status='Cancelled').count()
    
    success_rate = (completed_count / total_orders * 100) if total_orders > 0 else 0
    
    # Calculate average completion time (in days)
    completed_orders = AdminOrder.objects.filter(status='Completed', updated_at__isnull=False)
    avg_days = 0
    if completed_orders.exists():
        total_days = sum((order.updated_at - order.created_at).days for order in completed_orders)
        avg_days = total_days / completed_orders.count()
    
    context = {
        'total_orders': total_orders,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'cancelled_count': cancelled_count,
        'success_rate': round(success_rate, 1),
        'avg_completion_time': round(avg_days, 1),
    }
    return render(request, 'adminsite/Reports/order_reports.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def payment_reports(request):
    total_revenue = AdminPayment.objects.filter(status='Success').aggregate(Sum('amount'))['amount__sum'] or 0
    total_refunds = AdminPayment.objects.filter(status='Refunded').aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = total_revenue - total_refunds
    
    # Monthly payment data for last 6 months
    payment_data = []
    for i in range(5, -1, -1):
        month_date = timezone.now() - timedelta(days=30*i)
        payments = AdminPayment.objects.filter(
            status='Success',
            created_at__year=month_date.year,
            created_at__month=month_date.month
        )
        gross = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        fees = gross * 0.02
        payment_data.append({
            'date': month_date.strftime('%b %Y'),
            'count': payments.count(),
            'gross': gross,
            'fees': fees,
            'net': gross - fees,
        })
    
    context = {
        'total_revenue': total_revenue,
        'total_refunds': total_refunds,
        'net_profit': net_profit,
        'payment_data': payment_data,
    }
    return render(request, 'adminsite/Reports/payment_reports.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def tailor_reports(request):
    tailors = AdminTailor.objects.filter(is_active=True)
    
    tailor_stats = []
    for tailor in tailors:
        completed = AdminOrder.objects.filter(tailor=tailor, status='Completed').count()
        revenue = AdminPayment.objects.filter(order__tailor=tailor, status='Success').aggregate(Sum('amount'))['amount__sum'] or 0
        ratings = AdminOrder.objects.filter(tailor=tailor, rating__gt=0).values_list('rating', flat=True)
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        tailor_stats.append({
            'tailor': tailor,
            'completed_orders': completed,
            'revenue': revenue,
            'avg_rating': round(avg_rating, 1),
        })
    
    context = {'tailor_stats': tailor_stats}
    return render(request, 'adminsite/Reports/tailor_reports.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def monthly_reports(request):
    # Calculate growth percentages
    current_month = timezone.now().month
    current_year = timezone.now().year
    last_month = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year if current_month > 1 else current_year - 1
    
    current_customers = AdminCustomer.objects.filter(created_at__year=current_year, created_at__month=current_month).count()
    last_customers = AdminCustomer.objects.filter(created_at__year=last_month_year, created_at__month=last_month).count()
    customer_growth = ((current_customers - last_customers) / max(1, last_customers)) * 100 if last_customers > 0 else 0
    
    current_revenue = AdminPayment.objects.filter(status='Success', created_at__year=current_year, created_at__month=current_month).aggregate(Sum('amount'))['amount__sum'] or 0
    last_revenue = AdminPayment.objects.filter(status='Success', created_at__year=last_month_year, created_at__month=last_month).aggregate(Sum('amount'))['amount__sum'] or 0
    revenue_growth = ((current_revenue - last_revenue) / max(1, last_revenue)) * 100 if last_revenue > 0 else 0
    
    # Return rate (customers who ordered more than once)
    repeat_customers = AdminCustomer.objects.annotate(order_count=Count('orders')).filter(order_count__gt=1).count()
    total_customers_with_orders = AdminCustomer.objects.filter(orders__isnull=False).distinct().count()
    return_rate = (repeat_customers / max(1, total_customers_with_orders)) * 100
    
    context = {
        'customer_growth': round(customer_growth, 1),
        'revenue_growth': round(revenue_growth, 1),
        'return_rate': round(return_rate, 1),
    }
    return render(request, 'adminsite/Reports/monthly_reports.html', context)


# ==================== ADMIN PROFILE ====================

@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def view_profile(request):
    admin_profile, created = AdminProfile.objects.get_or_create(user=request.user)
    
    total_orders = AdminOrder.objects.count()
    total_customers = AdminCustomer.objects.count()
    total_tailors = AdminTailor.objects.filter(is_active=True).count()
    
    context = {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_tailors': total_tailors,
    }
    return render(request, 'adminsite/Admin Profile/view_profile.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def update_details(request):
    admin_profile, created = AdminProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        user_form = AdminUserUpdateForm(request.POST, instance=request.user)
        profile_form = AdminProfileForm(request.POST, request.FILES, instance=admin_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('adminsite:view_profile')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        user_form = AdminUserUpdateForm(instance=request.user)
        profile_form = AdminProfileForm(instance=admin_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'adminsite/Admin Profile/update_details.html', context)


@login_required(login_url='adminsite:login')
@user_passes_test(is_admin)
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not check_password(old_password, request.user.password):
            messages.error(request, "Current password is incorrect")
        elif new_password != confirm_password:
            messages.error(request, "New passwords do not match")
        elif len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters")
        else:
            request.user.password = make_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password changed successfully!")
            return redirect('adminsite:view_profile')
    
    return render(request, 'adminsite/Admin Profile/change_password.html')