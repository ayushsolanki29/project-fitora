from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    # Main Pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('services/', views.services, name='services'),
    path('book-tailor/', views.book_tailor, name='book_tailor'),
    path('tailors/', views.tailors, name='tailors'),
    path('pricing/', views.pricing, name='pricing'),
    path('track-order/', views.track_order, name='track_order'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication Pages
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('become-tailor/', views.become_tailor, name='become_tailor'),
    
    # AJAX Endpoints
    path('api/track-order/', views.api_track_order, name='api_track_order'),
    path('api/contact-form/', views.api_contact_form, name='api_contact_form'),
    path('api/tailor-application/', views.api_tailor_application, name='api_tailor_application'),
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/chat/history/', views.api_chat_history, name='api_chat_history'),
]