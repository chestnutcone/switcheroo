# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:12:31 2019

@author: Oliver
"""

from django.urls import path
from . import views

urlpatterns = [
        path('assign/', views.assign_view, name='assign'),
        path('assign/result',views.assign_result_view, name='assign_result'),
        path('schedule/', views.schedule_view, name='schedule'),
        path('schedule/result',views.schedule_result_view, name='schedule_result'),
        path('swap/',views.swap_view, name='swap'),
        path('swap/result',views.swap_result_view, name='swap_result'),
        ]