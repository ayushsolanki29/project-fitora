from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='admins/', blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Admin: {self.user.username}"


class AdminTailor(models.Model):
    SPECIALTY_CHOICES = [
        ('Suits & Blazers', 'Suits & Blazers'),
        ('Traditional Wear', 'Traditional Wear'),
        ('Casual Wear', 'Casual Wear'),
        ('Wedding Attire', 'Wedding Attire'),
        ('Bridal Wear', 'Bridal Wear'),
        ('Alterations', 'Alterations'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    specialty = models.CharField(max_length=50, choices=SPECIALTY_CHOICES, default='Suits & Blazers')
    profile_pic = models.ImageField(upload_to='tailors/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    completed_orders = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    def __str__(self):
        return self.name


class AdminCustomer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_customer_profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='customers/', blank=True, null=True)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username


class AdminOrder(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Delivered', 'Delivered'),
    ]
    
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]
    
    customer = models.ForeignKey(AdminCustomer, on_delete=models.CASCADE, related_name='orders')
    tailor = models.ForeignKey(AdminTailor, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    order_number = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    measurements = models.JSONField(default=dict, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Normal')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_date = models.DateField(null=True, blank=True)
    
    cancellation_reason = models.TextField(blank=True, null=True)
    refund_issued = models.BooleanField(default=False)
    rating = models.IntegerField(default=0, blank=True)
    
    def __str__(self):
        return f"Order #{self.order_number}"


class AdminPayment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    
    METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('UPI', 'UPI'),
        ('Net Banking', 'Net Banking'),
        ('Cash', 'Cash'),
    ]
    
    order = models.ForeignKey(AdminOrder, on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(AdminCustomer, on_delete=models.CASCADE, related_name='payments')
    tailor = models.ForeignKey(AdminTailor, on_delete=models.SET_NULL, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='Cash')
    transaction_ref = models.CharField(max_length=100, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.transaction_ref:
            self.transaction_ref = f"TXN{random.randint(100000, 999999)}{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Payment {self.transaction_ref}"


class AdminTransactionRecord(models.Model):
    payment = models.OneToOneField(AdminPayment, on_delete=models.CASCADE, related_name='transaction_record')
    gateway_id = models.CharField(max_length=100)
    gateway_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_verified = models.BooleanField(default=False)
    processed_date = models.DateTimeField(auto_now_add=True)
    response_data = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Transaction {self.gateway_id}"