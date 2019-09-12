from django.contrib import admin

# Register your models here.
from schedule.models import Shift
from schedule.models import Schedule

#admin.site.register(Shift)
#admin.site.register(Schedule)

class ShiftAdmin(admin.ModelAdmin):
    list_display = ('shift_name',
                    'shift_start', 
                    'shift_duration', 
                    )
    
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('schedule_name',
                    'day_1', 
                    'day_2',
                    'day_3',
                    )
    

admin.site.register(Shift, ShiftAdmin)
admin.site.register(Schedule, ScheduleAdmin)