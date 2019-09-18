# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 22:07:12 2019

@author: Oliver
"""

from django.urls import path
from .views import SignUpView

urlpatterns = [
               path('signup/', SignUpView.as_view(), name='signup'),
               ]