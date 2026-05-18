from decimal import Decimal

from customer.models import Customer, CustomerOrder
from tailor.models import Tailor, TailorCustomer, TailorOrder

GARMENT_BASE_PRICES = {
    'shirt': Decimal('800'),
    'pants': Decimal('1000'),
    'dress': Decimal('1500'),
    'suit': Decimal('3500'),
    'kurta': Decimal('1200'),
    'blouse': Decimal('900'),
    'lehenga': Decimal('5000'),
    'sherwani': Decimal('4500'),
    'alteration': Decimal('400'),
    'default': Decimal('1000'),
}


def get_tailor_display_name(tailor):
    if tailor.shop_name:
        return tailor.shop_name
    return tailor.get_full_name()


def estimate_order_amount(garment_type):
    if not garment_type:
        return GARMENT_BASE_PRICES['default']
    key = garment_type.strip().lower()
    for name, price in GARMENT_BASE_PRICES.items():
        if name in key:
            return price
    return GARMENT_BASE_PRICES['default']


def sync_customer_order_to_tailor(customer_order, tailor):
    """Mirror a website booking into the tailor portal."""
    customer = customer_order.customer
    tailor_customer, _ = TailorCustomer.objects.get_or_create(
        tailor=tailor,
        phone_number=customer.mobile,
        defaults={
            'first_name': customer.first_name or customer.username,
            'last_name': customer.last_name or '',
            'email': customer.email,
        },
    )

    TailorOrder.objects.get_or_create(
        tailor=tailor,
        order_number=customer_order.order_number,
        defaults={
            'customer': tailor_customer,
            'garment_type': customer_order.garment_type,
            'description': customer_order.description,
            'amount': customer_order.amount,
            'advance_paid': customer_order.advance_paid,
            'balance_due': customer_order.balance_due,
            'status': 'Pending',
            'delivery_date': customer_order.delivery_date,
        },
    )
