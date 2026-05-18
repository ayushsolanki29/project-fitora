"""Gemini AI chatbot with live FITORA database context + smart fallback."""
from django.conf import settings

from customer.models import Customer, CustomerOrder
from tailor.models import Tailor
from .models import ChatMessage

SYSTEM_PROMPT = """You are FITORA Assistant for a tailoring platform in India.
Answer briefly about booking, tailors, orders, payments. Use the database context provided.
Prices in ₹. Be friendly and helpful."""


def build_database_context(request):
    lines = ['=== FITORA LIVE DATABASE ===']
    tailors = Tailor.objects.filter(is_active=True).order_by('-is_verified')[:15]
    lines.append(f'\nACTIVE TAILORS ({tailors.count()}):')
    for t in tailors:
        lines.append(
            f'- {t.display_name} | {t.specialty} | {t.city or "India"} | '
            f'{t.years_of_experience} yrs | verified={t.is_verified}'
        )
    if not tailors.exists():
        lines.append('- No tailors yet. Register at /become-tailor/')

    lines.append('\nPAGES: /tailors/ /book-tailor/ /track-order/ /login/ /customer/ /adminpanel/')
    lines.append('PAYMENTS: Stripe card payments at /customer/make-payment/')

    customer_id = request.session.get('customer_id')
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
            orders = CustomerOrder.objects.filter(customer=customer).order_by('-created_at')[:5]
            lines.append(f'\nCUSTOMER: {customer.get_full_name()} ({customer.email})')
            for o in orders:
                lines.append(
                    f'- #{o.order_number} | {o.garment_type} | {o.status} | '
                    f'₹{o.amount} | paid ₹{o.advance_paid} | due ₹{o.balance_due}'
                )
        except Customer.DoesNotExist:
            pass
    return '\n'.join(lines)


def get_chat_history(session_key, limit=10):
    messages = ChatMessage.objects.filter(session_key=session_key).order_by('-created_at')[:limit]
    return list(reversed(messages))


def rule_based_reply(request, user_message):
    """Database-connected fallback when Gemini is unavailable."""
    msg = user_message.lower()
    tailors = Tailor.objects.filter(is_active=True)
    customer_id = request.session.get('customer_id')

    if any(w in msg for w in ['hello', 'hi', 'hey', 'help']):
        return (
            f"Hello! I'm FITORA Assistant. We have {tailors.count()} active tailor(s) on the platform. "
            "Ask me about tailors, booking, orders, payments, or tracking!"
        )

    if any(w in msg for w in ['tailor', 'tailors', 'shop', 'stitch']):
        if not tailors.exists():
            return "No tailors are listed yet. You can apply at /become-tailor/ or check back soon!"
        lines = [f"Here are our {tailors.count()} active tailor(s) from the database:\n"]
        for t in tailors[:10]:
            lines.append(f"• **{t.display_name}** — {t.specialty}, {t.city or 'India'} ({t.years_of_experience} yrs exp)")
        lines.append("\n👉 Book now: /book-tailor/")
        return '\n'.join(lines)

    if any(w in msg for w in ['book', 'booking', 'order']):
        return (
            "To book a tailor:\n"
            "1. Register/login at /login/\n"
            "2. Go to /book-tailor/\n"
            "3. Select tailor, garment type, delivery date\n"
            "4. Pay via Stripe at /customer/make-payment/\n"
            f"We currently have {tailors.count()} tailor(s) available."
        )

    if any(w in msg for w in ['pay', 'payment', 'stripe', 'price', 'cost']):
        return (
            "Payments are processed securely via **Stripe** (test mode).\n"
            "After booking, go to Customer Portal → Make Payment.\n"
            "Estimated prices: Shirt ~₹800, Pants ~₹1000, Suit ~₹3500, Lehenga ~₹5000.\n"
            "Cash payment at the tailor shop is also supported."
        )

    if any(w in msg for w in ['track', 'status', 'where']):
        return (
            "Track your order at /track-order/ using your order number (e.g. ORD95839...).\n"
            "You can also check status in the Customer Portal after login."
        )

    if customer_id and any(w in msg for w in ['my order', 'my orders', 'order']):
        orders = CustomerOrder.objects.filter(customer_id=customer_id).order_by('-created_at')[:5]
        if not orders:
            return "You have no orders yet. Book at /book-tailor/"
        lines = ["Your recent orders from the database:\n"]
        for o in orders:
            lines.append(
                f"• #{o.order_number} — {o.garment_type}, {o.status}, "
                f"₹{o.amount} (due ₹{o.balance_due}), tailor: {o.tailor_name or 'TBD'}"
            )
        return '\n'.join(lines)

    if any(w in msg for w in ['login', 'register', 'account']):
        return "Register at /register/ or login at /login/. Demo: demo@fitora.com / Customer@123"

    ctx = build_database_context(request)
    return (
        f"I can help with tailors, booking, payments, and order tracking. "
        f"Try asking 'show tailors' or 'how to book'.\n\nLive data:\n{ctx[:600]}..."
    )


def call_gemini(conversation):
    """Try Gemini API (new SDK first, then legacy)."""
    if not settings.GEMINI_API_KEY:
        return None

    try:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        for model in ('gemini-2.0-flash-lite', 'gemini-2.0-flash', 'gemini-1.5-flash'):
            try:
                response = client.models.generate_content(model=model, contents=conversation)
                if response and response.text:
                    return response.text.strip()
            except Exception:
                continue
    except ImportError:
        pass

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        for model_name in ('gemini-2.0-flash-lite', 'gemini-2.0-flash', 'gemini-1.5-flash'):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(conversation)
                if response and response.text:
                    return response.text.strip()
            except Exception:
                continue
    except ImportError:
        pass

    return None


def ask_gemini(request, user_message, session_key):
    customer_id = request.session.get('customer_id')

    ChatMessage.objects.create(
        session_key=session_key,
        customer_id=customer_id,
        role='user',
        content=user_message,
    )

    db_context = build_database_context(request)
    history = get_chat_history(session_key, limit=8)

    conversation = f'{SYSTEM_PROMPT}\n\n{db_context}\n\n--- CHAT ---\n'
    for msg in history[:-1]:
        label = 'User' if msg.role == 'user' else 'Assistant'
        conversation += f'{label}: {msg.content}\n'
    conversation += f'User: {user_message}\nAssistant:'

    reply = call_gemini(conversation)
    if not reply:
        reply = rule_based_reply(request, user_message)
        reply += '\n\n_(Using database assistant — Gemini API quota may be exceeded. Add billing at Google AI Studio for full AI.)_'

    ChatMessage.objects.create(
        session_key=session_key,
        customer_id=customer_id,
        role='assistant',
        content=reply,
    )

    return reply
