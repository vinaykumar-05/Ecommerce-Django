from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail,EmailMessage
from .forms import RegisterForm
from .models import Category, Product, Order, OrderItem, UserProfile
from django.contrib import messages
from decimal import Decimal
from django.conf import settings



# Home view
def home(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    products = Product.objects.filter(category_id=category_id) if category_id else Product.objects.all()

    for product in products:
        if product.is_offer:
            product.discounted_price = round(product.price * Decimal('0.75'), 2)

    # Build special offers to show limited products in offer section
    offers = {}
    for category in categories:
        offer_products = Product.objects.filter(category=category, is_offer=True)[:3]
        for op in offer_products:
            op.discounted_price = round(op.price * Decimal('0.75'), 2)
        if offer_products:
            offers[category.name] = offer_products

    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'offers': offers
    })

def all_offers(request):
    offers = {}
    for category in Category.objects.all():
        offer_products = Product.objects.filter(category=category, is_offer=True)[:5]
        for product in offer_products:
            product.discounted_price = round(product.price * Decimal('0.75'), 2)
        if offer_products.exists():
            offers[category.name] = offer_products
    return render(request, 'store/all_offers.html', {'offers': offers})

# Register view with welcome email
from django.utils.timezone import now
import logging
from .models import RegistrationLog

logger = logging.getLogger(__name__)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            UserProfile.objects.create(
                user=user,
                mobile=form.cleaned_data['mobile'],
                address=form.cleaned_data['address']
            )

            # Send welcome email
            send_mail(
                'Welcome to ElectroShop!',
                f"Hi {user.first_name},\n\nThank you for joining ElectroShop!",
                'your_email@gmail.com',
                [user.email],
                fail_silently=False,
            )

            # Get IP address
            ip = get_client_ip(request)

            # Save registration log in database
            RegistrationLog.objects.create(user=user, ip_address=ip)

            # Log to server log
            logger.info(f"NEW REGISTRATION: {user.username} | IP: {ip} | Time: {now()}")

            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    
    return render(request, 'store/register.html', {'form': form})
# View product detail
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'store/product_detail.html', {'product': product})

# Add to cart
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

# Remove from cart
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart')

# Display cart
def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        if product.is_offer:
            discounted_price = (product.price * Decimal('0.75')).quantize(Decimal('0.01'))
        else:
            discounted_price = product.price

        subtotal = discounted_price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': discounted_price,
            'subtotal': subtotal
        })

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

# Checkout with fake payment simulation
@login_required(login_url='login')
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        if product.is_offer:
            price = product.price * Decimal('0.75')
        else:
            price = product.price
        subtotal = price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    if request.method == 'POST':
        request.session['checkout_data'] = {
            'address': request.POST['address'],
            'pincode': request.POST['pincode'],
            'payment_method': request.POST['payment_method'],
            'cart': cart
        }

        payment_method = request.POST['payment_method']
        if payment_method == 'CARD':
            return redirect('fake_card_payment')
        elif payment_method == 'PHONEPE':
            return redirect('fake_phonepe')
        elif payment_method == 'GPAY':
            return redirect('fake_gpay')
        else:
            return redirect('process_order')

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

# Fake payment views
@login_required
def fake_card_payment(request):
    if request.method == 'POST':
        return redirect('process_order')
    return render(request, 'store/fake_card_payment.html')

@login_required
def fake_phonepe(request):
    if request.method == 'POST':
        return redirect('process_order')
    return render(request, 'store/fake_phonepe.html', {'method': 'PhonePe'})

@login_required
def fake_gpay(request):
    if request.method == 'POST':
        return redirect('process_order')
    return render(request, 'store/fake_gpay.html', {'method': 'Google Pay'})

# Final order processing
from datetime import timedelta

@login_required
def process_order(request):
    data = request.session.get('checkout_data')
    cart = data.get('cart', {})
    total = Decimal('0.00')
    cart_items = []

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        if product.is_offer:
            price = product.price * Decimal('0.75')
        else:
            price = product.price

        subtotal = price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal
        })

    # Create order
    order = Order.objects.create(
        user=request.user,
        address=data['address'],
        pincode=data['pincode'],
        total=total,
        payment_method=data['payment_method']
    )

    # Add items and update stock
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            price=item['price']
        )
        item['product'].quantity -= item['quantity']
        item['product'].save()

    # Prepare email product lines
    product_lines = "\n".join([
        f"- {item['product'].name} (Qty: {item['quantity']}, ₹{item['price']:.2f})"
        for item in cart_items
    ])

    # Estimated delivery date (today + 5 days)
    delivery_date = timezone.now().date() + timedelta(days=5)

    # Send confirmation email
    send_mail(
        'Your Order is Confirmed - ElectroShop',
        f"""Hi {request.user.first_name},

Thank you for choosing ElectroShop!

Your order has been successfully placed.

Order ID: #{order.id}
Items:
{product_lines}

Order Total: ₹{total:.2f}
Estimated Delivery: {delivery_date.strftime('%d %B %Y')}

Regards,
ElectroShop Team""",
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        fail_silently=False,
    )

    # Clear cart session
    request.session['cart'] = {}
    request.session.pop('checkout_data', None)

    return redirect('order_success')
# Order success page
def order_success(request):
    return render(request, 'store/order_success.html')

# View past orders
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

# View order detail
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()
    return render(request, 'store/order_detail.html', {
        'order': order,
        'items': items
    })

# Login view
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import LoginLog  # if you're using LoginLog model
from django.utils.timezone import now

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if username exists
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, f"Username '{username}' does not exist.")
            return render(request, 'store/login.html')

        # Now authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Save login log
            ip = get_client_ip(request)
            LoginLog.objects.create(user=user, ip_address=ip)

            messages.success(request, "Login successful!")
            return redirect(request.GET.get('next') or 'home')
        else:
            messages.error(request, "Invalid password!")
            return redirect(login)

    return render(request, 'store/login.html')
# Profile view
@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST['first_name']
        request.user.last_name = request.POST['last_name']
        request.user.email = request.POST['email']
        profile.mobile = request.POST['mobile']
        profile.address = request.POST['address']

        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']

        request.user.save()
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'store/profile.html', {'user': request.user, 'profile': profile})
