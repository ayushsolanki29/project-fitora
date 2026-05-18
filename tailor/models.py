from django.db import models
import random
import uuid

class Tailor(models.Model):
    SPECIALTY_CHOICES = [
        ('Suits & Blazers', 'Suits & Blazers'),
        ('Traditional Wear', 'Traditional Wear'),
        ('Bridal Wear', 'Bridal Wear'),
        ('Casual Wear', 'Casual Wear'),
        ('Alterations', 'Alterations'),
        ('All Types', 'All Types'),
    ]
    
    # Basic Info
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    
    # Profile Info
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='tailor_profiles/', blank=True, null=True)
    specialty = models.CharField(max_length=50, choices=SPECIALTY_CHOICES, default='Suits & Blazers')
    years_of_experience = models.IntegerField(default=0)
    bio = models.TextField(blank=True, null=True)
    
    # Shop Details
    shop_name = models.CharField(max_length=200, blank=True, null=True)
    shop_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    opening_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)
    working_days = models.CharField(max_length=100, default='Mon-Sat')
    is_open = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Earnings
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def name(self):
        """Alias used across templates and legacy code."""
        return self.get_full_name()

    @property
    def display_name(self):
        return self.shop_name or self.get_full_name()

    @property
    def completed_orders_count(self):
        return self.orders.filter(status__in=['Completed', 'Delivered']).count()


class TailorCustomer(models.Model):
    tailor = models.ForeignKey(Tailor, on_delete=models.CASCADE, related_name='customers')
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    
    # Changed from 'measurements' to 'customer_measurements' to avoid conflict
    customer_measurements = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    profile_pic = models.ImageField(upload_to='customer_profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class TailorOrder(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Cutting', 'Cutting'),
        ('Stitching', 'Stitching'),
        ('Completed', 'Completed'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]
    
    tailor = models.ForeignKey(Tailor, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(TailorCustomer, on_delete=models.CASCADE, related_name='orders')
    
    order_number = models.CharField(max_length=50, unique=True, blank=True)
    garment_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Normal')
    
    delivery_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    cancellation_reason = models.TextField(blank=True, null=True)
    is_refunded = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD{random.randint(10000, 99999)}{uuid.uuid4().hex[:4].upper()}"
        if self.amount:
            self.balance_due = self.amount - self.advance_paid
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    @property
    def is_overdue(self):
        from datetime import date
        return date.today() > self.delivery_date and self.status != 'Delivered'


class TailorPayment(models.Model):
    METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('UPI', 'UPI'),
        ('Bank Transfer', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]
    
    tailor = models.ForeignKey(Tailor, on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey(TailorOrder, on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(TailorCustomer, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='Cash')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    note = models.TextField(blank=True, null=True)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RCP{random.randint(10000, 99999)}{self.created_at.strftime('%Y%m%d') if self.created_at else ''}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Payment #{self.receipt_number}"


class TailorMeasurement(models.Model):
    # Fixed: Added unique related_name to avoid conflict
    customer = models.ForeignKey(
        TailorCustomer, 
        on_delete=models.CASCADE, 
        related_name='measurement_records'  # Changed from 'measurements'
    )
    tailor = models.ForeignKey(Tailor, on_delete=models.CASCADE, related_name='measurement_records')
    
    neck = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    chest = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    waist = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    hip = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    shoulder = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    sleeve_length = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    inseam = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    length = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    bicep = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    thigh = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    calf = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    measurement_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Measurements for {self.customer.get_full_name()}"