from django.test import TestCase
from schedule.models import Shift, Schedule, Assign, Vacation, Request
from user.models import Group, CustomUser, EmployeeID
from people.models import Unit, Position, Employee, Weekday
import schedule.models as sm
import datetime


def create_user(employee_id, group_name='', group=None, is_manager=False):
    if is_manager:
        user_detail = EmployeeID.objects.create(employee_id=employee_id,
                                                is_manager=is_manager)
        # print('username', 'user{}'.format(employee_id))
        user = CustomUser.objects.create(employee_detail=user_detail,
                                         username='user{}'.format(employee_id))
        group = Group.objects.create(owner=user,
                                     name=group_name,
                                     password='test1234')
        user.group = group
        user.save()
        return user, group
    else:
        user_detail = EmployeeID.objects.create(employee_id=employee_id,
                                                is_manager=is_manager)

        user = CustomUser.objects.create(employee_detail=user_detail,
                                         username='user{}'.format(employee_id),
                                         group=group)
        return user


def create_shift(shift_start, shift_dur, shift_name, group):
    shift = Shift.objects.create(shift_start=shift_start,
                                 shift_duration=shift_dur,
                                 shift_name=shift_name,
                                 group=group)
    return shift


def create_schedule(schedule_name, day_list, group, cycle=3):
    schedule = Schedule.objects.create(schedule_name=schedule_name,
                                       cycle=cycle,
                                       day_1=day_list[0],
                                       day_2=day_list[1],
                                       day_3=day_list[2],
                                       group=group)
    return schedule


def create_unit(unit_name, group):
    return Unit.objects.create(unit_choice=unit_name,
                               group=group)


def create_position(position_name, group):
    return Position.objects.create(position_choice=position_name,
                                   group=group)


def create_employee(user, position, unit, group, weekday):
    employee = Employee.objects.create(user=user,
                                       person_position=position,
                                       person_unit=unit,
                                       group=group,
                                       )

    for work in weekday:
        employee.weekday.add(Weekday.objects.get(pk=work))
    employee.save()
    return employee


def num_generator():
    num = 0
    while True:
        num += 1
        yield num


def create_employee_pool(mor_start, nig_start, shift_dur, group_name, id_gen):

    manager, group = create_user(employee_id=next(id_gen),
                                 group_name=group_name,
                                 is_manager=True)
    u1 = create_user(employee_id=next(id_gen),
                     group=group)
    u2 = create_user(employee_id=next(id_gen),
                     group=group)
    u3 = create_user(employee_id=next(id_gen),
                     group=group)
    mor = create_shift(mor_start, shift_dur, 'morning', group)
    nig = create_shift(nig_start, shift_dur, 'night', group)
    _ = create_schedule('standard', [mor, mor, nig], group)
    unit = create_unit('T00ACE', group)
    rn = create_position('RN', group)
    lpn = create_position("LPN", group)

    available = [0, 1, 2, 3, 4]
    rn_users = [u1, u2]
    lpn_users = [u3]
    for user in rn_users:
        _ = create_employee(user=user, position=rn, unit=unit, group=group, weekday=available)
    for user in lpn_users:
        _ = create_employee(user=user, position=lpn, unit=unit, group=group, weekday=available)

class AssignModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        mor_start = datetime.time(7, 30)
        night_start = datetime.time(19, 30)
        shift_dur = datetime.timedelta(hours=12)
        id_gen = num_generator()
        Weekday._set_weekday()

        # create group 1
        create_employee_pool(mor_start=mor_start, nig_start=night_start,
                             shift_dur=shift_dur, group_name='group1', id_gen=id_gen)

        # create group 2
        create_employee_pool(mor_start=mor_start, nig_start=night_start,
                             shift_dur=shift_dur, group_name='group2', id_gen=id_gen)

    def test_set_schedule(self):
        group1 = Group.objects.get(name='group1')
        group1_pool = Employee.objects.filter(group=group1)
        # print('schedule pattern', Schedule.objects.filter(group=group1).filter(schedule_name__exact='standard'))
        shift_pattern = Schedule.objects.filter(group=group1).get(schedule_name='standard')
        morning_shift = Shift.objects.filter(group=group1).get(shift_name='morning')
        night_shift = Shift.objects.filter(group=group1).get(shift_name='night')

        employees = []
        for person in group1_pool:
            if not person.user.employee_detail.is_manager:
                employees.append(person)
            else:
                manager = person

        def testing_behavior(self, start_date, diff, employees, shift_pattern,
                             expected_status, expected_not_registered):
            status_ls = []
            not_registered_ls = []

            for i, employee in enumerate(employees):
                status, not_registered = sm.set_schedule(person=employee,
                                                         start_date=start_date,
                                                         shift_pattern=shift_pattern)
                # not_registered is list of (dates, shift)
                start_date = start_date + diff
                status_ls.append(status)
                not_registered_ls.append(not_registered)
            self.assertEquals(status_ls, expected_status)
            self.assertEquals(not_registered_ls, expected_not_registered)

        start_date = datetime.date(2019, 9, 1)  # sunday
        diff = datetime.timedelta(days=3)
        expected_status = [False, True, False]
        expected_not_registered = [[(datetime.date(2019, 9, 1), morning_shift)],
                                   [],
                                   [(datetime.date(2019, 9, 7), morning_shift),
                                    (datetime.date(2019, 9, 8), morning_shift)]]
        # testing whether assign schedule avoids non-working days
        testing_behavior(self, start_date, diff, employees, shift_pattern,
                         expected_status, expected_not_registered)

        # testing whether it checks existing schedule
        start_date = datetime.date(2019, 9, 2)  # monday
        diff = datetime.timedelta(days=3)
        expected_status = [False, False, False]
        expected_not_registered = [[(datetime.date(2019, 9, 2), morning_shift)],
                                   [(datetime.date(2019, 9, 5), morning_shift),
                                    (datetime.date(2019, 9, 7), night_shift)],
                                   [(datetime.date(2019, 9, 8), morning_shift)]]
        # testing whether assign schedule avoids non-working days
        testing_behavior(self, start_date, diff, employees, shift_pattern,
                         expected_status, expected_not_registered)

        # testing whether different schedule pattern works
        new_pattern = Schedule.objects.create(schedule_name='new_pattern',
                                              cycle=2,
                                              day_1=night_shift,
                                              day_2=night_shift,
                                              group=group1)
        start_date = datetime.date(2019, 9, 4)  # wednesday
        diff = datetime.timedelta(days=3)
        expected_status = [False, False, False]
        expected_not_registered = [[(datetime.date(2019, 9, 4), night_shift)],
                                   [(datetime.date(2019, 9, 7), night_shift),
                                    (datetime.date(2019, 9, 8), night_shift)],
                                   [(datetime.date(2019, 9, 10), night_shift)]]
        # testing whether assign schedule avoids non-working days
        testing_behavior(self, start_date, diff, employees, new_pattern,
                         expected_status, expected_not_registered)

    def test_set_schedule_day(self):
        group1 = Group.objects.get(name='group1')
        group1_pool = Employee.objects.filter(group=group1)
        shift_pattern = Schedule.objects.filter(group=group1).get(schedule_name='standard')
        morning_shift = Shift.objects.filter(group=group1).get(shift_name='morning')
        night_shift = Shift.objects.filter(group=group1).get(shift_name='night')

        employees = []
        for person in group1_pool:
            if not person.user.employee_detail.is_manager:
                employees.append(person)
            else:
                manager = person

        e1 = employees[0]
        start_date = datetime.date(2019,9,1)
        # lands on weekend, wont work
        output = sm.set_schedule_day(e1, start_date, morning_shift)
        expected = False
        self.assertEquals(output, expected)

        start_date = datetime.date(2019, 9, 2)
        output = sm.set_schedule_day(e1, start_date, morning_shift)
        expected = True
        self.assertEquals(output, expected)

        start_date = datetime.date(2019, 9, 2)
        # schedule conflict wont work
        output = sm.set_schedule_day(e1, start_date, morning_shift)
        expected = False
        self.assertEquals(output, expected)

        start_date = datetime.date(2019, 9, 2)
        # currently allows shift overlap
        output = sm.set_schedule_day(e1, start_date, night_shift)
        expected = True
        self.assertEquals(output, expected)

    def test_swap(self):
        group1 = Group.objects.get(name='group1')
        group1_pool = Employee.objects.filter(group=group1)
        shift_pattern = Schedule.objects.filter(group=group1).get(schedule_name='standard')
        morning_shift = Shift.objects.filter(group=group1).get(shift_name='morning')
        night_shift = Shift.objects.filter(group=group1).get(shift_name='night')

        employees = []
        for person in group1_pool:
            if not person.user.employee_detail.is_manager:
                employees.append(person)
            else:
                manager = person

class ShiftModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        morning_shift = Shift.objects.create(shift_start=datetime.time(7, 30),
                                             shift_duration=datetime.timedelta(hours=12),
                                             shift_name='morning')
        night_shift = Shift.objects.create(shift_start=datetime.time(19, 30),
                                           shift_duration=datetime.timedelta(hours=12),
                                           shift_name='night')

    def test_shift_start_name_label(self):
        shift = Shift.objects.filter(name__exact='morning')[0]
        field_label = shift._meta.get_field('shift_start').verbose_name
        self.assertEquals(field_label, 'shift start')


class ScheduleModelTest(TestCase):
    pass
