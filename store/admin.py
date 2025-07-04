from django.contrib import admin
from .models import Category, Product, Order, OrderItem, UserProfile, RegistrationLog, LoginLog

# Inline order items display inside the Order admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'subtotal']

    def subtotal(self, obj):
        return obj.subtotal()
    subtotal.short_description = 'Subtotal'


# Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'quantity']
    list_filter = ['category']
    search_fields = ['name', 'description']


# Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'ordered_at', 'total', 'pincode']
    list_filter = ['ordered_at', 'payment_method']
    search_fields = ['user__username', 'id', 'pincode']
    inlines = [OrderItemInline]


# UserProfile Admin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile', 'address']
    search_fields = ['user__username', 'mobile']


# RegistrationLog Admin
class RegistrationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'timestamp']
    search_fields = ['user__username']


# LoginLog Admin
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time','ip_address']
    search_fields = ['user__username']

# Register all models
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(RegistrationLog, RegistrationLogAdmin)
admin.site.register(LoginLog, LoginLogAdmin)
