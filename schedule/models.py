from django.db import models

from people.models import Employee
import datetime
import pytz
from django.core.validators import MaxValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from user.models import Group
from project_specific.models import Organization
from django.db.models import Q
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    log_filename = 'logs/schedule_models.log'
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    file_handler = logging.handlers.TimedRotatingFileHandler(log_filename, when='midnight')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


class Shift(models.Model):
    """The shift model is suppose to register common shifts. Ie morning/night 
    shifts, to avoid keep typing the same thing. It becomes a reusable object
    
    Shift start is starting time for the shift, and duration is how long
    the shift will last for
    
    Shift name is just a reference name ie morning shift
    """
    # correspond to datetime.time object
    shift_start = models.TimeField(help_text='enter format hh:mm:ss')
    # correspond to datetime.timedelta
    shift_duration = models.DurationField(help_text='enter format hh:mm:ss')
    shift_name = models.CharField(max_length=20)

    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)

    def __str__(self):
        return self.shift_name


class Schedule(models.Model):
    """
    The schedule model is suppose to register common schedule pattern. For
    example, if morning/morning/night/night/rest/rest/rest/rest days are common
    pattern, then it can be stored as a pattern, and admin does not have to repeat
    this schedule pattern
    
    cycle is how many days does this cycle cut off? In the aforementioned 
    shift cycle, it is 8 days. There will be a lot of day fields to accommodate
    different shift patterns. But if there are 10 day fields, and cut off is 
    at 8, then it will be a cycle of the first 8 day. The last two are ignored
    
    
    """
    schedule_name = models.CharField(max_length=20)
    cycle = models.PositiveSmallIntegerField(verbose_name='cycle',
                                             validators=[MaxValueValidator(10)],
                                             help_text='how many days is the shift pattern cycle',
                                             )

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
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)

    def mk_ls(self):
        self.day_list = [self.day_1, self.day_2, self.day_3]
        self.day_list = self.day_list[:self.cycle]

    def __str__(self):
        return self.schedule_name


class Assign(models.Model):
    """Assign model is made to assign schedule to employee. It will store
    all schedule in this model. You can filter for employee, day, etc
    
    field switch is to indicate whether this schedule is currently hoping 
    for a switch. Once a swap is made, this will be made false
    
    
    Will need to have a mass schedule assign function, where it can apply 
    pattern to all employee at once
    """
    # correspond to datetime.date
    start_date = models.DateField(help_text='start day for shift')

    shift_start = models.DateTimeField()
    shift_end = models.DateTimeField()

    employee = models.ForeignKey(Employee,
                                 on_delete=models.CASCADE,
                                 null=True)
    # for switching shifts
    switch = models.BooleanField(default=False)

    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)

    def same(self, shift_start, employee):
        """return dictionary with bool value 
        whether the attributes match up to query"""
        result = {}

        result['shift_start'] = self.shift_start == shift_start
        result['employee'] = self.employee == employee
        return result


class Vacation(models.Model):
    """
    Vacation model is made to store vacation days or days off for employees
    """

    date = models.DateField(help_text='Day Off')
    employee = models.ForeignKey(Employee,
                                 on_delete=models.CASCADE,
                                 null=True)
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)


class Request(models.Model):
    """This Request model is designed to hold those schedules that are currently
    requesting the receiver for a swap. It happens after the requester selects
    who to make the switch with.
    
    Accept is whether receiver accepts the shift swap
    done is whether a response has been accepted
    
    
    """
    applicant = models.ForeignKey(Employee,
                                  on_delete=models.CASCADE,
                                  null=True,
                                  related_name="requester")
    receiver = models.ForeignKey(Employee,
                                 on_delete=models.CASCADE,
                                 null=True,
                                 related_name="receiver")
    applicant_schedule = models.ForeignKey(Assign,
                                           on_delete=models.SET_NULL,
                                           null=True,
                                           related_name="requester_shift")
    receiver_schedule = models.ForeignKey(Assign,
                                          on_delete=models.SET_NULL,
                                          null=True,
                                          related_name="receiver_shift")
    # get creation timestamp for timeout purpose later
    created = models.DateTimeField(auto_now_add=True)

    # did the receiver accept the proposed swap?
    accept = models.BooleanField(default=False)
    # is the action done?
    done = models.BooleanField(default=False)


