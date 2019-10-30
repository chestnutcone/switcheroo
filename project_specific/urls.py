# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 13:17:48 2019

@author: Oliver
"""

from django.urls import path
from . import views

urlpatterns = [
        path('', views.main_view, name='main'),
        path('profile/', views.profile_view, name='index'),
        path('logout/', views.logout_view, name='logout'),
        path('settings/', views.preference_view, name='preference'),
        path('swap/', views.swap_view, name='swap'),
        path('schedule/', views.schedule_view, name='schedule_view'),
        path('vacation/', views.vacation_view, name='vacation_view'),
        path('swap/request', views.swap_request_view, name='swap_request'),
        path('swap/receive', views.receive_request_view, name='receive_swap'),
        path('manager/', views.manager_profile_view, name='manager_view'),
        path('manager/vacation', views.manager_vacation_view, name='manager_vacation_view'),
        path('manager/request', views.manager_request_view, name='manager_request_view'),
        path('manager/assign', views.manager_assign_view, name='manager_assign_view'),
        path('manager/people', views.manager_people_view, name='manager_people_view'),
        path('manager/schedule', views.manager_schedule_view, name='manager_schedule_view'),
        path('manager/view', views.manager_employee_view, name='manager_employee_view'),
        path('manager/settings', views.manager_preference_view, name='manager_preference_view'),
        ]
