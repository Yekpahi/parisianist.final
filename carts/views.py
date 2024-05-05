import uuid
from django.shortcuts import get_object_or_404, render, redirect
from account.models import Account
from carts.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from store.models import Color, Product, Size, Variation
# paypal
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import orders
from orders.forms import OrderForm
from django.contrib import messages
from django.db.models import Sum


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_to_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    # Assuming 'category' is a related model and has a 'slug' field
    category_slug = product.category.slug
    # Assuming 'product' model has a 'slug' field
    product_slug = product.product_slug
    # If the user is not authentificated
    if current_user.is_authenticated:
        size_id = request.POST.get('size')
        color_id = request.POST.get('color')
        size = get_object_or_404(Size, id=size_id)
        color = get_object_or_404(Color, id=color_id)
        variation = Variation.objects.get(
            product=product, color=color, size=size)

        total_ordered = CartItem.objects.filter(variations=variation).aggregate(
            Sum('quantity'))['quantity__sum'] or 0

        if total_ordered >= variation.variation_number:
            messages.error(
                request, "Ce produit n'est pas disponible dans la variation sélectionnée.", extra_tags='cart_error')
            return redirect('product_detail', category_slug=category_slug, product_slug=product_slug)

        cart_item = CartItem.objects.filter(
            user=current_user, product=product, variations=variation).first()

        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                user=current_user, product=product, quantity=1)
            cart_item.variations.add(variation)

        messages.success(
            request, "Le produit a été ajouté à votre panier.", extra_tags='cart_success')
        return redirect('product_detail', category_slug=category_slug, product_slug=product_slug)

        # If the user is not authentificated

    else:
        size_id = request.POST.get('size')
        color_id = request.POST.get('color')
        size = get_object_or_404(Size, id=size_id)
        color = get_object_or_404(Color, id=color_id)
        variation = Variation.objects.get(
            product=product, color=color, size=size)

        total_ordered = CartItem.objects.filter(variations=variation).aggregate(
            Sum('quantity'))['quantity__sum'] or 0

        if total_ordered >= variation.variation_number:
            messages.error(
                request, "Ce produit n'est pas disponible dans la variation sélectionnée.", extra_tags='cart_error')
            return redirect('product_detail', category_slug=category_slug, product_slug=product_slug)
        try:
            # get the cart using the cart_id present in the session
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        cart_item = CartItem.objects.filter(
            product=product, cart=cart, variations=variation).first()

        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product, cart=cart, quantity=1)
            cart_item.variations.add(variation)

        messages.success(
            request, "Le produit a été ajouté à votre panier.", extra_tags='cart_success')
        return redirect('product_detail', category_slug=category_slug, product_slug=product_slug)


def increment_quantity(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    # If the user is  authentificated

    if current_user.is_authenticated:
        size_id = request.POST.get('size')
        color_id = request.POST.get('color')
        size = get_object_or_404(Size, id=size_id)
        color = get_object_or_404(Color, id=color_id)
        variation = Variation.objects.get(
            product=product, color=color, size=size)

        total_ordered = CartItem.objects.filter(variations=variation).aggregate(
            Sum('quantity'))['quantity__sum'] or 0

        if total_ordered >= variation.variation_number:
            messages.error(
                request, "Ce produit n'est pas disponible dans la variation sélectionnée.", extra_tags='cart_error')
            return redirect('cart')

        cart_item = CartItem.objects.filter(
            user=current_user, product=product, variations=variation).first()

        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                user=current_user, product=product, quantity=1)
            cart_item.variations.add(variation)

        messages.success(
            request, "Le produit a été ajouté à votre panier.", extra_tags='cart_success')
        return redirect('cart')
    # If the user is not authentificated
    else:
        size_id = request.POST.get('size')
        color_id = request.POST.get('color')
        size = get_object_or_404(Size, id=size_id)
        color = get_object_or_404(Color, id=color_id)
        variation = Variation.objects.get(
            product=product, color=color, size=size)

        total_ordered = CartItem.objects.filter(variations=variation).aggregate(
            Sum('quantity'))['quantity__sum'] or 0

        if total_ordered >= variation.variation_number:
            messages.error(
                request, "Ce produit n'est pas disponible dans la variation sélectionnée.", extra_tags='cart_error')
            return redirect('cart')
        try:
            # get the cart using the cart_id present in the session
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()
        cart_item = CartItem.objects.filter(
            cart=cart, product=product, variations=variation).first()

        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                cart=cart, product=product, quantity=1)
            cart_item.variations.add(variation)

        messages.success(
            request, "Le produit a été ajouté à votre panier.", extra_tags='cart_success')
        return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(
                product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

# Remove a Item


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
            product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.product_price*cart_item.quantity)
            quantity += cart_item.quantity
        tax = (20*total)/100
        grand_total = round((total + tax), 2)

    except ObjectDoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'cart/cart.html', context)


def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        # cart = Cart.objects.get(cart_id=_cart_id(request))
        # cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.product_price*cart_item.quantity)
            quantity += cart_item.quantity
        tax = (20*total)/100
        grand_total = round((total + tax), 2)

    except ObjectDoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, 'checkout/checkout.html', context)


@csrf_exempt
def payment_done(request):
    returnData = request.POST
    return render(request, 'payment_success.html', {'data': returnData})


@csrf_exempt
def payment_canceled(request):
    return render(request, 'payment_fail.html')