def get_schedule(person):
    """
    get a person's schedules sorted by date
    
    person is Employee instance"""
    existing_schedule = Assign.objects.filter(employee__exact=person).order_by('shift_start')
    return existing_schedule


def set_schedule_day(person, start_day, shift, override=False):
    """
    set schedule for a single day on that person
    
    person is Employee instance
    start_day is datetime.date
    shift is Shift instance"""
    status_detail = {'overridable': [],
                     'non_overridable': [],
                     'holiday': [],
                     'employee': person}
    try:
        org = Organization.objects.get(pk=1)
    except ObjectDoesNotExist:
        pass
    else:
        holiday_model = org.holiday_model()
        if (holiday_model is not None) and (start_day in holiday_model):
            status_detail['holiday'].append(holiday_model[start_day])

    if person.group != shift.group:
        status = False
        status_detail['non_overridable'].append('Employee group does not match shift group')
        return status, status_detail

    shift_time = pytz.UTC.localize(shift.shift_start)
    shift_dur = shift.shift_duration

    # shift_start and shift_end tzinfo is UTC
    shift_start = datetime.datetime.combine(start_day, shift_time)
    shift_end = shift_start + shift_dur

    # register dates
    # check if there are any shift conflicts and vacation days
    existing_schedule = Assign.objects.filter(employee__exact=person).filter(start_date__exact=start_day)
    vacation_schedule = Vacation.objects.filter(employee__exact=person).filter(date__exact=start_day)

    workday_queryset = person.workday.all()

    workdays = [workday.day for workday in workday_queryset]
    if start_day.weekday() not in workdays:
        if not override:
            status = False
            status_detail['overridable'].append((start_day, shift))
            return status, status_detail

    if not (existing_schedule or vacation_schedule):
        schedule = Assign(start_date=start_day,
                          shift_start=shift_start,
                          shift_end=shift_end,
                          employee=person,
                          group=person.group)
        schedule.save()
        status = True
    else:
        # else if there is already a schedule
        # find all schedule time
        overlap = False
        if vacation_schedule.exists():
            overlap = True
        else:
            for exist_shift in existing_schedule:
                overlap = exist_shift.shift_start <= shift_start < exist_shift.shift_end
                if overlap:
                    # if found an overlap
                    break

        if overlap:
            # if there is overlap of shifts
            status_detail['non_overridable'].append((start_day, shift))
            status = False
        else:
            # if no overlap (but allow double shifts ie shift continuation)
            schedule = Assign(start_date=start_day,
                              shift_start=shift_start,
                              shift_end=shift_end,
                              employee=person,
                              group=person.group)
            schedule.save()
            status = True

    return status, status_detail


