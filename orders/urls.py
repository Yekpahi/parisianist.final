from django.urls import path
from orders import views


urlpatterns = [
path('place_order/', views.place_order, name='place_order'),
path('paypal_payment/', views.paypal_payment, name='paypal_payment'),
path('stripe_payment/', views.stripe_payment, name='stripe_payment'),

path('stripe_success/', views.stripe_success, name='stripe_success'),
path('stripe_cancel/', views.stripe_cancel, name='stripe_cancel'),
path('paypal_success/', views.stripe_success, name='paypal_success'),
path('paypal_cancel/', views.stripe_cancel, name='paypal_cancel'),
path('webhook/', views.stripe_webhook, name="webhook"), # new
path('config/', views.stripe_config, name="config"),

#    path('paypal_payment/<payment_method>/', views.paypal_payment, name='paypal_payment'),
path('order_complete/', views.order_complete, name='order_complete'),
    # path('stripe-payment/', views.stripe_payment, name='stripe_payment'),
    # path('paypal-payment/', views.paypal_payment, name='paypal_payment'),
]