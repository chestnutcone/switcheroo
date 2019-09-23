from django.test import TestCase
from schedule.models import Shift, Schedule, Assign, Vacation, Request
from user.models import Group, CustomUser, EmployeeID
from people.models import Unit, Position, Employee, Workday
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


def create_employee(user, position, unit, group, workday):
    employee = Employee.objects.create(user=user,
                                       person_position=position,
                                       person_unit=unit,
                                       group=group,
                                       )

    for work in workday:
        employee.workday.add(Workday.objects.get(pk=work))
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
        _ = create_employee(user=user, position=rn, unit=unit, group=group, workday=available)
    for user in lpn_users:
        _ = create_employee(user=user, position=lpn, unit=unit, group=group, workday=available)


class AssignModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        mor_start = datetime.time(7, 30)
        night_start = datetime.time(19, 30)
        shift_dur = datetime.timedelta(hours=12)
        id_gen = num_generator()
        Workday._set_workday()

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
        start_date = datetime.date(2019, 9, 1)
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
        shift_pattern_1 = Schedule.objects.filter(group=group1).get(schedule_name='standard')
        morning_shift_1 = Shift.objects.filter(group=group1).get(shift_name='morning')
        night_shift_1 = Shift.objects.filter(group=group1).get(shift_name='night')

        employees_1 = []
        for person in group1_pool:
            if not person.user.employee_detail.is_manager:
                employees_1.append(person)
            else:
                manager_1 = person

        group2 = Group.objects.get(name='group2')
        group2_pool = Employee.objects.filter(group=group2)
        shift_pattern_2 = Schedule.objects.filter(group=group2).get(schedule_name='standard')
        morning_shift_2 = Shift.objects.filter(group=group2).get(shift_name='morning')
        night_shift_2 = Shift.objects.filter(group=group2).get(shift_name='night')

        employees_2 = []
        for person in group2_pool:
            if not person.user.employee_detail.is_manager:
                employees_2.append(person)
            else:
                manager_2 = person

        start_date = datetime.date(2019, 9, 1)  # sunday
        diff = datetime.timedelta(days=3)

        for i, employee in enumerate(employees_1):
            _, _ = sm.set_schedule(person=employee,
                                   start_date=start_date,
                                   shift_pattern=shift_pattern_1)
            # not_registered is list of (dates, shift)
            start_date = start_date + diff

        start_date = datetime.date(2019, 9, 1)  # sunday
        diff = datetime.timedelta(days=3)

        for i, employee in enumerate(employees_2):
            _, _ = sm.set_schedule(person=employee,
                                   start_date=start_date,
                                   shift_pattern=shift_pattern_2)
            # not_registered is list of (dates, shift)
            start_date = start_date + diff

        # set employee 2 of group 1 and 2 sept 4 morn schedule to switch = True
        # swap employee 1 of group 1
        # should return employee 2 of group 2 for result
        e1_2 = employees_1[1]
        e2_2 = employees_2[1]
        e1_2_schedule = Assign.objects.filter(employee=e1_2).filter(start_date=datetime.date(2019, 9, 4))
        e2_2_schedule = Assign.objects.filter(employee=e2_2).filter(start_date=datetime.date(2019, 9, 4))
        e1_2_switch = e1_2_schedule[0]
        e2_2_switch = e2_2_schedule[0]
        e1_2_switch.switch = True
        e2_2_switch.switch = True
        e1_2_switch.save()
        e2_2_switch.save()

        swapper = employees_1[0]
        status = sm.swap(swapper, datetime.datetime(2019, 9, 3, 19, 30))

        expected_status = {'success': True,
                           'available_shifts': e1_2_schedule,
                           'free_people': []
                           }
        self.assertEquals(status['success'], expected_status['success'])
        self.assertEquals(len(status['available_shifts']), len(expected_status['available_shifts']))
        for shift in range(len(status['available_shifts'])):
            self.assertEquals(status['available_shifts'][shift], expected_status['available_shifts'][shift])
        self.assertEquals(status['free_people'], expected_status['free_people'])

        # test feature for those open to swap. Employee.accept_swap = True
        # reset previous test
        e1_2_switch.switch = False
        e2_2_switch.switch = False
        e1_2_switch.save()
        e2_2_switch.save()

        e1_2.accept_swap = True
        e2_2.accept_swap = True
        e1_2.save()
        e2_2.save()

        status = sm.swap(swapper, datetime.datetime(2019, 9, 3, 19, 30))
        e1_2_schedule = Assign.objects.filter(employee=e1_2)

        expected_status = {'success': True,
                           'available_shifts': e1_2_schedule,
                           'free_people': []
                           }
        self.assertEquals(status['success'], expected_status['success'])
        self.assertEquals(len(status['available_shifts']), len(expected_status['available_shifts']))
        for shift in range(len(status['available_shifts'])):
            self.assertEquals(status['available_shifts'][shift], expected_status['available_shifts'][shift])
        self.assertEquals(status['free_people'], expected_status['free_people'])

        # test free people that are accepting shifts but cannot offer return
        _, _ = sm.set_schedule(person=swapper,
                               start_date=datetime.date(2019, 9, 4),
                               shift_pattern=shift_pattern_1)
        swapper_schedule = sm.get_schedule(swapper)
        print('##printing swapper schedule')
        for s in swapper_schedule:
            print(s.shift_start)
        print('##done printing swapper schedule')
        status = sm.swap(swapper, datetime.datetime(2019, 9, 3, 19, 30))
        print('status', status)
        expected_status = {'success': True,
                           'available_shifts': None,
                           'free_people': [e1_2]
                           }
        self.assertEquals(status['success'], expected_status['success'])
        self.assertEquals(status['available_shifts'], expected_status['available_shifts'])
        self.assertEquals(status['free_people'][0], expected_status['free_people'][0])


class ShiftModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _ = Shift.objects.create(shift_start=datetime.time(7, 30),
                                 shift_duration=datetime.timedelta(hours=12),
                                 shift_name='morning')
        _ = Shift.objects.create(shift_start=datetime.time(19, 30),
                                 shift_duration=datetime.timedelta(hours=12),
                                 shift_name='night')

    def test_shift_start_name_label(self):
        shift = Shift.objects.filter(shift_name__exact='morning')[0]
        field_label = shift._meta.get_field('shift_start').verbose_name
        self.assertEquals(field_label, 'shift start')


class ScheduleModelTest(TestCase):
    pass
