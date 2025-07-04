
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile/', views.profile_view, name='profile'),
path('fake-card-payment/', views.fake_card_payment, name='fake_card_payment'),
path('fake-phonepe/', views.fake_phonepe, name='fake_phonepe'),
path('fake-gpay/', views.fake_gpay, name='fake_gpay'),
path('process-order/', views.process_order, name='process_order'),
    path('offers/', views.all_offers, name='all_offers'),



]