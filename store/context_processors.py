from stripe import Product
from store.models import Variation, Wishlist
from django.contrib import messages


def get_filters(request):
    colors = Variation.objects.distinct().values('color__name', 'color__id', 'color__colorCode')
    sizes = Variation.objects.distinct().values('size__size', 'size__id')
    data = {
        'colors': colors,
        'sizes':sizes,
    }
    return data

def wishlist_context(request):
    try:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()    

        # wishlist= Wishlist.objects.filter(user=request.user)
    except:
        messages.warning(request, "You need to login before accessing your your wishlist.")
        wishlist_count=0
    return {
        # 'wishlist' : wishlist,
        'wishlist_count':wishlist_count
        
    }
    