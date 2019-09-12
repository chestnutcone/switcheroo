from django.contrib import admin

# Register your models here.
from people.models import Position, Unit, Individual


admin.site.register(Position)
admin.site.register(Unit)

#admin.site.register(Individual)

class IndividualAdmin(admin.ModelAdmin):
    list_display = ('get_user', 
                    'person_position', 
                    'employee_id', 
                    'person_unit')
    list_filter = ('person_unit', 'person_position')
    exclude = ('accept_swap',)    
    
    def get_user(self, indv):
        return indv.user.first_name+" "+indv.user.last_name
    get_user.admin_order_field = 'user'
    get_user.short_description = 'Name'
admin.site.register(Individual, IndividualAdmin)
