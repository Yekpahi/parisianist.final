from django.urls import path
from store import views


urlpatterns = [
    path('', views.product_list, name='store'),
    # path(r'^categories/$', views.product_list, name = "products_by_category"),
    path('category/<slug:category_slug>/',
         views.product_list, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name="product_detail"),
    path('filter-data', views.filter_data, name='filter_data'),
    path('search/', views.search, name='search'),
    path("wishlist/", views.wishlist, name="wishlist"),
    path('toggle-wishlist/', views.toggle_wishlist, name='toggle-wishlist'),    
    path('remove-from-wishlist/', views.remove_from_wishlist, name="remove_from_wishlist")
]
