from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from tailor.models import Tailor
from customer.models import Customer
from adminpanel.sync import sync_all_admin_tailors


SAMPLE_TAILORS = [
    {
        'username': 'ramesh_tailor',
        'email': 'ramesh@fitora.com',
        'mobile': '9876543210',
        'first_name': 'Ramesh',
        'last_name': 'Patel',
        'shop_name': 'Ramesh Tailor Studio',
        'city': 'Ahmedabad',
        'specialty': 'Traditional Wear',
        'years_of_experience': 12,
        'bio': 'Expert in bridal wear, lehenga, and designer outfits.',
    },
    {
        'username': 'meena_boutique',
        'email': 'meena@fitora.com',
        'mobile': '9876543211',
        'first_name': 'Meena',
        'last_name': 'Shah',
        'shop_name': 'Meena Boutique',
        'city': 'Mumbai',
        'specialty': 'Bridal Wear',
        'years_of_experience': 15,
        'bio': 'Premium boutique for designer dresses and embroidery.',
    },
    {
        'username': 'suresh_tailor',
        'email': 'suresh@fitora.com',
        'mobile': '9876543212',
        'first_name': 'Suresh',
        'last_name': 'Kumar',
        'shop_name': 'Suresh Formal Wear',
        'city': 'Surat',
        'specialty': 'Suits & Blazers',
        'years_of_experience': 10,
        'bio': 'Professional mens tailoring for suits and formal wear.',
    },
]


class Command(BaseCommand):
    help = 'Seed sample tailors and sync admin tailors to the public portal'

    def handle(self, *args, **options):
        synced = sync_all_admin_tailors()
        self.stdout.write(self.style.SUCCESS(f'Synced {synced} admin tailor(s)'))

        created = 0
        for data in SAMPLE_TAILORS:
            if Tailor.objects.filter(email=data['email']).exists():
                continue
            Tailor.objects.create(
                password=make_password('Tailor@123'),
                shop_address='FITORA Marketplace',
                is_active=True,
                is_verified=True,
                is_open=True,
                **data,
            )
            created += 1

        if not Customer.objects.filter(email='demo@fitora.com').exists():
            Customer.objects.create(
                username='demo_customer',
                email='demo@fitora.com',
                mobile='9999999999',
                password=make_password('Customer@123'),
                first_name='Demo',
                last_name='Customer',
            )
            self.stdout.write(self.style.SUCCESS('Created demo customer: demo@fitora.com / Customer@123'))

        self.stdout.write(self.style.SUCCESS(f'Created {created} sample tailor(s)'))
        self.stdout.write(self.style.SUCCESS(f'Total active tailors: {Tailor.objects.filter(is_active=True).count()}'))
