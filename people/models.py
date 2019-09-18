from django.db import models
from django.contrib.auth import get_user_model
from user.models import Group


class Position(models.Model):
    """This will be a list of positions that employees will occupy
    """
    position_choice = models.CharField(max_length=50)
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)

    def __str__(self):
        return self.position_choice


class Unit(models.Model):
    """This will be a list of units that employees will occupy
    """
    unit_choice = models.CharField(max_length=50)
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)

    def __str__(self):
        return self.unit_choice


class Employee(models.Model):
    """Employee will have one to one relationship with users. Each employee
    instance must have a user to be defined first. Which means employee should
    be registered as users before admin can assign them to roles.
    
    Employee ID is used as primary key, which means it must be unique and 
    not empty, since it is used to fetch the object
    
    Purpose of Employee is to assign each user to a role 
    
    accept_swap is for the person to choose whether or not to accept shifts 
    even when they are not activing requesting swaps. This will be controlled
    by the employee and not the admin
    """
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

    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)

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
        return self.user.first_name + " " + self.user.last_name