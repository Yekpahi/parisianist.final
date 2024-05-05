
from category.models import Category


def catmenu_links(request, category_slug=None):
    
    return {
        'catlinks': Category.objects.all(),
        'cat_parents':  Category.objects.filter(parent=None)
    }