from django.db import models
from django.contrib.auth import get_user_model
from user.models import *


class Position(models.Model):
    """This will be a list of positions that employees will occupy
    """
    position_choice = models.CharField(max_length=50)
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)

    def json_format(self):
        result = {'position_name': self.position_choice,
                  'pk': self.pk}
        return result

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

    def json_format(self):
        result = {'unit_name': self.unit_choice,
                  'pk': self.pk}
        return result

    def __str__(self):
        return self.unit_choice


class Workday(models.Model):
    name = models.CharField(max_length=5)
    day = models.PositiveSmallIntegerField(primary_key=True)
    # 0 = monday, 6 = sunday etc

    def json_format(self):
        result = {'workday_name': self.name,
                  'pk': self.day}
        return result

    @staticmethod
    def _set_workday():
        if not Workday.objects.filter(pk=6).exists():
            weekdays = ['Mon','Tues','Wed','Thurs', 'Fri', 'Sat','Sun']
            for day, name in enumerate(weekdays):
                weekday, created = Workday.objects.get_or_create(name=name, day=day)
                weekday.save()

    def __str__(self):
        return self.name


# execute to ensure the weekday objects exist. Need to find out how to register once only.
# Weekday._set_workday()


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
    workday = models.ManyToManyField(Workday,
                                     blank=True,
                                     help_text="availability")
    date_joined = models.DateField()

    def json_format(self):
        workday_q = self.workday.all().order_by('pk')
        workday_preference = [w.name for w in workday_q]
        result = {'first_name': str(self.user.first_name),
                  'last_name': str(self.user.last_name),
                  'unit': str(self.person_unit),
                  'position': str(self.person_position),
                  'employee_id': str(self.user.employee_detail.employee_id),
                  'workday_preference': workday_preference}
        return result

    @staticmethod
    def get_employee_instance(employee_id):
        employee_id = int(employee_id)
        employee_detail = EmployeeID.objects.get(pk=employee_id)
        employee_user = CustomUser.objects.get(employee_detail=employee_detail)
        employee = Employee.objects.get(user=employee_user)
        return employee

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
