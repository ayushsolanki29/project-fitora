from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'tailor'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),
    path('verify-otp/', views.verifyotp, name='verifyotp'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('verify-reset/', views.verifyreset, name='verifyreset'),
    path('new-password/', views.new_password, name='new_password'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.tailor_dashboard, name='tailor_dashboard'),
    
    # Profile Management
    path('view-profile/', views.view_profile, name='view_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('shop-details/', views.shop_details, name='shop_details'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Customer Management
    path('view-customers/', views.view_customers, name='view_customers'),
    path('customer-measurement-records/', views.customer_measurement_records, name='customer_measurement_records'),
    path('add-new-customer/', views.add_new_customer, name='add_new_customer'),
    path('customer-order-history/', views.customer_order_history, name='customer_order_history'),
    
    # Order Management
    path('create-new-orders/', views.create_new_orders, name='create_new_orders'),
    path('view-all-orders/', views.view_all_orders, name='view_all_orders'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('pending-orders/', views.pending_orders, name='pending_orders'),
    path('delivered-orders/', views.delivered_orders, name='delivered_orders'),
    path('cancelled-orders/', views.cancelled_orders, name='cancelled_orders'),
    
    # Payment Management
    path('add-payments/', views.add_payments, name='add_payments'),
    path('view-payments/', views.view_payments, name='view_payments'),
    path('pending-payments/', views.pending_payments, name='pending_payments'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('generate-receipt/<int:payment_id>/', views.generate_receipt, name='generate_receipt'),
    
    # Delivery Schedule
    path('delivery-calendar/', views.delivery_calender, name='delivery_calender'),
    path('upcoming-deliveries/', views.upcoming_deliveries, name='upcoming_deliveries'),
    
    # Reports
    path('monthly-reports/', views.monthly_reports, name='monthly_reports'),
    path('income-reports/', views.income_reports, name='income_reports'),
    path('customer-reports/', views.customer_reports, name='customer_reports'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)