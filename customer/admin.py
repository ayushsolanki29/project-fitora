from django.contrib import admin
from .models import Customer, CustomerAddress, CustomerOrder, CustomerPayment

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'mobile', 'is_active', 'is_verified', 'created_at']
    list_filter = ['is_active', 'is_verified']
    search_fields = ['username', 'email', 'mobile', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'full_name', 'city', 'pincode', 'is_default']
    list_filter = ['is_default', 'city']
    search_fields = ['full_name', 'street', 'city']

@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'garment_type', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'customer__username', 'customer__email']

@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'customer', 'order', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['transaction_id', 'customer__username']