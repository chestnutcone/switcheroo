# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 21:59:23 2019

@author: Oliver
"""

from django import forms
#
class SwapForm(forms.Form):
    swap_shift_start = forms.DateTimeField(help_text='2006-10-25 14:30:59')
    
