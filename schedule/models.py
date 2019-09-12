from django.db import models

from people.models import Individual
import datetime
import pytz
from django.utils import timezone
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
# Create your models here.
class Shift(models.Model):
    # correspond to datetime.time object
    shift_start = models.TimeField(help_text='enter format hh:mm:ss') 
    # correspond to datetime.timedelta
    shift_duration = models.DurationField(help_text='enter format hh:mm:ss') 
    shift_name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.shift_name
    
class Schedule(models.Model):
        
    schedule_name = models.CharField(max_length=20, primary_key=True)
    cycle = models.PositiveSmallIntegerField(MaxValueValidator(10),
                                             help_text='how many days is the shift pattern cycle')
    day_1 = models.ForeignKey(Shift, 
                              related_name='%(app_label)s_%(class)s_1',
                             on_delete=models.SET_NULL, 
                             null=True,
                             blank=True)
    day_2 = models.ForeignKey(Shift, 
                              related_name='%(app_label)s_%(class)s_2',
                             on_delete=models.SET_NULL, 
                             null=True,
                             blank=True)
    day_3 = models.ForeignKey(Shift, 
                              related_name='%(app_label)s_%(class)s_3',
                             on_delete=models.SET_NULL, 
                             null=True,
                             blank=True)
    def mk_ls(self):
        self.day_list = [self.day_1, self.day_2, self.day_3]
        self.day_list = self.day_list[:self.cycle]
    
    
    def __str__(self):
        return self.schedule_name
    

class Assign(models.Model):
    # correspond to datetime.date
    start_date = models.DateField(help_text='start day for shift')
    
    shift_start = models.DateTimeField()
    shift_end = models.DateTimeField()
    
    individual = models.ForeignKey(Individual,
                               on_delete=models.SET_NULL,
                               null=True)
    # for switching shifts
    switch = models.BooleanField(default=False)
    def same(self, shift_start, individual):
        """return dictionary with bool value 
        whether the attributes match up to query"""
        result = {}
#        result['start_date'] = self.start_date == start_date
        result['shift_start'] = self.shift_start == shift_start
#        result['shift_end'] = self.shift_end == shift_end
        result['individual'] = self.individual == individual
        return result
        
        
def get_schedule(person):
    """get a person's schedules sorted by date"""
    existing_schedule = Assign.objects.filter(individual__exact=person).order_by('shift_start')
#    print('fetching schedule for', person.user.first_name, 
#          person.user.last_name)
#    for schedule in existing_schedule:
#        print(schedule.shift_start, schedule.shift_end)
    return existing_schedule
        
        
def set_schedule(person, start_date, shift_pattern):
    """
    start_date is datetime.date object
    shift is shift pattern 
    """
    
    # shift_start is datetime.time
    not_registered = []
    working_days = len(shift_pattern.day_list)
    working_dates = []
    for i in range(working_days):
        working_dates.append(start_date + datetime.timedelta(days=i))


    for pattern, dates in zip(shift_pattern.day_list, working_dates):
        if pattern is None:
            # if it is a rest day, go to next iteration to set schedule
            continue
        shift_time = pytz.UTC.localize(pattern.shift_start)
        shift_dur = pattern.shift_duration

        # shift_start and shift_end tzinfo is UTC
        shift_start = datetime.datetime.combine(dates, shift_time)
        shift_end = shift_start + shift_dur

        # register dates
        # check if there are any shift conflicts
        existing_schedule = Assign.objects.filter(individual__exact=person).filter(start_date__exact=dates)
      
        if not existing_schedule:
            schedule = Assign(start_date = dates,
                              shift_start = shift_start,
                              shift_end = shift_end,
                              individual = person)
            schedule.save()
        else:
            # else if there is already a schedule
            # find all schedule time
            overlap = False
            for exist_shift in existing_schedule:
                overlap = exist_shift.shift_start <= shift_start < exist_shift.shift_end
                if overlap:
                    # if found an overlap
                    break
                
            if overlap:
                # if there is overlap of shifts
                not_registered.append((dates, pattern))
            else:
                # if no overlap (but allow double shifts ie shift continuation)
                schedule = Assign(start_date = dates,
                              shift_start = shift_start,
                              shift_end = shift_end,
                              individual = person)
                schedule.save()
        
    if not not_registered:
        # if all are successful
        print('schedule set')
    else:
        # if some failed
        print('following dates did not register schedule due to schedule conflicts:')
        for failed_d, failed_p in not_registered:
            print(failed_d, failed_p)
    
    status = not not_registered
    return status

