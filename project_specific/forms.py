# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 21:59:23 2019

@author: Oliver
"""

from django import forms
from user.models import Group


class SwapForm(forms.Form):
    swap_shift_start = forms.DateTimeField(help_text='2006-10-25 14:30:59')


class GroupCreateForm(forms.Form):
    name = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
    password_conf = forms.CharField(max_length=50, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(GroupCreateForm, self).clean()
        password = cleaned_data.get('password')
        password_conf = cleaned_data.get('password_conf')

        if password != password_conf:
            self._errors['password_conf'] = self.error_class(['Password do not match'])
            del self.cleaned_data['password_conf']
        return cleaned_data


class GroupJoinForm(forms.Form):
    group_id = forms.IntegerField(min_value=0)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(GroupJoinForm, self).clean()
        group_id = cleaned_data.get('group_id')
        password = cleaned_data.get('password')

        group = Group.objects.get(pk=group_id)
        group_pass = group.password
        if (group.id != group_id) or (password != group_pass):
            self._errors['group_id'] = self.error_class(['group ID or password does not match record'])
            del self.cleaned_data['group_id']
            del self.cleaned_data['password']
        return cleaned_data
