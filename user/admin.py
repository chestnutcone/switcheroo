from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email','first_name', 'last_name','is_staff', 'get_group']
#
    def get_group(self, user):
        try:
            output = user.group.id
        except AttributeError:
            output = 'N/A'
        return output
    get_group.admin_order_field = 'group'
    get_group.short_description = 'Group ID'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group=request.user.group)
admin.site.register(CustomUser, CustomUserAdmin)