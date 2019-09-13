# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 21:59:23 2019

@author: Oliver
"""

from django import forms
from user.models import Session

#
class SwapForm(forms.Form):
    swap_shift_start = forms.DateTimeField(help_text='2006-10-25 14:30:59')
    
class SessionCreateForm(forms.Form):
    password = forms.CharField(max_length=50)
    password_conf = forms.CharField(max_length=50)
    
    def clean(self):
        cleaned_data = super(SessionCreateForm, self).clean()
        password = cleaned_data.get('password')
        password_conf = cleaned_data.get('password_conf')
        
        if password != password_conf:
            self._errors['password_conf'] = self.error_class(['Password do not match'])
            del self.cleaned_data['password_conf']
        return cleaned_data
    
class SessionJoinForm(forms.Form):
    session_id = forms.IntegerField(min_value=0)
    password = forms.CharField(max_length=50)
    
    def clean(self):
        cleaned_data = super(SessionJoinForm, self).clean()
        session_id = cleaned_data.get('session_id')
        password = cleaned_data.get('password')
        
        session = Session.objects.get(pk=session_id)
        session_pass = session.password
        if (session.id != session_id) or (password != session_pass):
            self._errors['session_id'] = self.error_class(['session ID or password does not match record'])
            del self.cleaned_data['session_id']
            del self.cleaned_data['password']
        return cleaned_data
    
        
        