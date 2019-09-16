from django.contrib import admin

# Register your models here.
from people.models import Position, Unit, Individual
from .forms import IndividualForm, PositionForm, UnitForm

#admin.site.register(Position)
#admin.site.register(Unit)
#admin.site.register(Individual)

        
        
class IndividualAdmin(admin.ModelAdmin):
    list_display = ('get_user', 
                    'person_position', 
                    'employee_id', 
                    'person_unit',
                    'group')
    list_filter = ('person_unit', 'person_position', 'group')
    exclude = ('accept_swap','group')    
    
    def get_user(self, indv):
        return indv.user.first_name+" "+indv.user.last_name
    get_user.admin_order_field = 'user'
    get_user.short_description = 'Name'
    
    form = IndividualForm
    
    def save_model(self, request, obj, form, change):
        obj.group = request.user.group
        super().save_model(request, obj, form, change)
        
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group=request.user.group)

#    def get_form(self, request, obj=None, **kwargs):
#        kwargs['user'] = request.user
#        return super().get_form(request, obj, **kwargs)
class PositionAdmin(admin.ModelAdmin):
    form = PositionForm
    exclude = ('group',)
    def save_model(self, request, obj, form, change):
        obj.group = request.user.group
        super().save_model(request, obj, form, change)
        
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group=request.user.group)
    
class UnitAdmin(admin.ModelAdmin):
    form = UnitForm
    exclude = ('group',)
    def save_model(self, request, obj, form, change):
        obj.group = request.user.group
        super().save_model(request, obj, form, change)
        
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group=request.user.group)
        
admin.site.register(Individual, IndividualAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Unit, UnitAdmin) 