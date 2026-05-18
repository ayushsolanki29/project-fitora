from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.views.decorators.http import require_http_methods

from tailor.models import Tailor, TailorOrder
from customer.models import Customer, CustomerOrder
from .utils import (
    estimate_order_amount,
    get_tailor_display_name,
    sync_customer_order_to_tailor,
)


def index(request):
    context = {
        'title': 'FITORA - Smart Tailoring Management System',
        'tailor_count': Tailor.objects.filter(is_active=True).count(),
    }
    return render(request, 'website/index.html', context)


def about(request):
    return render(request, 'website/about.html', {'title': 'About FITORA'})


def how_it_works(request):
    return render(request, 'website/how-it-works.html', {'title': 'How FITORA Works'})


def services(request):
    return render(request, 'website/services.html', {'title': 'Our Services'})


def book_tailor(request):
    """Tailor booking page — requires customer login."""
    tailors_list = Tailor.objects.filter(is_active=True, is_verified=True).order_by('shop_name', 'username')
    if not tailors_list.exists():
        tailors_list = Tailor.objects.filter(is_active=True).order_by('shop_name', 'username')

    preselect_tailor = request.GET.get('tailor') or request.POST.get('tailor')

    if request.method == 'POST':
        if not request.session.get('customer_id'):
            request.session['next_after_login'] = request.get_full_path()
            messages.info(request, 'Please log in to book a tailor.')
            return redirect('website:login')

        tailor_id = request.POST.get('tailor')
        garment_type = request.POST.get('garment_type', '').strip()
        description = request.POST.get('description', '').strip()
        delivery_date = request.POST.get('delivery_date')
        amount_raw = request.POST.get('amount')

        if not tailor_id or not garment_type or not delivery_date:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('website:book_tailor')

        try:
            customer = Customer.objects.get(id=request.session['customer_id'])
            tailor = Tailor.objects.get(id=tailor_id, is_active=True)
            amount = Decimal(amount_raw) if amount_raw else estimate_order_amount(garment_type)

            order = CustomerOrder.objects.create(
                customer=customer,
                tailor_id=tailor.id,
                tailor_name=get_tailor_display_name(tailor),
                garment_type=garment_type,
                description=description,
                delivery_date=delivery_date,
                amount=amount,
                balance_due=amount,
                status='Pending',
                payment_status='Pending',
            )

            sync_customer_order_to_tailor(order, tailor)

            request.session['last_order_id'] = order.id
            messages.success(
                request,
                f'Order #{order.order_number} created! Pay ₹{amount} from your dashboard.',
            )
            return redirect('customer:make_payment')
        except Tailor.DoesNotExist:
            messages.error(request, 'Selected tailor is not available.')
        except Exception as e:
            messages.error(request, f'Error creating order: {e}')

    context = {
        'title': 'Book a Tailor',
        'tailors': tailors_list,
        'preselect_tailor': preselect_tailor,
        'is_logged_in': bool(request.session.get('customer_id')),
    }
    return render(request, 'website/book_tailor.html', context)


def tailors(request):
    """Dynamic tailor listing with search and filters."""
    tailors_qs = Tailor.objects.filter(is_active=True).order_by('-is_verified', 'shop_name', 'username')

    search = request.GET.get('q', '').strip()
    specialty = request.GET.get('specialty', '').strip()
    city = request.GET.get('city', '').strip()

    if search:
        tailors_qs = tailors_qs.filter(
            Q(shop_name__icontains=search)
            | Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(specialty__icontains=search)
            | Q(city__icontains=search)
        )
    if specialty:
        tailors_qs = tailors_qs.filter(specialty__icontains=specialty)
    if city:
        tailors_qs = tailors_qs.filter(city__icontains=city)

    specialties = Tailor.SPECIALTY_CHOICES
    cities = (
        Tailor.objects.filter(is_active=True, city__isnull=False)
        .exclude(city='')
        .values_list('city', flat=True)
        .distinct()
    )

    context = {
        'title': 'Our Tailors',
        'tailors': tailors_qs,
        'search': search,
        'selected_specialty': specialty,
        'selected_city': city,
        'specialties': specialties,
        'cities': cities,
        'tailor_count': tailors_qs.count(),
    }
    return render(request, 'website/tailors.html', context)


