import stripe
from decimal import Decimal

from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse

from .models import Customer, CustomerOrder, CustomerPayment

stripe.api_key = settings.STRIPE_SECRET_KEY


def _stripe_value(obj, key, default=None):
    """Read a field from a Stripe object (dict-like access, not .get())."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return obj[key]
    except (KeyError, TypeError):
        return getattr(obj, key, default)


def create_stripe_checkout(request, order_id, amount):
    """Create Stripe Checkout Session and redirect to payment page."""
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, id=customer_id)
    order = get_object_or_404(CustomerOrder, id=order_id, customer=customer)

    pay_amount = Decimal(str(amount)) if amount else (order.balance_due or order.amount)
    if pay_amount <= 0:
        messages.error(request, 'Invalid payment amount.')
        return None

    amount_paise = int(pay_amount * 100)
    if amount_paise < 50:
        messages.error(request, 'Minimum payment amount is ₹0.50')
        return None

    success_url = request.build_absolute_uri(
        reverse('customer:stripe_success')
    ) + '?session_id={CHECKOUT_SESSION_ID}'

    cancel_url = request.build_absolute_uri(
        reverse('customer:stripe_cancel')
    )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'unit_amount': amount_paise,
                    'product_data': {
                        'name': f'FITORA Order #{order.order_number}',
                        'description': order.garment_type or 'Tailoring service',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'order_id': str(order.id),
                'customer_id': str(customer.id),
                'order_number': order.order_number,
            },
            customer_email=customer.email,
        )
        request.session['stripe_pending_order'] = order.id
        request.session['stripe_pending_amount'] = str(pay_amount)
        return session.url
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {e.user_message if hasattr(e, "user_message") else str(e)}')
        return None


def handle_stripe_success(request):
    """Verify Stripe session and record payment in database."""
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, 'Invalid payment session.')
        return redirect('customer:make_payment')

    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer:login')

    customer = get_object_or_404(Customer, id=customer_id)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        messages.error(request, 'Could not verify payment. Contact support.')
        return redirect('customer:make_payment')

    payment_status = _stripe_value(session, 'payment_status')
    if payment_status != 'paid':
        messages.warning(request, 'Payment was not completed.')
        return redirect('customer:make_payment')

    order_id = _stripe_value(_stripe_value(session, 'metadata'), 'order_id')
    if not order_id:
        messages.error(request, 'Payment verified but order information is missing. Contact support.')
        return redirect('customer:make_payment')

    order = get_object_or_404(CustomerOrder, id=order_id, customer=customer)

    if CustomerPayment.objects.filter(transaction_id=session_id).exists():
        messages.info(request, 'Payment already recorded.')
        return redirect('customer:payment_history')

    amount_total = _stripe_value(session, 'amount_total')
    if amount_total is None:
        messages.error(request, 'Could not determine payment amount. Contact support.')
        return redirect('customer:make_payment')

    amount_paid = Decimal(amount_total) / 100

    payment = CustomerPayment.objects.create(
        customer=customer,
        order=order,
        amount=amount_paid,
        payment_method='Card',
        transaction_id=session_id,
        status='Success',
    )

    order.advance_paid += payment.amount
    order.balance_due = max(Decimal('0'), order.amount - order.advance_paid)
    if order.balance_due <= 0:
        order.payment_status = 'Paid'
    order.save()

    request.session.pop('stripe_pending_order', None)
    request.session.pop('stripe_pending_amount', None)

    messages.success(request, f'Payment of ₹{payment.amount} successful via Stripe!')
    return redirect('customer:payment_history')


def handle_stripe_cancel(request):
    messages.info(request, 'Payment cancelled. You can try again anytime.')
    return redirect('customer:make_payment')
