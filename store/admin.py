from django.contrib import admin

# Register your models here.
from .models import Color, Photo, Product, Size, Variation, VariationImages, Wishlist

class PhotoAdmin(admin.StackedInline):
    model = Photo
    list_display = ['product_name', 'product_slug']
    prepopulated_fields = {'photo_slug': ('product_image',),}

class ProductAdmin(admin.ModelAdmin):
    inlines = [PhotoAdmin]
    list_display = ['id', 'product_name', 'product_price', 'product_stock', 'is_active', 'updated',]
    prepopulated_fields = {'product_slug': ('product_name',),}
    class Meta:
        model = Product
    
class VariationImagesAdmin(admin.StackedInline):
    model = VariationImages
    list_display = ['color', 'size']
    prepopulated_fields = {'variation_image_slug': ('variation_image',),}

    # def subcategories(self, obj):
    #     return "  - ".join([sb.subcategory_name for sb in obj.product_subcategory.all()])
    
    

class VariationAdmin(admin.ModelAdmin):
    inlines = [VariationImagesAdmin]
    list_display = ('product', 'variation_number', 'color', 'size', 'is_available')
    list_editable = ('is_available',)
    list_filter = ('product', 'variation_number', 'color', 'size')
    
    class Meta:
        model : Variation
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']        

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Color)
admin.site.register(Size)