def set_schedule(person, start_date, shift_pattern, repeat=1, override=False):
    """
    This function sets a person's schedule
    
    person is Employee instance
    start_date is datetime.date object
    shift is shift pattern from Schedule
    """
    status_detail = {
                     'overridable': [],
                     'non_overridable': [],
                     'holiday': [],
                     'args':(person, start_date, shift_pattern, repeat)
                    }
    if person.group != shift_pattern.group:
        status = False
        status_detail['non_overridable'] = ['All attempts']
        return status, status_detail

    try:
        org = Organization.objects.get(pk=1)
    except ObjectDoesNotExist:
        holiday_model = None
    else:
        holiday_model = org.holiday_model()

    # shift_start is datetime.time
    workday_queryset = person.workday.all()
    workdays = [workday.day for workday in workday_queryset]

    shift_pattern.mk_ls()
    work_schedule = len(shift_pattern.day_list) * repeat
    work_schedule_list = []
    for i in range(work_schedule):
        work_schedule_list.append(start_date + datetime.timedelta(days=i))

    for pattern, date in zip(shift_pattern.day_list * repeat, work_schedule_list):
        if pattern is None:
            # if it is a rest day, go to next iteration to set schedule
            continue
        if date.weekday() not in workdays:
            if not override:
                status_detail['overridable'].append((date, pattern))
                continue

        if holiday_model is not None and date in holiday_model:
            status_detail['holiday'].append(holiday_model[date])

        shift_time = pytz.UTC.localize(pattern.shift_start)
        shift_dur = pattern.shift_duration

        # shift_start and shift_end tzinfo is UTC
        shift_start = datetime.datetime.combine(date, shift_time)
        shift_end = shift_start + shift_dur

        # register date
        # check if there are any shift conflicts
        existing_schedule = Assign.objects.filter(employee__exact=person).filter(start_date__exact=date)
        vacation_schedule = Vacation.objects.filter(employee__exact=person).filter(date__exact=date)

        if not (existing_schedule or vacation_schedule):
            schedule = Assign(start_date=date,
                              shift_start=shift_start,
                              shift_end=shift_end,
                              employee=person,
                              group=person.group)
            schedule.save()
        else:
            # else if there is already a schedule
            # find all schedule time
            overlap = False
            if vacation_schedule.exists():
                overlap = True
            else:
                for exist_shift in existing_schedule:
                    overlap = exist_shift.shift_start <= shift_start < exist_shift.shift_end
                    if overlap:
                        # if found an overlap
                        break

            if overlap:
                # if there is overlap of shifts
                status_detail['non_overridable'].append((date, pattern))
            else:
                # if no overlap (but allow double shifts ie shift continuation)
                schedule = Assign(start_date=date,
                                  shift_start=shift_start,
                                  shift_end=shift_end,
                                  employee=person,
                                  group=person.group)
                schedule.save()

    status = not bool(status_detail['non_overridable'] or
                      status_detail['overridable'])
    return status, status_detail


def clear_schedule(person):
    """clear all a person's schedule"""

    while True:
        try:
            option = input("This will delete all the person's schedule." \
                           "Choose an option to proceed [y/N]: ").lower()
            if option in ['y', 'n']:
                break
        except:
            pass
    if option == 'y':
        while True:
            try:
                employee_id = input("The schedule will be permanently deleted." \
                                    "Are you sure? Enter employee ID if you\
                                    want to delete schedule: ").lower()

                if employee_id.isdigit() and int(employee_id) == person.user.employee_detail.employee_id:
                    Assign.objects.filter(employee__exact=person).delete()
                    break
                else:
                    print('employee ID does not match, will not delete any schedule')
                    break
            except:
                pass
    else:
        print("person's schedule not deleted")


def del_schedule(person, date):
    """delete a person's schedule on a particular date
    person is Employee instance
    date is datetime.date
    """
    schedule = Assign.objects.filter(employee__exact=person).filter(start_date__exact=date)
    if schedule.count() > 1:
        # if there are more than one schedule on that date
        for n, s in enumerate(schedule):
            print('id: {}, start time: {}, end time: {}'.format(n, s.shift_start, s.shift_end))

        print("there are more than one schedule on this day. Which one would you like to delete?")
        while True:
            try:
                option = input('Please enter a valid index (int)'
                               'of the object you want to delete ')
                if option.isdigit() and int(option) <= schedule.count():
                    break
            except:
                pass

        schedule[option].delete()
    else:
        schedule.delete()


