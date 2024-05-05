from django.db import models
from account.models import Account
from store.models import Product, Variation
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Refunding', 'Refunding'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    DELIVERY_METHOD = (
        ("DHL", "DHL"),
        ("Colissimo", "Colissimo"),
    )

    PAYMENT_METHOD = (
        ("Card", "Card"),
        ("Paypal", "Paypal"),
    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    # Existing fields...
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    # Add this line
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=50)
    postcode = models.CharField(max_length=50)
    order_total = models.FloatField()
    tax = models.FloatField()
    payment_intent = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    delivery_method = models.CharField(
        max_length=10, choices=DELIVERY_METHOD)
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD, default='Card')
    ip = models.CharField(max_length=20, blank=True)
    is_ordered = models.BooleanField(default=False)
    paid_amount = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name
 
    #Send message to user when the colis is delivered
    def save(self, *args, **kwargs):
        # Déterminer si c'est une mise à jour et obtenir l'ancien statut
        if self.pk:
            old_status = Order.objects.get(pk=self.pk).status
        else:
            old_status = None

        super().save(*args, **kwargs)

        # Envoyer un email si le statut passe à 'Shipped'
        if old_status != 'Shipped' and self.status == 'Shipped' and self.tracking_number:
            subject = 'Votre commande a été expédiée'
            message = render_to_string(
                'orders/emails/shipment_email.html', {'order': self})
            send_mail(subject, '', settings.DEFAULT_FROM_EMAIL,
                      [self.email], html_message=message)
            print(message)
        if old_status != 'Completed' and self.status == 'Completed' and self.tracking_number:
            subject = 'Votre commande a été livré'
            message = render_to_string(
                'orders/emails/delivery_confirmed_email.html', {'order': self})
            send_mail(subject, '', settings.DEFAULT_FROM_EMAIL,
                      [self.email], html_message=message)
            print(message)
        # Ajuster la méthode de livraison pour les commandes en France
        
       
        if self.country == 'France' and not self.pk:
            self.delivery_method = 'Colissimo'
            super().save(update_fields=['delivery_method'])


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
