
from orders.models import Order, OrderProduct


def order_details_context(request):
    # Récupérer l'ID de la commande à partir de la requête
    order_id = request.GET.get('order_id')

    # Si order_id est None ou une chaîne vide, retourner un dictionnaire vide
    if not order_id:
        return {}

    # Récupérer les détails de la commande et calculer le subtotal
    order_details_email = OrderProduct.objects.filter(order__order_number=order_id)
    subtotal = sum(item.product_price * item.quantity for item in order_details_email)

    # Retourner un dictionnaire contenant les données de la commande
    return {
        'order_detail_email': order_details_email,
        'order': Order.objects.get(order_number=order_id),
        'subtotal': subtotal,
    }