def clear_schedule(person):
    """clear all a person's schedule"""
    
    while True:
        try:
            option = input("This will delete all the person's schedule. \
                           Choose an option to proceed [y/n]: ").lower()
            if option in ['y','n']:
                break
        except:
            pass
    if option == 'y':
        Assign.objects.filter(individual__exact=person).delete()
    else:
        print("person's schedule not deleted")
        
def del_schedule(person, date):
    """delete a person's schedule on a particular date"""
    schedule = Assign.objects.filter(individual__exact=person).filter(start_date__exact=date)
    if schedule.count() > 1:
        # if there are more than one schedule on that date
        for n, s in enumerate(schedule):
            print('id: {}, start time: {}, end time: {}'.format(n, s.shift_start, s.shift_end))
        
        print("there are more than one schedule on this day. \
                  Which one would you like to delete?")
        while True:
            try:
                option = input('Please enter a valid index (int) \
                  of the object you want to delete ')
                if option.isdigit() and int(option) <= schedule.count():
                    break
            except:
                pass
            
        schedule[option].delete()
    else:
        schedule.delete()
    
        
def swap(person, swap_shift_start):
    print(person)
    success = True
    
    # try to see if the schedule exist
    swap_day = Assign.objects.filter(individual__exact=person).filter(shift_start__exact=swap_shift_start)
    # if there are no schedule that day, it will not find it
    if swap_day.count() == 0:
        raise ValidationError('There are no schedule for '+str(swap_shift_start))
    
    # there should only be one schedule with 
    # that one shift start date for that person
    result = swap_day[0].same(shift_start=swap_shift_start,individual=person)
    assert all(result.values()) and swap_day.count() == 1
    # make the switch attribute True
    swap_day[0].switch = True
    swap_day[0].save()
    
    # person's schedule not including the day requesting to be swapped
    person_schedule = Assign.objects.filter(individual__exact=person)

    # not itself, of those swapping as well, those that dont have the same shift
    swapper_shifts = Assign.objects.exclude(individual__exact=person).filter(switch__exact=True).exclude(shift_start__exact=swap_shift_start)
    # get shifts that are not in the person's schedule already
    for start, end in zip(person_schedule.values_list('shift_start'),person_schedule.values_list('shift_end')):        
        # range is inclusive....that means no double shift allowed unless change syntax
        swapper_shifts = swapper_shifts.exclude(
                shift_start__range=(start[0],end[0])).exclude(
                        shift_end__range=(start[0],end[0]))

#    swapper_shifts = swapper_shifts.exclude(shift_start__in=person_schedule.values_list('shift_start'))
        

    if swapper_shifts.count() > 0:
        # if we have some swappers, swap them
        for shift in swapper_shifts:
            print('swappers', shift.individual, shift.shift_start)
        output = swapper_shifts
    else:
        # get from people that are accepting shifts
        acceptors = Individual.objects.filter(accept_swap__exact=True)
#        print('acceptors', acceptors)
        # find people that are accepting shifts who are not working on that day
        backup_swapper_shifts = Assign.objects.exclude(individual__exact=person).filter(individual__in=acceptors).exclude(shift_start__exact=swap_shift_start)
#        backup_swapper_shifts = backup_swapper_shifts.exclude(shift_start__in=person_schedule.values_list('shift_start'))
#        print('backup shifts pre', backup_swapper_shifts)
        for start, end in zip(person_schedule.values_list('shift_start'),person_schedule.values_list('shift_end')):
            backup_swapper_shifts = backup_swapper_shifts.exclude(
                    shift_start__range=(start[0],end[0])).exclude(
                            shift_end__range=(start[0],end[0]))
#            print('checking', start, end)
#            print('in loop', backup_swapper_shifts)
        if backup_swapper_shifts.count() > 0:
            # this gives available shifts to swap
            for backup in backup_swapper_shifts:
                print('backup swappers', backup.individual, backup.shift_start)
                
            output = backup_swapper_shifts
        else:
            print('no people are available to swap')
            success = False
            output = None
            # go into queue of holding, wait till database updates, then run rechecks
    return {'success':success,
            'available_shifts':output,}
            
        
        
        
        