def pricing(request):
    from .utils import GARMENT_BASE_PRICES
    context = {
        'title': 'Pricing Plans',
        'prices': GARMENT_BASE_PRICES,
    }
    return render(request, 'website/princing.html', context)


def track_order(request):
    return render(request, 'website/track-order.html', {'title': 'Track Your Order'})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not message:
            messages.error(request, 'Please fill in all fields.')
        else:
            try:
                send_mail(
                    f'Contact Form: {name}',
                    f'From: {name} ({email})\n\nMessage: {message}',
                    settings.EMAIL_HOST_USER,
                    [getattr(settings, 'CONTACT_EMAIL', 'support@fitora.com')],
                    fail_silently=True,
                )
                messages.success(request, 'Your message has been sent successfully!')
            except Exception:
                messages.success(request, 'Thank you! We received your message and will reply soon.')
        return redirect('website:contact')

    return render(request, 'website/contact.html', {'title': 'Contact Us'})


def login_page(request):
    if request.session.get('customer_id'):
        return redirect('customer:customer_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        try:
            customer = Customer.objects.get(email=email)
            if check_password(password, customer.password):
                request.session['customer_id'] = customer.id
                request.session['customer_name'] = customer.username
                messages.success(request, f'Welcome back, {customer.get_full_name()}!')

                next_url = request.session.pop('next_after_login', None)
                if next_url:
                    return redirect(next_url)
                return redirect('customer:customer_dashboard')
            messages.error(request, 'Invalid password.')
        except Customer.DoesNotExist:
            messages.error(request, 'Email not found. Please register first.')

    return render(request, 'website/login.html', {'title': 'Login'})


def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'customer')

        if not username or not email or not password:
            messages.error(request, 'Please fill in all required fields.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        elif role == 'tailor':
            request.session['tailor_registration'] = {
                'username': username,
                'email': email,
                'mobile': mobile,
                'password': password,
            }
            return redirect('website:become_tailor')
        elif Customer.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            Customer.objects.create(
                username=username,
                email=email,
                mobile=mobile,
                password=make_password(password),
            )
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('website:login')

    return render(request, 'website/register.html', {'title': 'Register'})


def become_tailor(request):
    reg_data = request.session.get('tailor_registration', {})

    if request.method == 'POST':
        first_name = request.POST.get('first_name', request.POST.get('name', '')).strip()
        last_name = request.POST.get('last_name', '').strip()
        shop_name = request.POST.get('shop_name', '').strip()
        email = request.POST.get('email', reg_data.get('email', '')).strip()
        mobile = request.POST.get('phone', request.POST.get('mobile', reg_data.get('mobile', ''))).strip()
        experience = request.POST.get('experience', '0')
        specialty = request.POST.get('specialty', 'All Types')
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        password = request.POST.get('password', reg_data.get('password', ''))

        if not email or not mobile or not password:
            messages.error(request, 'Email, phone, and password are required.')
            return render(request, 'website/become_a_tailor.html', {'title': 'Become a Tailor'})

        if Tailor.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'website/become_a_tailor.html', {'title': 'Become a Tailor'})

        username = email.split('@')[0]
        base_username = username
        counter = 1
        while Tailor.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1

        try:
            years = int(''.join(filter(str.isdigit, str(experience))) or 0)
        except ValueError:
            years = 0

        Tailor.objects.create(
            username=username,
            email=email,
            mobile=mobile,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            shop_name=shop_name or f"{first_name}'s Tailoring",
            shop_address=address,
            city=city,
            specialty=specialty if specialty in dict(Tailor.SPECIALTY_CHOICES) else 'All Types',
            years_of_experience=years,
            is_active=False,
            is_verified=False,
        )

        request.session.pop('tailor_registration', None)

        try:
            send_mail(
                'New Tailor Application - FITORA',
                f'New tailor application:\nName: {first_name} {last_name}\nShop: {shop_name}\nEmail: {email}\nPhone: {mobile}',
                settings.EMAIL_HOST_USER,
                [getattr(settings, 'CONTACT_EMAIL', 'admin@fitora.com')],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, 'Application submitted! Admin will review and activate your account soon.')
        return redirect('website:login')

    context = {
        'title': 'Become a Tailor',
        'reg_data': reg_data,
        'specialties': Tailor.SPECIALTY_CHOICES,
    }
    return render(request, 'website/become_a_tailor.html', context)


