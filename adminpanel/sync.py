"""Sync admin panel tailors to the public tailor portal."""
from django.contrib.auth.hashers import make_password

from tailor.models import Tailor
from .models import AdminTailor


def sync_admin_tailor_to_portal(admin_tailor):
    """Create or update tailor.Tailor from AdminTailor."""
    username = admin_tailor.email.split('@')[0]
    base = username
    counter = 1
    existing = Tailor.objects.filter(email=admin_tailor.email).first()
    while Tailor.objects.filter(username=username).exclude(pk=existing.pk if existing else None).exists():
        username = f'{base}{counter}'
        counter += 1

    name_parts = admin_tailor.name.split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    defaults = {
        'username': username,
        'mobile': admin_tailor.phone or '0000000000',
        'password': make_password('Tailor@123'),
        'first_name': first_name,
        'last_name': last_name,
        'shop_name': admin_tailor.name,
        'shop_address': admin_tailor.address or '',
        'specialty': admin_tailor.specialty if admin_tailor.specialty in dict(Tailor.SPECIALTY_CHOICES) else 'All Types',
        'years_of_experience': admin_tailor.experience_years,
        'is_active': admin_tailor.is_active,
        'is_verified': admin_tailor.is_active,
    }

    tailor, created = Tailor.objects.update_or_create(
        email=admin_tailor.email,
        defaults=defaults,
    )
    return tailor, created


def sync_all_admin_tailors():
    count = 0
    for admin_tailor in AdminTailor.objects.all():
        sync_admin_tailor_to_portal(admin_tailor)
        count += 1
    return count
