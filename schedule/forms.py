# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 13:45:34 2019

@author: Oliver
"""

from django import forms
from schedule.models import Shift, Schedule


class AssignForm(forms.Form):
    employee_id = forms.IntegerField()
    start_date = forms.DateField(help_text='format 2006-10-25')
    shift_pattern = forms.CharField(max_length=20)
    repeat = forms.IntegerField(min_value=1, max_value=50,
                                help_text='how many repeats')


class SwapForm(forms.Form):
    employee_id = forms.IntegerField()
    swap_shift_start = forms.DateTimeField(help_text='2006-10-25 14:30:59')


class ViewScheduleForm(forms.Form):
    employee_id = forms.IntegerField()


# admin forms below
class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['shift_name', 'shift_start', 'shift_duration', 'group']
        labels = {'shift_name': 'Shift Name',
                  'shift_start': 'Shift Start',
                  'shift_duration': 'Shift Duration',
                  }


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['schedule_name', 'cycle', 'day_1', 'day_2', 'day_3', 'group']
        labels = {'schedule_name': 'Schedule Name',
                  'cycle': 'Cycle',
                  'day_1': 'Day 1',
                  'day_2': 'Day 2',
                  'day_3': 'Day 3', }
