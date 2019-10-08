# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 21:59:23 2019

@author: Oliver
"""

from django import forms
from user.models import Group
from django.http import JsonResponse


class AjaxableResponseMixin:
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class SwapForm(AjaxableResponseMixin, forms.Form):
    # swap_shift_start = forms.DateTimeField(help_text='2006-10-25 14:30:59')
    test_date = forms.DateField()


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