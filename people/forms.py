# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 23:47:03 2019

@author: Oliver
"""
from django import forms
from people.models import Position, Unit, Employee
from user.models import CustomUser

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['user','employee_id','person_position','person_unit', 'group']
        labels = {'user':'Employee',
                  'employee_id': 'Employee ID',
                  'person_position': 'Position',
                  'person_unit': 'Unit',}
#    def __init__(self, *args, **kwargs):
##        user = kwargs.pop('user')
#        super(EmployeeForm, self).__init__(*args, **kwargs)
#        print('current instance', self.instance.group)
#        
#        self.fields['user'].queryset = CustomUser.objects.filter(group=self.instance.group)

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['position_choice', 'group']
        labels = {'position_choice': 'Position'}
        
class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit 
        fields = ['unit_choice', 'group']
        labels = {'unit_choice':'Unit'}