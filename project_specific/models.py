from django.db import models
import holidays
from .province_state import province_state
from people.models import Employee
from user.models import CustomUser


class Organization(models.Model):
    """
    this will store organization's data
    """
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=5)  # abbreviation form; only considering US and CAN for now
    province = models.CharField(max_length=5, blank=True)  # abbreviation form
    state = models.CharField(max_length=5, blank=True)  # abbreviation form

    def holiday_model(self):
        model = None
        if self.country == 'US' or self.country == 'USA':
            total_state = province_state.get('US')
            if self.state in total_state.keys():
                model = holidays.US(state=self.state)
        elif self.country == 'CAN':
            total_provinces = province_state.get('CAN')
            if self.province in total_provinces.keys():
                model = holidays.CA(prov=self.province)
        return model

    def __str__(self):
        return self.name


class VacationNotification(models.Model):
    requester = models.ForeignKey(Employee,
                                  on_delete=models.CASCADE,
                                  null=True)
    assignee = models.ForeignKey(CustomUser,
                                 on_delete=models.CASCADE,
                                 null=True)
    date = models.DateField()
    schedule_conflict = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    responded = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)

    def json_format(self):
        output = {'requester_name': '{} {}'.format(self.requester.user.first_name,
                                                   self.requester.user.last_name),
                  'requester_employee_id': str(self.requester.user.employee_detail.employee_id),
                  'date': str(self.date),
                  'schedule_conflict': str(self.schedule_conflict),
                  }
        return output


class RecentActions(models.Model):
    """
    action 1: add  2: change 3: delete
    """
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             null=True)
    action = models.PositiveSmallIntegerField()
    object_name = models.TextField(max_length=200)
    object_class = models.TextField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
