from django.shortcuts import redirect, render
from store.models import Product


def homepage(request):
    products = Product.objects.all()[0:5]
    context = {
        'products': products,
        
}
    return render(request, "main/home.html", context)

def about(request):
    return render(request, "main/about.html")

def privacy(request):
    return render(request, "main/privacy.html")

def terms(request):
    return render(request, "main/terms.html")

def legalNotice(request):
    return render(request, "main/legalNotice.html")

def refund(request):
    return render(request, "main/refund.html")
def shipping(request):
    return render(request, "main/shipping.html")
