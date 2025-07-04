from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=10)  # ✅ New: Stock quantity
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    is_offer = models.BooleanField(default=False)  # 🔸 Add this field


    def __str__(self):
        return self.name


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('CARD', 'Card'),
        ('PHONEPE', 'PhonePe'),
        ('GPAY', 'Google Pay'),
        ('COD', 'Cash on Delivery'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    pincode = models.CharField(max_length=10, default='')  
    total = models.FloatField()
    ordered_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='COD')

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price if self.price else 0

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"


class RegistrationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=45, default='127.0.0.1')
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.username} registered from {self.ip_address}"

class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=now)
    ip_address = models.GenericIPAddressField(blank=True, null=True)  # Optional


    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png')

    def __str__(self):
        return self.user.username
