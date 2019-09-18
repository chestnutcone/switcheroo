from django.contrib import admin
from schedule.models import Shift, Schedule


class ShiftAdmin(admin.ModelAdmin):
    list_display = ('shift_name',
                    'shift_start',
                    'shift_duration',
                    )
    exclude = ('group',)

    def save_model(self, request, obj, form, change):
        obj.group = request.user.group
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group=request.user.group)


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('schedule_name',
                    'day_1',
                    'day_2',
                    'day_3',
                    )
    exclude = ('group',)

    def save_model(self, request, obj, form, change):
        obj.group = request.user.group
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(group=request.user.group)


admin.site.register(Shift, ShiftAdmin)
admin.site.register(Schedule, ScheduleAdmin)