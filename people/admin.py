from django.contrib import admin
from people.models import Position, Unit, Employee
from .forms import EmployeeForm, PositionForm, UnitForm


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_user',
                    'person_position',
                    'employee_id',
                    'person_unit',
                    'group')
    list_filter = ('person_unit', 'person_position', 'group')
    exclude = ('accept_swap', 'group')

    def get_user(self, indv):
        return indv.user.first_name + " " + indv.user.last_name

    get_user.admin_order_field = 'user'
    get_user.short_description = 'Name'

    form = EmployeeForm

    def save_model(self, request, obj, form, change):
        obj.group = request.user.group
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group=request.user.group)


class PositionAdmin(admin.ModelAdmin):
    form = PositionForm
    list_display = ('position_choice', 'group')
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
    list_display = ('unit_choice', 'group')
    exclude = ('group',)

    def save_model(self, request, obj, form, change):
        obj.group = request.user.group
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group=request.user.group)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Unit, UnitAdmin)