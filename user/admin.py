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
    list_display = ['first_name', 'last_name','email', 'username', 'get_session']
#
    def get_session(self, user):
        try:
            output = user.session.id
        except AttributeError:
            output = 'N/A'
        return output
    get_session.admin_order_field = 'session'
    get_session.short_description = 'Session ID'
admin.site.register(CustomUser, CustomUserAdmin)