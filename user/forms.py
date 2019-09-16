# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 20:47:48 2019

@author: Oliver
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'first_name','last_name','email', 'is_manager')

class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('username','first_name','last_name','email', 'is_manager')