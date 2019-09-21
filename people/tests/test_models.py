# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 10:19:42 2019

@author: Oliver
"""

from django.test import TestCase
from people.models import Employee, Position, Unit
from user.models import Group, CustomUser, EmployeeID

# Create your tests here.
class EmployeeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # "setUpTestData: Run once to set up non-modified data for all class methods.")
        # set up non-modified objects used by all test methods
        employee_detail = EmployeeID.objects.create(employee_id=1)
        user = CustomUser.objects.create(employee_detail=employee_detail)
        group = Group.objects.create(owner=user,
                                     name='group1',
                                     password='test123')
        user.group = group
        user.save()
        position = Position.objects.create(position_choice='RN')
        unit = Unit.objects.create(unit_choice='T00ACE')
        Employee.objects.create(user=user,
                                person_position=position,
                                person_unit=unit,
                                )

    def setUp(self):
        # print("setUp: Run once for every test method to setup clean data.")
        pass

    def test_person_position_label(self):
        employee_detail = EmployeeID.objects.get(pk=1)
        user = CustomUser.objects.get(employee_detail=employee_detail)
        person = Employee.objects.get(user=user)
        field_label = person._meta.get_field('person_position').verbose_name
        self.assertEquals(field_label, 'person position')

    def test_person_unit_label(self):
        employee_detail = EmployeeID.objects.get(pk=1)
        user = CustomUser.objects.get(employee_detail=employee_detail)
        person = Employee.objects.get(user=user)
        field_label = person._meta.get_field('person_unit').verbose_name
        self.assertEquals(field_label, 'person unit')


class PositionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # "setUpTestData: Run once to set up non-modified data for all class methods.")
        # set up non-modified objects used by all test methods
        Position.objects.create(position_choice='RN')

    def setUp(self):
        # print("setUp: Run once for every test method to setup clean data.")
        pass

    def test_position_label(self):
        position = Position.objects.get(pk=1)
        field_label = position._meta.get_field('position_choice').verbose_name
        self.assertEquals(field_label, 'position choice')


class UnitModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # "setUpTestData: Run once to set up non-modified data for all class methods.")
        # set up non-modified objects used by all test methods
        Unit.objects.create(unit_choice='T00ACE')

    def setUp(self):
        # print("setUp: Run once for every test method to setup clean data.")
        pass

    def test_position_label(self):
        unit = Unit.objects.get(pk=1)
        field_label = unit._meta.get_field('unit_choice').verbose_name
        self.assertEquals(field_label, 'unit choice')
