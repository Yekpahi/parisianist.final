from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from account.models import Account, UserProfile

class AccountAdmin(UserAdmin) :
     list_display = ['first_name', 'last_name', 'username',  'email', 'last_login', 'date_joined', 'is_active', 'is_admin', 'is_staff', 'is_superuser']
     list_display_links = ('email', 'first_name', 'last_name')
     readonly_fiels = ('last_login', 'date_joined')
     ordering = ('-date_joined',)
     
     filter_horizontal = ()
     list_filter = ()
     fieldsets = ()
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'country')
    
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)