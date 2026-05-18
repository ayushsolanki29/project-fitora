from django.conf import settings


def stripe_keys(request):
    return {
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'GEMINI_CHAT_ENABLED': bool(settings.GEMINI_API_KEY),
    }
