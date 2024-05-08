import json
from django.urls import reverse
import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseServerError, JsonResponse
from django.shortcuts import render
import datetime
from django.shortcuts import render, redirect
from carts.models import Cart, CartItem
from store.models import Product
from .forms import OrderForm
from .models import Order, OrderProduct, Payment
from django.contrib.gis.geoip2 import GeoIP2
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.mail import send_mail
import stripe
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from account.models import Account
import paypalrestsdk


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)


@login_required(login_url="login")
@csrf_exempt
def stripe_payment(request):
    if request.method == 'GET':
        domain_url = getattr(settings, 'DOMAIN_URL')
        success_url = domain_url + \
            reverse('stripe_success') + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = domain_url + reverse('stripe_cancel')
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Récupérer le paramètre `order_id`
        order_id = request.GET.get('order_id')

        try:
            # Créez ou récupérez la commande en utilisant l'`order_number`
            order = Order.objects.get(
                user=request.user, is_ordered=False, order_number=order_id)
            line_items = []

            # Récupérez les produits de la commande
            order_products = order.orderproduct_set.all()

            # Parcourez chaque produit de la commande pour créer les éléments de ligne
            for order_product in order_products:
                line_items = {
                    'price_data': {
                        'currency': 'eur',
                        'unit_amount': int(order_product.product_price * 100),
                        'product_data': {
                            'name': order_product.product.product_name,  # Utilisez le vrai nom du produit
                        },
                    },
                    'quantity': order_product.quantity,  # Utilisez la quantité réelle du produit
                }
            line_items.append(line_items)
            # Créez une nouvelle session de paiement Stripe
          # Créez une nouvelle session de paiement Stripe en utilisant les éléments de ligne
            checkout_session = stripe.checkout.Session.create(
                success_url=success_url,
                cancel_url=cancel_url,
                payment_method_types=['card'],
                mode='payment',
                # Utilisez les éléments de ligne créés à partir des produits de la commande
                line_items=line_items
            )

            # # Mettez à jour les éléments de la ligne avec les vrais produits
            # checkout_session.update({
            #     'line_items': line_items
            # })

            # Générez un numéro de commande unique
            order.order_number = str(uuid.uuid4()).replace('-', '')[:20]

            # Créez un nouvel objet Payment associé à la commande
            payment = Payment.objects.create(
                user=request.user,
                payment_id=checkout_session['id'],
                payment_method='Card',
                amount_paid=order.order_total,
                status='Completed'
            )
            payment.save()

            # Associez le paiement à la commande et marquez-la comme commandée
            order.payment = payment
            order.is_ordered = True
            order.save()

            # Move the cart items to Order Product table
            cart_items = CartItem.objects.filter(user=request.user)

            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payment
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.product.product_price
                orderproduct.ordered = True
                orderproduct.save()

                cart_item = CartItem.objects.get(id=item.id)
                product_variation = cart_item.variations.all()
                orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variations.set(product_variation)
                orderproduct.save()

                # Reduce the quantity of the sold products
                product = Product.objects.get(id=item.product_id)
                product.product_stock -= item.quantity
                product.save()

            # Clear cart
            CartItem.objects.filter(user=request.user).delete()

            # Send order received email to customer
            mail_subject = 'Thank you for your order!'
            message = render_to_string('orders/order_received_email.html', {
                'user': request.user,
                'order': order,
            })
            to_email = order.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # Send order number and transaction id back to sendData method via JsonResponse
            data = {
                'order_number': order.order_number,
                'transID': payment.payment_id,
                'sessionId': checkout_session['id']
            }

            # Autres actions...
            return JsonResponse(data)
        except Exception as e:
            # Retournez une réponse JSON avec l'erreur et un statut 500 en cas d'erreur
            return JsonResponse({'error': str(e)}, status=500)


def stripe_success(request):
    return render(request, 'orders/stripe_success.html')


def stripe_cancel(request):
    return render(request, 'orders/stripe_cancel.html')


