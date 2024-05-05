
from django.urls import path
from main import views


urlpatterns = [
    path('', views.homepage, name='home'),
    path('about/', views.about, name= "about"),
    path('refund-policy/', views.refund, name= "refund"),
    path('terms-of-sales/', views.terms, name= "terms"),
    path('privacy-policy/', views.privacy, name= "privacy"),
    path('legal-notice/', views.legalNotice, name= "legalNotice"),
    path('shipping-policy/', views.shipping, name= "shipping"),
]
