# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 13:45:34 2019

@author: Oliver
"""

from django import forms
#
class AssignForm(forms.Form):
    employee_id = forms.IntegerField()
    #input_formats='%Y-%m-%d',
    start_date = forms.DateField(help_text='format 2006-10-25')
    shift_pattern = forms.CharField(max_length=20)

class SwapForm(forms.Form):
    employee_id = forms.IntegerField()
    swap_shift_start = forms.DateTimeField(help_text='2006-10-25 14:30:59')

class ScheduleForm(forms.Form):
    employee_id = forms.IntegerField()