def swap(person, swap_shift_start):
    """
    this function will check if swap shift is possible
    person is Employee instance, and the requester
    swap_shift_start is the shift that needs to be swapped
    
    This will output a dictionary with key success, available_shifts, free_people
    
    first checks people that are currently swapping,
    then check people that are open to swap (even if not currently swapping)
    then check people that are open to swap but are not working (no shifts offered
    in return. Acceptor does not offer shift in return on last case
    
    if a shift/person is found to be possible to make swap, success will 
    be True. If there are shifts offered in return, the available_shifts 
    will be QuerySet. If there are no shifts offered in return, then, 
    available_shifts will remain as None and free_people will return as a list 
    of Employee instance who are open to accept shift and are not working 
    that shift
    
    If not possible to find any shift/person to swap, success will be Fail
    and available_shifts will be None and free_people will be empty list
    
    The current logic of swap shift does not allow double shifts (inclusive). 
    If person A wants to swap 7-9 shift and person B can offer 9-11. It will 
    not allow the shift to be swapped
    """

    success = True
    output = None
    free_people = []
    error = False

    swap_shift_start = pytz.UTC.localize(swap_shift_start)
    swap_day = Assign.objects.filter(employee__exact=person).filter(shift_start=swap_shift_start)
    if not swap_day.exists():
        logger.error('The requested shift to swap cannot be found in schedule')
        success = False
        error = True
        return {'success': success,
                'available_shifts': output,
                'free_people': free_people,
                'error': error}
    swap_day_switch = swap_day[0]
    # there should only be one schedule with 
    # that one shift start date for that person
    result = swap_day_switch.same(shift_start=swap_shift_start, employee=person)
    if not all(result.values()) and swap_day.count() == 1:
        logger.error('Duplicate (non-unique shift start) shifts requesting to be swap')
        error = True
        success = False
        return {
                'success': success,
                'available_shifts': output,
                'free_people': free_people,
                'error': error
                }

    swap_day_switch.switch = True
    swap_day_switch.save()

    person_schedule = Assign.objects.filter(employee__exact=person)

    # not itself, in the same group, of those swapping as well, those that dont have the same shift
    # filtering of group is included in filtering for position and unit since position and unit contain group info
    # currently filtering for exact position
    possible_swappers = Employee.objects.filter(
        person_unit=person.person_unit).filter(
        person_position=person.person_position)

    swapper_shifts = Assign.objects.filter(employee__in=possible_swappers).exclude(employee=person).filter(
        switch=True).exclude(shift_start=swap_shift_start)

    # get shifts that are not in the person's schedule already
    for start, end in zip(person_schedule.values_list('shift_start'), person_schedule.values_list('shift_end')):
        swapper_shifts = swapper_shifts.exclude(
            Q(shift_start__gte=start[0]) & Q(shift_start__lt=end[0])).exclude(
            Q(shift_end__gt=start[0]) & Q(shift_end__lte=end[0]))

    if swapper_shifts.count() > 0:
        output = swapper_shifts
    else:
        # get from people that are accepting shifts that are in the same group, unit, position
        acceptors = Employee.objects.filter(
            person_unit=person.person_unit).filter(
            person_position=person.person_position).filter(accept_swap__exact=True)
        # find people that are accepting shifts who are not working on that day
        backup_swapper_shifts = Assign.objects.exclude(employee__exact=person).filter(employee__in=acceptors).exclude(
            shift_start__exact=swap_shift_start)

        # looking for possible trades on the accepting swaps
        for start, end in zip(person_schedule.values_list('shift_start'), person_schedule.values_list('shift_end')):
            backup_swapper_shifts = backup_swapper_shifts.exclude(
                Q(shift_start__gte=start[0]) & Q(shift_start__lt=end[0])).exclude(
                Q(shift_end__gt=start[0]) & Q(shift_end__lte=end[0]))

            if backup_swapper_shifts.count() == 0:
                break

        if backup_swapper_shifts.count() > 0:
            output = backup_swapper_shifts

        else:
            # look for people that are accepting shifts but not offering anything
            # in return. Which means people who are accepting shifts but that
            # are not working that day

            for acceptor in acceptors:
                # check if person has shift on that day
                workdays = [workday.day for workday in acceptor.workday.all()]

                if (not Assign.objects.filter(employee__exact=acceptor).filter(
                        shift_start__exact=swap_shift_start).exists()) and swap_shift_start.weekday() in workdays:
                    # if acceptor not working that day and is available to work

                    free_people.append(acceptor)
            if not free_people:
                success = False

                # go into queue of holding, wait till database updates, then run rechecks
    return {
            'success': success,
            'available_shifts': output,
            'free_people': free_people,
            'error': error
            }


def send_email(subject, msg, sender_address, receiver_list):
    """
    This function will send email
    
    subject, msg, sender_address in str,
    receiver_list in list of str"""
    success = send_mail(subject=subject,
                        message=msg,
                        from_email=sender_address,
                        recipient_list=receiver_list)
    return success


def set_vacation(person, date):
    work_conflict = Assign.objects.get(employee=person, start_date=date).exists()
    if work_conflict:
        created = None
    else:
        _, created = Vacation.objects.get_or_create(date=date, employee=person, group=person.group)
    status = {
              'work_conflict': work_conflict,
              'vacation_created': created
             }
    return status
