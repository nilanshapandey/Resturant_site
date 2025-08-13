from django.shortcuts import redirect, render, get_object_or_404
from .models import Restaurant, Dish, Category, Order, OrderItem, Customer
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import random
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import RegisterForm


from django.contrib.auth import login as auth_login  # ✅ Fix naming conflict




def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            auth_login(request, user)  # ✅ Use correct login
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})



@login_required
def order_history(request):
    customer = get_object_or_404(Customer, user=request.user)
    orders = Order.objects.filter(customer=customer).order_by('-ordered_on')
    return render(request, 'core/order_history.html', {'orders': orders})

def home(request):
    restaurants = Restaurant.objects.all()
    dishes = Dish.objects.all()
    categories = Category.objects.all()
    return render(request, 'core/home.html', {
        'restaurants': restaurants,
        'dishes': dishes,
        'categories': categories,
    })

def restaurant_menu(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    menu_items = Dish.objects.filter(restaurant=restaurant)

    cart = request.session.get('cart', {})

    if request.method == 'POST' and 'add_to_cart' in request.POST:
        item_id = request.POST['item_id']
        qty = int(request.POST.get('quantity', 1))
        if item_id in cart:
            cart[item_id] += qty
        else:
            cart[item_id] = qty
        request.session['cart'] = cart
        return redirect('core/restaurant_menu', pk=pk)

    cart_items = []
    total = 0
    for item_id, qty in cart.items():
        try:
            item = Dish.objects.get(pk=item_id)
            cart_items.append({
                'item': item,
                'qty': qty,
                'subtotal': item.price * qty
            })
            total += item.price * qty
        except:
            pass

    context = {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'cart_items': cart_items,
        'total': total,
        'otp_sent': request.session.get('otp_sent', False),
        'otp_verified': request.session.get('otp_verified', False)
    }
    return render(request, 'core/restaurant_menu.html', context)

@login_required
def send_otp(request):
    otp = str(random.randint(100000, 999999))
    request.session['otp'] = otp
    request.session['otp_sent'] = True
    send_mail('Your OTP', f'Your OTP is {otp}', settings.DEFAULT_FROM_EMAIL, [request.user.email])
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        correct_otp = request.session.get('otp')

        if entered_otp == correct_otp:
            request.session['otp_verified'] = True
            cart = request.session.get('cart', {})

            if not cart:
                messages.error(request, "Your cart is empty.")
                return redirect('home')

            customer, created = Customer.objects.get_or_create(user=request.user)
            order = Order.objects.create(customer=customer)

            for item_id, qty in cart.items():
                try:
                    dish = Dish.objects.get(pk=item_id)
                    OrderItem.objects.create(order=order, dish=dish, quantity=qty)
                except Dish.DoesNotExist:
                    continue

            request.session['cart'] = {}
            messages.success(request, "OTP Verified! Order placed successfully.")
            return redirect('home')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'verify_otp.html')

@csrf_exempt
def add_to_cart_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = str(data.get('item_id'))
        qty = int(data.get('quantity', 1))

        cart = request.session.get('cart', {})
        if item_id in cart:
            cart[item_id] += qty
        else:
            cart[item_id] = qty
        request.session['cart'] = cart

        total_items = sum(cart.values())
        return JsonResponse({'status': 'success', 'cart_count': total_items})

@login_required
def get_cart_count(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for item_id, qty in cart.items():
        try:
            dish = Dish.objects.get(pk=item_id)
            cart_items.append({'id': item_id, 'name': dish.name, 'price': dish.price, 'qty': qty})
            total += dish.price * qty
        except Dish.DoesNotExist:
            pass

    return JsonResponse({'cart': cart_items, 'total': total})

@login_required
def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        del cart[str(pk)]
        request.session['cart'] = cart
    return JsonResponse({'status': 'ok'})

def search(request):
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')

    restaurants = Restaurant.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )

    return render(request, 'core/home.html', {
        'restaurants': restaurants,
        'query': query,
        'selected_category': category,
    })

def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for item_id, qty in cart.items():
        try:
            dish = Dish.objects.get(pk=item_id)
            items.append({'dish': dish, 'qty': qty, 'subtotal': dish.price * qty})
            total += dish.price * qty
        except Dish.DoesNotExist:
            pass

    return render(request, 'core/cart.html', {'items': items, 'total': total})

def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        cart[str(pk)] += 1
    else:
        cart[str(pk)] = 1
    request.session['cart'] = cart
    return redirect('cart')



class CustomLoginView(LoginView):
    template_name = 'core/custom_login.html'

custom_login_view = CustomLoginView.as_view()