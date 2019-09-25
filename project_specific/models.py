from django.db import models
import holidays
from .province_state import province_state


class Organization(models.Model):
    """
    this will store organization's data
    """
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=5)  # abbreviation form; only considering US and CAN for now
    province = models.CharField(max_length=5, blank=True)  # abbreviation form
    state = models.CharField(max_length=5, blank=True)  # abbreviation form

    def holiday_model(self):
        model = None
        if self.country == 'US' or self.country == 'USA':
            total_state = province_state.get('US')
            if self.state in total_state.keys():
                model = holidays.US(state=self.state)
        elif self.country == 'CAN':
            total_provinces = province_state.get('CAN')
            if self.province in total_provinces.keys():
                model = holidays.CA(prov=self.province)
        return model

    def __str__(self):
        return self.name
