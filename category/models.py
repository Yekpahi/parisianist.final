from django.db import models
from django.urls import reverse
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length= 100, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(max_length=200, blank = True)
    cat_image = models.ImageField(upload_to='static/category/', blank = True, null=True)
    cat_header_image = models.ImageField(upload_to='static/category/header', blank = True, null=True)

    class MPTTMeta:
       order_insertion_by = ['name']

    class Meta:
        ordering = ('name',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def get_absolute_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.name
    
       