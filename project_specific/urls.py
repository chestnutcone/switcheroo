# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 13:17:48 2019

@author: Oliver
"""

from django.urls import path
from . import views

urlpatterns = [
        path('', views.profile_view, name='index'),
        path('logout/', views.logout_view, name='logout'),
        path('swap/', views.swap_view, name='swap'),
        path('group/', views.group_view, name='group'),
        path('schedule/', views.schedule_view, name='schedule_view'),
        path('vacation/', views.vacation_view, name='vacation_view'),
        path('swap/request', views.swap_request_view, name='swap_request'),
        path('swap/receive', views.receive_request_view, name='receive_swap'),
        ]