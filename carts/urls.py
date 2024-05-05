from django.urls import include, path
from carts import views
urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('increment_quantity/<int:product_id>/', views.increment_quantity, name='increment_quantity'),

    # path('delete-from-cart',views.delete_cart_item,name='delete_from_cart'),
    # path('update-cart',views.update_cart_item,name='update_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('checkout/', views.checkout, name ="checkout"),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_canceled, name='payment_cancelled'),
]
