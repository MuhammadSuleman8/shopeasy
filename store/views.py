from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product, Category, Cart, CartItem, Order, OrderItem

def home(request):
    products = Product.objects.all()[:8]
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'products': products, 'categories': categories})

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    return render(request, 'store/product_list.html', {'products': products, 'categories': categories})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def cart(request):
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    items = cart_obj.cartitem_set.all()
    total = cart_obj.get_total()
    return render(request, 'store/cart.html', {'cart': cart_obj, 'items': items, 'total': total})

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart_obj, created = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product)
    if not created:
        item.quantity += 1
        item.save()
    messages.success(request, f'{product.name} cart mein add ho gaya!')
    return redirect('cart')

@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk)
    item.delete()
    return redirect('cart')

@login_required
def place_order(request):
    cart_obj = get_object_or_404(Cart, user=request.user)
    items = cart_obj.cartitem_set.all()
    if request.method == 'POST':
        address = request.POST['address']
        total = cart_obj.get_total()
        order = Order.objects.create(user=request.user, total_price=total, address=address)
        for item in items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
        items.delete()
        messages.success(request, 'Order place ho gaya!')
        return redirect('order_history')
    return render(request, 'store/place_order.html', {'cart': cart_obj, 'items': items, 'total': cart_obj.get_total()})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'store/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Username ya password galat hai!')
    return render(request, 'store/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')