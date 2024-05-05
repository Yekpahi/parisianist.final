from django.contrib import admin
from category.models import Category
from mptt.admin import DraggableMPTTAdmin


admin.site.register(
    Category,
    DraggableMPTTAdmin,
    list_display=(
        'parent',
        'name',
        # ...more fields if you feel like it...
    ),
    list_display_links=(
        'name',
    ),
    prepopulated_fields = {'slug': ('name',),}
)