@login_required(login_url="login")
def stripe_paymentsss(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            # Créez ou récupérez la commande
            orders = Order.objects.filter(user=request.user, is_ordered=False)

            for order in orders:    # Créez une nouvelle session de paiement Stripe

                checkout_session = stripe.checkout.Session.create(
                    success_url=domain_url +
                    'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url + 'stripe_cancel/',
                    payment_method_types=['card'],
                    mode='payment',
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'unit_amount': int(order.order_total * 100),
                                'product_data': {
                                    'name': 'T-shirt',  # Nom par défaut, sera remplacé ci-dessous
                                },
                            },
                            'quantity': 1,
                        }
                    ]
                )

                # Récupérez les produits de la commande
                order_products = order.orderproduct_set.all()
                line_items = []

                for order_product in order_products:
                    line_item = {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(order_product.product_price * 100),
                            'product_data': {
                                'name': order_product.product.product_name,  # Utilisez le vrai nom du produit
                            },
                        },
                        'quantity': order_product.quantity,
                    }
                    line_items.append(line_item)

                # Mettez à jour les éléments de la ligne avec les vrais produits
                checkout_session.update({
                    'line_items': line_items
                })

                # Générez un numéro de commande unique
                order.order_number = str(uuid.uuid4()).replace('-', '')[:20]

                # Créez un nouvel objet Payment associé à la commande
                payment = Payment.objects.create(
                    user=request.user,
                    payment_id=checkout_session['id'],
                    payment_method='Card',
                    amount_paid=order.order_total,
                    status='Completed'
                )
                payment.save()

                # Associez le paiement à la commande et marquez-la comme commandée
                order.payment = payment
                order.is_ordered = True
                order.save()

                # Enregistrez la commande dans la base de données
                order.save()
                # Move the cart items to Order Product table
                cart_items = CartItem.objects.filter(user=request.user)

                for item in cart_items:
                    orderproduct = OrderProduct()
                    orderproduct.order_id = order.id
                    orderproduct.payment = payment
                    orderproduct.user_id = request.user.id
                    orderproduct.product_id = item.product_id
                    orderproduct.quantity = item.quantity
                    orderproduct.product_price = item.product.product_price
                    orderproduct.ordered = True
                    orderproduct.save()

                    cart_item = CartItem.objects.get(id=item.id)
                    product_variation = cart_item.variations.all()
                    orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                    orderproduct.variations.set(product_variation)
                    orderproduct.save()

                    # Reduce the quantity of the sold products
                    product = Product.objects.get(id=item.product_id)
                    product.product_stock -= item.quantity
                    product.save()

                # Clear cart
                CartItem.objects.filter(user=request.user).delete()
                # Send order received email to customer
                mail_subject = 'Thank you for your order!'
                message = render_to_string('orders/order_received_email.html', {
                    'user': request.user,
                    'order': order,
                })
                to_email = request.user.email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()

                # Send order number and transaction id back to sendData method via JsonResponse
                data = {
                    'order_number': order.order_number,
                    'transID': payment.payment_id,
                    'sessionId': checkout_session['id']
                }

                # Autres actions...
                return JsonResponse(data)

        except Exception as e:
            # Retournez une réponse JSON avec l'erreur et un statut 500 en cas d'erreur
            return JsonResponse({'error': str(e)}, status=500)
# Stripe payment
# Stripe payment


# payments/views.py


@csrf_exempt
@login_required(login_url="login")
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here

    return HttpResponse(status=200)


paypalrestsdk.configure({
    "mode": "sandbox",  # Changez en "live" en mode de production
    "client_id": settings.STRIPE_SECRET_KEY,
    "client_secret": settings.STRIPE_SECRET_KEY
})


@csrf_exempt
def paypal_payment(request):
    body = json.loads(request.body)
    current_user = request.user if not isinstance(
        request.user, AnonymousUser) else None
    order = Order.objects.get(
        user=current_user, is_ordered=False, order_number=body['orderID'])
    # If user is anonymous, create a temporary user object

    if current_user is None:
        # Generate a unique identifier for the username
        # Use a portion of the UUID as a username
        username = f"AnonymousUser_{uuid.uuid4().hex[:10]}"
        first_name = order.first_name
        last_name = order.last_name

        anonymousEmail = order.email
        current_user = Account.objects.create(
            username=username, email=anonymousEmail, first_name=first_name, last_name=last_name)
    # Store transaction details inside Payment model
    payment = Payment(
        user=current_user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=current_user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.product_price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.product_stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=current_user).delete()

    # Send order received email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': current_user,
        'order': order,
    })
    to_email = order.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def paypal_success(request):
    return render(request, 'orders/stripe_success.html')


def paypal_cancel(request):
    return render(request, 'orders/stripe_cancel.html')
# Orders


