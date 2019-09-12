from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

class Position(models.Model):
    position_choice = models.CharField(max_length=50)
    def __str__(self):
        return self.position_choice
    
class Unit(models.Model):
    unit_choice = models.CharField(max_length=50)
    def __str__(self):
        return self.unit_choice
    
#class ScheduleDict(models.Model):
#    employee_id = models.IntegerField(primary_key=True,
#                                      help_text='enter employee id to queue')
#    
#class KeyVal(models.Model):
#    container = models.ForeignKey(ScheduleDict, db_index=True)
    
    
class Individual(models.Model):
    
    user = models.OneToOneField(get_user_model(),
                               on_delete=models.CASCADE,
                               unique=True)
    employee_id = models.IntegerField(primary_key=True, 
                                      help_text='enter unique employee id')
    
    person_position = models.ForeignKey(Position, 
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        help_text='select a position')
    person_unit = models.ForeignKey(Unit, 
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    help_text='select a unit')
    # available for swap even if they're not currently swapping
    # aka available for accepting shifts
    accept_swap = models.BooleanField(default=False)

    
    def get_info(self):
        print('   ')
        print('printing all info.....')
        print('name', self.user.first_name, self.user.last_name)
        print('email', self.user.email)
        print('id', self.employee_id)
        print('position', self.person_position)
        print('unit', self.person_unit)
        print('accept shifts', self.accept_swap)
        
    
    def __str__(self):
        return self.user.first_name+" "+self.user.last_name