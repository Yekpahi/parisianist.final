from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from store.models import Color, Photo, Product, Size, Variation, VariationImages, Wishlist
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string


def product_list(request, category_slug=None, product_slug=None):
    wishlisted_list = []
    if request.user.is_authenticated:
        wishlisted_list = list(Wishlist.objects.filter(user_id=request.user).values_list(
            'product_id', flat=True).order_by('product_id'))

    category = None
    products = None
    categories = Category.objects.all()
    # for printint only the parents
    parents = Category.objects.filter(parent=None)
    # End for printint only the parents

    # Start filter by product variation
    colors = Variation.objects.distinct().values(
        'color__name', 'color__id', 'color__colorCode')
    sizes = Variation.objects.distinct().values('size__size', 'size__id')
    # End filter by product variation

    # start Size color and filter
    SizeId = request.GET.get('sizeID')
    ColorId = request.GET.get('colorID')
    # End Size color and filter
    # Start sortby
    sort_by = request.GET.get("sort", "l2h")
    # End sortby
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        sub_categories = category.get_descendants(include_self=True)
        products = Product.objects.filter(category__in=sub_categories)
     # start Size color and filter
    elif SizeId:
        products = Product.objects.filter(
            variation__size__id__in=SizeId).distinct()
    elif ColorId:
        products = Product.objects.filter(
            variation__color__id__in=ColorId).distinct()
    # End Size color and filter
    # Start sortby
    elif sort_by == "l2h":
        products = Product.objects.filter(
            is_active=True).order_by('product_price')
    elif sort_by == "h2l":
        products = Product.objects.filter(
            is_active=True).order_by('-product_price')
    # end sort by
    # start Size color and filter
    else:
        products = Product.objects.all().filter(is_active=True)

    return render(request,
                  'store/store.html',
                  {'category': category,
                   'categories': categories,
                   'products': products,
                   'parents': parents,
                   # 'productx': productx,
                   'sizes': sizes,
                   'colors': colors,
                   'wishlisted_list': wishlisted_list
                   })

# product details
# def product_detail(request, category_slug, product_slug):
#     try:
#         single_product = Product.objects.get(category__slug=category_slug, product_slug=product_slug)
#         variations = Variation.objects.filter(product=single_product)
#         colors = Variation.objects.filter(product=single_product).values('color__id', 'color__name', 'color__colorCode').distinct()
#         sizes = Variation.objects.filter(product=single_product).values('size__id', 'size__size', 'color__id').distinct()
#           # if item is already in the cart
#         in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product)
#         # Créer un dictionnaire pour mapper chaque couleur à ses images correspondantes
#         variation_images_by_color = {}
#         for color in colors:
#             variation_images_by_color[color['color__id']] = {}
#             for variation in variations.filter(color_id=color['color__id']):
#                 variation_images_by_color[color['color__id']][variation.id] = VariationImages.objects.filter(variation=variation)

#     except Exception as e:
#         raise
#     context = {
#         'single_product': single_product,
#         'variations': variations,
#         'in_cart': in_cart,
#         'colors': colors,
#         'sizes': sizes,
#         'variation_images_by_color': variation_images_by_color,
#     }
#     return render(request, 'store/product_detail.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        # product=Product.objects.get(id=id)
        # Retrieve the single product instance
        single_product = Product.objects.get(
            category__slug=category_slug, product_slug=product_slug)
        # details images
        variations = Variation.objects.filter(product=single_product)
        # if item is already in the cart
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product)
        # colors and sizes
        colors = Variation.objects.filter(product=single_product).values(
            'color__id', 'color__name', 'color__colorCode').distinct()
        sizes = Variation.objects.filter(product=single_product).values(
            'size__id', 'size__size', 'color__id').distinct()

    except Exception as e:
        raise
    context = {
        'single_product': single_product,
        'variations': variations,
        'in_cart': in_cart,
        'colors': colors,
        'sizes': sizes,
        # 'data':product
    }
    return render(request, 'store/product_detail.html', context)

# filter data


def filter_data(request):
    colors = request.GET.getlist('color[]')
    sizes = request.GET.getlist('size[]')
    allProducts = Product.objects.all().order_by('-id').distinct()
    if len(colors) > 0:
        allProducts = allProducts.filter(
            variation__color__id__in=colors).distinct()
    if len(sizes) > 0:
        allProducts = allProducts.filter(
            variation__size__id__in=sizes).distinct()
    t = render_to_string('ajax/product-list.html', {'data': allProducts})
    return JsonResponse({'data': t})


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created').filter(
                Q(product_description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count
    }
    return render(request,  'store/store.html', context)


@login_required
# My Wishlist
def wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user).order_by('-id')
    context = {
        "wishlist": wishlist
    }
    return render(request, "account/dashboard/wishlist.html", context)


def toggle_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, product=product)
    if not created:
        # The product is already in the wishlist, so we remove it
        wishlist_item.delete()
        action = 'removed'
    else:
        action = 'added'

    # Count current items in the wishlist after action
    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return JsonResponse({'status': action, 'wishlist_count': wishlist_count})


def remove_from_wishlist(request):
    pid = request.GET['id']
    wishlist = Wishlist.objects.filter(user=request.user).count()
    wishlist_id = Wishlist.objects.get(id=pid)
    delete_product = wishlist_id.delete()
    context = {
        "bool": True,
        'wishlist': wishlist
    }

    t = render_to_string('store/async/wishlist_list.html', context)

    return JsonResponse({'data': t, 'all_wishlist': wishlist})
