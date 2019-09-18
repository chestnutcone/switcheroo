# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 20:47:48 2019

@author: Oliver
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Group


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'is_manager')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'is_manager')


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'owner', 'password']
