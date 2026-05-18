from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta, date
import random

from .models import Customer, CustomerAddress, CustomerOrder, CustomerPayment
from .forms import CustomerRegistrationForm, CustomerProfileForm, CustomerAddressForm


# ==================== AUTHENTICATION ====================

def Register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.password = make_password(form.cleaned_data['password'])
            customer.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('customer:login')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'customer/Register.html', {'form': form})


def login(request):
    if request.method == "POST":
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Customer.objects.get(email=email)

            if check_password(password, user.password):
                otp = random.randint(100000, 999999)
                request.session['login_otp'] = str(otp)
                request.session['temp_user'] = user.id

                send_mail(
                    'Login OTP - Fitora',
                    f'Your OTP for login is: {otp}\n\nThis OTP is valid for 10 minutes.',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, f"OTP sent to {email}")
                return redirect('customer:verifyotp')
            else:
                messages.error(request, 'Invalid password')
        except Customer.DoesNotExist:
            messages.error(request, 'User not found')

    return render(request, 'customer/login.html')


def verifyotp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')

        if otp == request.session.get('login_otp'):
            user_id = request.session.get('temp_user')
            user = Customer.objects.get(id=user_id)
            
            request.session['customer_id'] = user_id
            request.session['customer_name'] = user.username
            
            request.session.pop('login_otp', None)
            request.session.pop('temp_user', None)
            
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('customer:customer_dashboard')
        else:
            messages.error(request, 'Invalid OTP')

    return render(request, 'customer/verifyotp.html')


