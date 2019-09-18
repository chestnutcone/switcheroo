# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 10:19:42 2019

@author: Oliver
"""

from django.test import TestCase
from people.models import Employee, Position, Unit
# Create your tests here.
class EmployeeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
#       "setUpTestData: Run once to set up non-modified data for all class methods.")
        # set up non-modified objects used by all test methods
        position = Position.objects.create(position_choice='RN')
        unit = Unit.objects.create(unit_choice='T00ACE')
        Individual.objects.create(person_name='Test Subject',
                                  person_email='test_subject@hotmail.com',
                                  employee_id=123456,
                                  person_position=position,
                                  person_unit=unit,
                                  )

    def setUp(self):
#        print("setUp: Run once for every test method to setup clean data.")
        pass

    def test_person_name_label(self):
        person = Individual.objects.get(pk=123456)
        field_label = person._meta.get_field('person_name').verbose_name
        self.assertEquals(field_label, 'person name')
        
    def test_person_email_label(self):
        person = Individual.objects.get(pk=123456)
        field_label = person._meta.get_field('person_email').verbose_name
        self.assertEquals(field_label, 'person email')
        
    def test_employee_id_label(self):
        person = Individual.objects.get(pk=123456)
        field_label = person._meta.get_field('employee_id').verbose_name
        self.assertEquals(field_label, 'employee id')
        
    def test_person_position_label(self):
        person = Individual.objects.get(pk=123456)
        field_label = person._meta.get_field('person_position').verbose_name
        self.assertEquals(field_label, 'person position')
        
    def test_person_unit_label(self):
        person = Individual.objects.get(pk=123456)
        field_label = person._meta.get_field('person_unit').verbose_name
        self.assertEquals(field_label, 'person unit')
        
    def test_person_name_max_len(self):
        person = Individual.objects.get(pk=123456)
        max_length = person._meta.get_field('person_name').max_length
        self.assertEquals(max_length,100)
        
        
class PositionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
#       "setUpTestData: Run once to set up non-modified data for all class methods.")
        # set up non-modified objects used by all test methods
        Position.objects.create(position_choice='RN')

    def setUp(self):
#        print("setUp: Run once for every test method to setup clean data.")
        pass

    def test_position_label(self):
        position = Position.objects.get(pk=1)
        field_label = position._meta.get_field('position_choice').verbose_name
        self.assertEquals(field_label, 'position choice')

class UnitModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
#       "setUpTestData: Run once to set up non-modified data for all class methods.")
        # set up non-modified objects used by all test methods
        Unit.objects.create(unit_choice='T00ACE')

    def setUp(self):
#        print("setUp: Run once for every test method to setup clean data.")
        pass

    def test_position_label(self):
        unit = Unit.objects.get(pk=1)
        field_label = unit._meta.get_field('unit_choice').verbose_name
        self.assertEquals(field_label, 'unit choice')
