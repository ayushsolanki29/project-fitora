from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'adminsite'

urlpatterns = [
    # Authentication
    path('', views.login_page, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('forget-password/', views.forgot_password, name='forgot_password'),
    path('verify-reset/', views.verify_reset, name='verify_reset'),
    path('new-password/', views.new_password, name='new_password'),
    
    # Dashboard
    path('dashboard/', views.adminsite_dashboard, name='adminsite_dashboard'),
    
    # Tailors
    path('view-all-tailors/', views.view_all_tailors, name='view_all_tailors'),
    path('add-new-tailor/', views.add_new_tailor, name='add_new_tailor'),
    path('edit-tailor/<int:tailor_id>/', views.edit_tailor, name='edit_tailor'),
    path('delete-tailor/<int:tailor_id>/', views.delete_tailor, name='delete_tailor'),
    path('toggle-tailor-status/<int:tailor_id>/', views.toggle_tailor_status, name='toggle_tailor_status'),
    path('tailor-performance/', views.tailor_performance, name='tailor_performance'),
    
    # Customer Management
    path('view-all-customers/', views.view_all_customers, name='view_all_customers'),
    path('customer-order-history/<int:customer_id>/', views.customer_order_history, name='customer_order_history'),
    path('customer-details/<int:customer_id>/', views.customer_details, name='customer_details'),
    path('toggle-customer-status/<int:customer_id>/', views.toggle_customer_status, name='toggle_customer_status'),
    
    # Orders
    path('view-all-orders/', views.view_all_orders, name='view_all_orders'),
    path('order-details/<int:order_id>/', views.order_details, name='order_details'),
    path('pending-orders/', views.pending_orders, name='pending_orders'),
    path('completed-orders/', views.completed_orders, name='completed_orders'),
    path('cancelled-orders/', views.cancelled_orders, name='cancelled_orders'),
    path('approve-order/<int:order_id>/', views.approve_order, name='approve_order'),
    path('assign-tailor/<int:order_id>/', views.assign_tailor, name='assign_tailor'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    
    # Payments Management
    path('pending-payments/', views.pending_payments, name='pending_payments'),
    path('transaction-records/', views.transaction_records, name='transaction_records'),
    path('all-payments/', views.all_payments, name='all_payments'),
    path('verify-payment/<int:payment_id>/', views.verify_payment, name='verify_payment'),
    path('decline-payment/<int:payment_id>/', views.decline_payment, name='decline_payment'),
    
    # Reports
    path('order-reports/', views.order_reports, name='order_reports'),
    path('payment-reports/', views.payment_reports, name='payment_reports'),
    path('tailor-reports/', views.tailor_reports, name='tailor_reports'),
    path('monthly-reports/', views.monthly_reports, name='monthly_reports'),
    
    # Admin Profile
    path('view-profile/', views.view_profile, name='view_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('update-details/', views.update_details, name='update_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)