# ==================== API ENDPOINTS ====================

def api_track_order(request):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Invalid request'})

    order_id = request.GET.get('order_id', '').strip()
    if not order_id:
        return JsonResponse({'success': False, 'message': 'Order ID required'})

    order = CustomerOrder.objects.filter(order_number__icontains=order_id).first()
    order_type = 'customer'
    if not order:
        order = TailorOrder.objects.filter(order_number__icontains=order_id).first()
        order_type = 'tailor'

    if not order:
        return JsonResponse({'success': False, 'message': 'Order not found. Check your order number.'})

    progress = getattr(order, 'progress_percentage', 50)
    tailor_name = getattr(order, 'tailor_name', None)
    if not tailor_name and hasattr(order, 'tailor'):
        tailor_name = get_tailor_display_name(order.tailor)

    payment_status = getattr(order, 'payment_status', 'Pending')
    amount = float(getattr(order, 'amount', 0) or 0)
    balance = float(getattr(order, 'balance_due', 0) or 0)

    return JsonResponse({
        'success': True,
        'order': {
            'id': order.order_number,
            'status': order.status,
            'progress': progress,
            'garment_type': getattr(order, 'garment_type', 'Custom'),
            'description': getattr(order, 'description', '') or '',
            'tailor_name': tailor_name or 'Assigned soon',
            'delivery_date': order.delivery_date.strftime('%d %b %Y') if order.delivery_date else 'Not set',
            'created_date': order.created_at.strftime('%d %b %Y'),
            'payment_status': payment_status,
            'amount': amount,
            'balance_due': balance,
            'order_type': order_type,
        },
    })


@require_http_methods(['POST'])
def api_contact_form(request):
    """Legacy AJAX endpoint — redirects JSON for fetch clients."""
    name = request.POST.get('name', '')
    email = request.POST.get('email', '')
    message = request.POST.get('message', '')
    try:
        send_mail(
            f'Contact Form: {name}',
            f'From: {name} ({email})\n\nMessage: {message}',
            settings.EMAIL_HOST_USER,
            [getattr(settings, 'CONTACT_EMAIL', 'support@fitora.com')],
            fail_silently=True,
        )
        return JsonResponse({'success': True, 'message': 'Message sent successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_http_methods(['POST'])
def api_tailor_application(request):
    return JsonResponse({'success': False, 'message': 'Use the become-tailor form instead.'})


@require_http_methods(['POST'])
def api_chat(request):
    """AI chatbot — database-aware Gemini assistant."""
    import json
    from .chatbot import ask_gemini

    if not request.session.session_key:
        request.session.create()

    try:
        body = json.loads(request.body) if request.body else {}
        user_message = (body.get('message') or request.POST.get('message', '')).strip()
    except json.JSONDecodeError:
        user_message = request.POST.get('message', '').strip()

    if not user_message:
        return JsonResponse({'success': False, 'message': 'Please enter a message.'})

    if len(user_message) > 2000:
        return JsonResponse({'success': False, 'message': 'Message too long.'})

    session_key = request.session.session_key
    reply = ask_gemini(request, user_message, session_key)
    return JsonResponse({'success': True, 'reply': reply})


def api_chat_history(request):
    """Return recent chat messages for current session."""
    from .models import ChatMessage

    if not request.session.session_key:
        return JsonResponse({'success': True, 'messages': []})

    messages = ChatMessage.objects.filter(
        session_key=request.session.session_key
    ).order_by('created_at')[-20:]

    data = [{'role': m.role, 'content': m.content} for m in messages]
    return JsonResponse({'success': True, 'messages': data})