def forget_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = Customer.objects.get(email=email)
            otp = random.randint(100000, 999999)
            
            request.session['reset_email'] = email
            request.session['reset_otp'] = str(otp)
            
            send_mail(
                'Password Reset OTP - Fitora',
                f'Your OTP for password reset is: {otp}\n\nThis OTP is valid for 10 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, "OTP sent to your email")
            return redirect('customer:verifyreset')
        except Customer.DoesNotExist:
            messages.error(request, 'Email not found')

    return render(request, 'customer/forget_password.html')


def verifyreset(request):
    if request.method == "POST":
        otp = request.POST.get('otp')

        if otp == request.session.get('reset_otp'):
            return redirect('customer:new_password')
        else:
            messages.error(request, 'Invalid OTP')

    return render(request, 'customer/verifyreset.html')


def new__password(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'customer/new_password.html')
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return render(request, 'customer/new_password.html')

        email = request.session.get('reset_email')

        try:
            user = Customer.objects.get(email=email)
            user.password = make_password(password)
            user.save()
            
            request.session.flush()
            messages.success(request, "Password changed successfully! Please login.")
            return redirect('customer:login')
        except Customer.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('customer:forget_password')

    return render(request, 'customer/new_password.html')


def logout_user(request):
    request.session.flush()
    messages.success(request, "Logged out successfully")
    return redirect('customer:login')


# ==================== DASHBOARD ====================

def customer_dashboard(request):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    
    total_orders = CustomerOrder.objects.filter(customer=customer).count()
    pending_orders = CustomerOrder.objects.filter(customer=customer, status='Pending').count()
    completed_orders = CustomerOrder.objects.filter(customer=customer, status='Delivered').count()
    total_spent = CustomerPayment.objects.filter(customer=customer, status='Success').aggregate(Sum('amount'))['amount__sum'] or 0
    
    recent_orders = CustomerOrder.objects.filter(customer=customer).order_by('-created_at')[:5]
    
    # Chart data
    chart_labels = []
    chart_data = []
    for i in range(5, -1, -1):
        month_date = timezone.now() - timedelta(days=30*i)
        count = CustomerOrder.objects.filter(
            customer=customer,
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()
        chart_labels.append(month_date.strftime('%b'))
        chart_data.append(count)
    
    context = {
        'customer': customer,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'customer/dashboard.html', context)


# ==================== PROFILE MANAGEMENT ====================

def view_profile(request):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    
    total_orders = CustomerOrder.objects.filter(customer=customer).count()
    total_spent = CustomerPayment.objects.filter(customer=customer, status='Success').aggregate(Sum('amount'))['amount__sum'] or 0
    completed_orders = CustomerOrder.objects.filter(customer=customer, status='Delivered').count()
    
    context = {
        'customer': customer,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'completed_orders': completed_orders,
    }
    return render(request, 'customer/My Profile/view_profile.html', context)


def edit_personal_details(request):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    
    if request.method == "POST":
        form = CustomerProfileForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('customer:view_profile')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = CustomerProfileForm(instance=customer)
    
    context = {'form': form, 'customer': customer}
    return render(request, 'customer/My Profile/edit_personal_details.html', context)


from .models import Customer

def change_password(request):

    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('customer:login')

    customer = Customer.objects.get(id=customer_id)

    context = {
        'customer': customer
    }

    return render(
        request,
        'customer/My Profile/change_password.html',
        context
    )
def address_information(request):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    address = CustomerAddress.objects.filter(customer=customer, is_default=True).first()
    
    context = {'address': address}
    return render(request, 'customer/My Profile/address_information.html', context)


def add_address(request):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    address = CustomerAddress.objects.filter(customer=customer, is_default=True).first()
    
    if request.method == "POST":
        form = CustomerAddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.customer = customer
            if addr.is_default:
                CustomerAddress.objects.filter(customer=customer).update(is_default=False)
            addr.save()
            messages.success(request, "Address saved successfully!")
            return redirect('customer:address_information')
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = CustomerAddressForm(instance=address)
    
    context = {'form': form, 'address': address}
    return render(request, 'customer/My Profile/add_address.html', context)


# ==================== ORDER MANAGEMENT ====================

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

def view_all_orders(request):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    orders = CustomerOrder.objects.filter(customer=customer).order_by('-id')

    paginator = Paginator(orders, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='Pending').count(),
        'completed_orders': orders.filter(status='Completed').count(),
    }

    return render(
        request,
        'customer/Orders/view_all_orders.html',
        context
    )
def order_details(request, order_id):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    order = get_object_or_404(CustomerOrder, id=order_id, customer=customer)
    
    context = {'order': order}
    return render(request, 'customer/My Orders/order_details.html', context)


def order_status_tracking(request, order_id):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    order = get_object_or_404(CustomerOrder, id=order_id, customer=customer)
    
    context = {'order': order}
    return render(request, 'customer/My Orders/order_status_tracking.html', context)


def delivery_date_information(request, order_id):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    order = get_object_or_404(CustomerOrder, id=order_id, customer=customer)
    
    context = {'order': order}
    return render(request, 'customer/My Orders/delivery_date_information.html', context)


def live_order_status(request, order_id):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    order = get_object_or_404(CustomerOrder, id=order_id, customer=customer)
    
    context = {'order': order}
    return render(request, 'customer/Track Order/live_order_status.html', context)


# ==================== PAYMENT MANAGEMENT ====================

def make_payment(request):
    if not request.session.get('customer_id'):
        return redirect('customer:login')

    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    unpaid_orders = CustomerOrder.objects.filter(customer=customer).exclude(payment_status='Paid')

    if request.method == 'POST':
        from decimal import Decimal, InvalidOperation
        from django.conf import settings
        from .stripe_payments import create_stripe_checkout

        order_id = request.POST.get('order_id')
        amount_raw = request.POST.get('amount')
        payment_method = request.POST.get('method', 'Card')
        action = request.POST.get('action', 'stripe')

        order = get_object_or_404(CustomerOrder, id=order_id, customer=customer)

        try:
            pay_amount = Decimal(amount_raw) if amount_raw else order.balance_due
        except (InvalidOperation, TypeError):
            pay_amount = order.balance_due or order.amount

        if pay_amount <= 0:
            messages.error(request, 'Invalid payment amount.')
            return redirect('customer:make_payment')

        # Stripe Checkout (card payments)
        if action == 'stripe' and settings.STRIPE_SECRET_KEY:
            checkout_url = create_stripe_checkout(request, order.id, pay_amount)
            if checkout_url:
                return redirect(checkout_url)
            return redirect('customer:make_payment')

        # Cash / manual payment at shop
        if action == 'cash' or payment_method == 'Cash':
            payment = CustomerPayment.objects.create(
                customer=customer,
                order=order,
                amount=pay_amount,
                payment_method='Cash',
                status='Success',
            )
            order.advance_paid += payment.amount
            order.balance_due = max(Decimal('0'), order.amount - order.advance_paid)
            if order.balance_due <= 0:
                order.payment_status = 'Paid'
            order.save()
            messages.success(request, f'Cash payment of ₹{payment.amount} recorded!')
            return redirect('customer:payment_history')

        messages.error(request, 'Please use Stripe for online payments.')
        return redirect('customer:make_payment')

    from django.conf import settings
    context = {
        'unpaid_orders': unpaid_orders,
        'stripe_enabled': bool(settings.STRIPE_SECRET_KEY),
    }
    return render(request, 'customer/Payments/make_payment.html', context)


def stripe_success(request):
    from .stripe_payments import handle_stripe_success
    return handle_stripe_success(request)


def stripe_cancel(request):
    from .stripe_payments import handle_stripe_cancel
    return handle_stripe_cancel(request)


def payment_history(request):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    payments_list = CustomerPayment.objects.filter(customer=customer).order_by('-created_at')
    
    # Filters
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    if search:
        payments_list = payments_list.filter(order__order_number__icontains=search)
    if status_filter:
        payments_list = payments_list.filter(status=status_filter)
    if date_filter:
        payments_list = payments_list.filter(created_at__date=date_filter)
    
    paginator = Paginator(payments_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'customer/Payments/payment_history.html', context)


def download_receipt(request, payment_id):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    payment = get_object_or_404(CustomerPayment, id=payment_id, customer=customer)
    
    context = {'payment': payment, 'customer': customer}
    return render(request, 'customer/Payments/download_receipt.html', context)


def previous_orders(request):
    if not request.session.get('customer_id'):
        return redirect('customer:login')
    
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    orders_list = CustomerOrder.objects.filter(
        customer=customer
    ).exclude(status='Pending').order_by('-created_at')
    
    # Filters
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    if search:
        orders_list = orders_list.filter(order_number__icontains=search)
    if status_filter:
        orders_list = orders_list.filter(status=status_filter)
    if date_filter:
        orders_list = orders_list.filter(created_at__date=date_filter)
    
    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'customer/Order History/previous_orders.html', context)