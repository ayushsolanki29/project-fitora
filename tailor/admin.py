from django.contrib import admin
from .models import (
    Tailor, 
    TailorCustomer, 
    TailorOrder, 
    TailorPayment, 
    TailorMeasurement
)

@admin.register(Tailor)
class TailorAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'mobile', 'is_active', 'is_verified', 'total_earnings', 'get_full_name_display']
    list_filter = ['is_active', 'is_verified', 'specialty']
    search_fields = ['username', 'email', 'mobile', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at', 'total_earnings', 'pending_balance']
    
    def get_full_name_display(self, obj):
        return obj.get_full_name()
    get_full_name_display.short_description = 'Full Name'

@admin.register(TailorCustomer)
class TailorCustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone_number', 'email', 'tailor', 'order_count', 'created_at']
    list_filter = ['tailor', 'is_active']
    search_fields = ['first_name', 'last_name', 'phone_number', 'email']
    
    def order_count(self, obj):
        return obj.orders.count()
    order_count.short_description = 'Total Orders'

@admin.register(TailorOrder)
class TailorOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'garment_type', 'amount', 'advance_paid', 'balance_due', 'status', 'delivery_date']
    list_filter = ['status', 'priority', 'tailor']
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'balance_due']

@admin.register(TailorPayment)
class TailorPaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'order', 'customer', 'amount', 'method', 'status', 'created_at']
    list_filter = ['method', 'status', 'tailor']
    search_fields = ['receipt_number', 'order__order_number', 'customer__first_name']
    readonly_fields = ['receipt_number', 'created_at', 'updated_at']

@admin.register(TailorMeasurement)
class TailorMeasurementAdmin(admin.ModelAdmin):
    list_display = ['customer', 'measurement_date', 'tailor', 'chest', 'waist', 'hip']
    list_filter = ['tailor', 'measurement_date']
    search_fields = ['customer__first_name', 'customer__last_name']
    readonly_fields = ['measurement_date', 'updated_at']
    
    fieldsets = (
        ('Customer Info', {
            'fields': ('customer', 'tailor')
        }),
        ('Body Measurements', {
            'fields': ('neck', 'chest', 'waist', 'hip', 'shoulder', 'sleeve_length', 'inseam', 'length', 'bicep', 'thigh', 'calf')
        }),
        ('Additional Info', {
            'fields': ('notes',)
        }),
    )