def place_order(request, total=0, quantity=0):

    pub_key = settings.STRIPE_PUBLIC_KEY
    current_user = request.user if not isinstance(
        request.user, AnonymousUser) else None
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    grand_total_dhl = 0
    taxdhl = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.product_price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (20 * total) / 100
    taxdhl = 1
    grand_total = round((total + tax), 2)
    grand_total_dhl += grand_total + taxdhl

    # Only for local
    if settings.DEBUG:
        # Utilisation de l'API ipify pour obtenir une adresse IP publique
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            ip_data = response.json()
            user_ip = ip_data.get('ip')
        else:
            # Fallback à une adresse IP locale si l'appel à l'API échoue
            user_ip = '127.0.0.1'
    else:
        user_ip = request.META.get('REMOTE_ADDR')

    g = GeoIP2()
    user_country = None
    try:
        user_country = g.country_code(user_ip)
    except Exception as e:
        print("Error determining user location:", e)

    if request.method == 'POST':
        orderform = OrderForm(request.POST, user_country=user_country)
        if orderform.is_valid():
            # data = Order()
            data = orderform.save(commit=False)
            data.first_name = orderform.cleaned_data['first_name']
            data.last_name = orderform.cleaned_data['last_name']
            data.zip_code = orderform.cleaned_data['zip_code']
            data.phone = orderform.cleaned_data['phone']
            data.email = orderform.cleaned_data['email']
            if current_user is None or current_user.is_anonymous:
                # Redirect to login if the user is anonymous and tries to pay with a card
                if orderform.cleaned_data['payment_method'] == "Card":
                    return redirect('login')  # Redirect to your login URL

                # Vérifiez si l'utilisateur anonyme existe dans la session
                anonymous_username = f"AnonymousUsername_{uuid.uuid4().hex[:10]}"
                anonymous_first_name = data.first_name
                anonymous_last_name = data.last_name
                anonymous_email = f"AnonymousMail_{uuid.uuid4().hex[:10]}"

                # Utilisez les détails de l'utilisateur anonyme s'ils existent
                if anonymous_username and anonymous_email:
                    current_user = Account.objects.create(
                        username=anonymous_username, email=anonymous_email, first_name=anonymous_first_name, last_name=anonymous_last_name)
                    data.user = current_user

            data.user = current_user
            data.address_line_1 = orderform.cleaned_data['address_line_1']
            data.address_line_2 = orderform.cleaned_data['address_line_2']
            data.postcode = orderform.cleaned_data['postcode']
            data.country = orderform.cleaned_data['country']
            data.city = orderform.cleaned_data['city']
            payment_method = orderform.cleaned_data.get('payment_method')
            data.delivery_method = orderform.cleaned_data['delivery_method']
            # data.payment_method = orderform.cleaned_data['payment_method']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            # Utilisez une adresse IP spécifique pour simuler la localisation

            # Déterminer le service de livraison en fonction de la localisation de l'utilisateur
            # user_ip = request.META.get('REMOTE_ADDR')
            # g = GeoIP2()
            # try:
            #     user_country = g.country_code(user_ip)
            #     print(user_country)
            #     if user_country == 'FR':
            #         orderform.fields['delivery_method'].initial = 'Colissimo'
            #     else:
            #         orderform.fields['delivery_method'].initial = 'DHL'
            # except Exception as e:
            #     print("Error determining user location:", e)

            data.save()

            # if payment_method == "Card":
            #     return redirect('stripe_payment')

            # elif  payment_method == "Paypal":
            #     return redirect('paypal_payment')
            # else :
            #     pass

            yr = int(datetime.date.today().strftime('%y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y-%m-%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number)

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'taxdhl': taxdhl,
                'grand_total': grand_total,
                'grand_total_dhl': grand_total_dhl,
                'pub_key': pub_key
            }
            if payment_method == "Card":
                return render(request, 'orders/stripe_payments.html', context)
            if payment_method == "Paypal":
                return render(request, 'orders/payments.html', context)

    else:
        orderform = OrderForm(user_country=user_country)

    context = {
        'orderform': orderform,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'taxdhl': taxdhl,
        'grand_total': grand_total,
        'grand_total_dhl': grand_total_dhl
    }
    return render(request, 'orders/place_order.html', context)


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        tax = 0
        taxdhl = 0
        grand_total = 0
        grand_total_dhl = 0

        for i in ordered_products:
            subtotal += i.product_price * i.quantity
            tax += (2*subtotal)/100
            taxdhl = 1
            grand_total += subtotal + tax
            grand_total_dhl += grand_total + taxdhl

        payment = Payment.objects.get(payment_id=transID)
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'tax': tax,
            'taxdhl': taxdhl,
            'grand_total': grand_total,
            'grand_total_dhl': grand_total_dhl
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('order_complete')
