from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'customer'

urlpatterns = [
    # Authentication
    path('', views.login, name='login'),
    path('register/', views.Register, name='Register'),
    path('verify-otp/', views.verifyotp, name='verifyotp'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('verify-reset/', views.verifyreset, name='verifyreset'),
    path('new-password/', views.new__password, name='new_password'),
    path('logout/', views.logout_user, name='logout'),
    
    # Dashboard
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    
    # Profile Management
    path('view-profile/', views.view_profile, name='view_profile'),
    path('edit-personal-details/', views.edit_personal_details, name='edit_personal_details'),
    path('change-password/', views.change_password, name='change_password'),
    path('address-information/', views.address_information, name='address_information'),
    path('add-address/', views.add_address, name='add_address'),
    
    # Orders
    path('view-all-orders/', views.view_all_orders, name='view_all_orders'),
    path('order-details/<int:order_id>/', views.order_details, name='order_details'),
    path('order-status-tracking/<int:order_id>/', views.order_status_tracking, name='order_status_tracking'),
    path('delivery-date-information/<int:order_id>/', views.delivery_date_information, name='delivery_date_information'),
    
    # Track Order
    path('live-order-status/<int:order_id>/', views.live_order_status, name='live_order_status'),
    
    # Payments
    path('make-payment/', views.make_payment, name='make_payment'),
    path('payment/success/', views.stripe_success, name='stripe_success'),
    path('payment/cancel/', views.stripe_cancel, name='stripe_cancel'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('download-receipt/<int:payment_id>/', views.download_receipt, name='download_receipt'),
    
    # Order History
    path('previous-orders/', views.previous_orders, name='previous_orders'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)