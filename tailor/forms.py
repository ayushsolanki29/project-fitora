from django import forms
from .models import (
    Tailor, 
    TailorCustomer, 
    TailorOrder, 
    TailorPayment, 
    TailorMeasurement
)
from django.contrib.auth.hashers import make_password

class TailorRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = Tailor
        fields = ['username', 'email', 'mobile', 'password']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Tailor.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Tailor.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already taken')
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class TailorProfileForm(forms.ModelForm):
    class Meta:
        model = Tailor
        fields = ['first_name', 'last_name', 'profile_pic', 'specialty', 
                  'years_of_experience', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'specialty': forms.Select(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of experience'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell about yourself'}),
        }


class TailorShopDetailsForm(forms.ModelForm):
    class Meta:
        model = Tailor
        fields = ['shop_name', 'shop_address', 'city', 'opening_time', 'closing_time', 'working_days', 'is_open']
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Shop name'}),
            'shop_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full shop address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'working_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mon-Sat'}),
            'is_open': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TailorCustomerForm(forms.ModelForm):
    class Meta:
        model = TailorCustomer
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'notes']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any special notes'}),
        }


class TailorMeasurementForm(forms.ModelForm):
    class Meta:
        model = TailorMeasurement
        fields = ['neck', 'chest', 'waist', 'hip', 'shoulder', 'sleeve_length', 
                  'inseam', 'length', 'bicep', 'thigh', 'calf', 'notes']
        widgets = {
            'neck': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'inches'}),
            'chest': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'inches'}),
            'waist': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'inches'}),
            'hip': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'inches'}),
            'shoulder': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'inches'}),
            'sleeve_length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'inches'}),
            'inseam': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'inches'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'inches'}),
            'bicep': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'inches'}),
            'thigh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'inches'}),
            'calf': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'inches'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }


class TailorOrderForm(forms.ModelForm):
    class Meta:
        model = TailorOrder
        fields = ['customer', 'garment_type', 'description', 'amount', 'advance_paid', 
                  'priority', 'delivery_date']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'garment_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Suit, Shirt, Lehenga'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Order details'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Total amount'}),
            'advance_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Advance paid'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class TailorPaymentForm(forms.ModelForm):
    class Meta:
        model = TailorPayment
        fields = ['order', 'amount', 'method', 'note']
        widgets = {
            'order': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Amount'}),
            'method': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Payment note (optional)'}),
        }