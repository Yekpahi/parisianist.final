from django.db import models

from store.models import Product, Variation
from account.models import Account

# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=200, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id
    def get_items(self):
        return CartItem.objects.filter(cart=self)


class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def sub_total(self):
        self.sub_total = round((self.product.product_price + (self.product.product_price*20/100)) * self.quantity, 2)
        return self.sub_total
    
    def __str__(self):
        return self.product.product_name
    