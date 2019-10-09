# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 13:17:48 2019

@author: Oliver
"""

from django.urls import path
from . import views

urlpatterns = [
        path('', views.profile_view, name='index'),
        path('swap/', views.swap_view, name='swap'),
        path('swap/result',views.swap_result_view, name='swap_result'),
        path('group/', views.group_view, name='group'),
        path('schedule/', views.schedule_view, name='schedule_view'),
        path('vacation/', views.vacation_view, name='vacation_view'),
        ]