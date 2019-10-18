from django.db import models
from django.contrib.auth.models import AbstractUser


class EmployeeID(models.Model):
    employee_id = models.IntegerField(primary_key=True,
                                      help_text='enter unique employee id')
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return self.employee_id


class CustomUser(AbstractUser):
    group = models.ForeignKey("Group",
                              on_delete=models.SET_NULL,
                              null=True)
    employee_detail = models.OneToOneField(EmployeeID,
                                           on_delete=models.CASCADE,
                                           null=True)

    def json_format(self):
        result = {'username': self.username,
                  'first_name': self.first_name,
                  'last_name': self.last_name,
                  'staff_status': self.is_staff,
                  'employee_id': self.employee_detail.employee_id}
        return result

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Group(models.Model):
    owner = models.ForeignKey(CustomUser,
                              on_delete=models.SET_NULL,
                              null=True,
                              related_name='group_owner')
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.name