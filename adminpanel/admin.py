from django.contrib import admin
from .models import (
    AdminTailor, 
    AdminCustomer, 
    AdminOrder, 
    AdminPayment, 
    AdminTransactionRecord, 
    AdminProfile
)

@admin.register(AdminTailor)
class AdminTailorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'specialty', 'experience_years', 'is_active', 'completed_orders']
    list_filter = ['specialty', 'is_active']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AdminCustomer)
class AdminCustomerAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'get_email', 'phone', 'total_spent', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Customer Name'

@admin.register(AdminOrder)
class AdminOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'tailor', 'amount', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['order_number', 'customer__user__email', 'customer__user__first_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AdminPayment)
class AdminPaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_ref', 'order', 'customer', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['transaction_ref', 'order__order_number', 'customer__user__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AdminTransactionRecord)
class AdminTransactionRecordAdmin(admin.ModelAdmin):
    list_display = ['gateway_id', 'payment', 'net_amount', 'is_verified', 'processed_date']
    list_filter = ['is_verified', 'processed_date']
    search_fields = ['gateway_id', 'payment__transaction_ref']

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'department']
    search_fields = ['user__username', 'user__email', 'phone']