from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib.admin.models import LogEntry
from schedule.models import *
from people.models import *
from user.models import Group, EmployeeID, CustomUser
from project_specific.models import VacationNotification
from django.http import HttpResponseRedirect, HttpResponse
from .forms import GroupCreateForm, GroupJoinForm
import logging
import os
import json
import datetime
import pytz
from dateutil.parser import parse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    log_filename = 'logs/project_specific_views.log'
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
    file_handler = logging.handlers.TimedRotatingFileHandler(log_filename, when='midnight')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


@login_required
def profile_view(request):
    if request.method == 'POST':
        if request.POST.get("swap"):
            return HttpResponseRedirect(reverse('swap'))
    else:
        current_user = request.user
        if current_user.is_superuser:
            # if superuser, skip group join/create
            # superuser is not manager, and will not have group assigned
            return HttpResponseRedirect('/admin/')
        else:
            if not request.user.group:
                # cannot find group id because group doesnt exist yet
                return HttpResponseRedirect(reverse('group'))
            elif current_user.employee_detail.is_manager:
                # if not superuser and is manager, and has a group, redirect to admin
                return HttpResponseRedirect('manager/')

        # will throw index error if the user is not registered under Employee
        try:
            current_indv = Employee.objects.filter(user__exact=current_user)[0]

            schedule = get_schedule(current_indv)
            dates = []
            shift_start = []
            shift_end = []
            for s in schedule:
                dates.append(s.start_date.strftime("%Y/%m/%d"))
                shift_start.append(s.shift_start.strftime("%Y/%m/%d, %H:%M:%S"))
                shift_end.append(s.shift_end.strftime("%Y/%m/%d, %H:%M:%S"))

            context = {'dates': dates,
                       'shift_start': shift_start,
                       'shift_end': shift_end,
                       'name': current_user.first_name}
        except IndexError:
            context = {'name': 'Please register user in Employee'}
        return render(request, 'project_specific/index.html', context=context)


@login_required
def swap_view(request):
    """the view page for swapping shift"""
    if request.method == 'POST':
        str_data = request.body
        str_data = str_data.decode('utf-8')
        json_data = json.loads(str_data)
        if json_data['action'] == 'swap':
            shift_start_time = [parse(time) for time in json_data['data']]
            current_user = request.user
            person_instance = Employee.objects.filter(user__exact=current_user)[0]
            total_result = {}

            for start_time in shift_start_time:
                # check if shift is already being switched
                timezone_start_time = pytz.UTC.localize(start_time)
                exist_swap = SwapResult.objects.filter(
                    applicant=person_instance).filter(shift_start=timezone_start_time).exists()
                if not exist_swap:
                    result = swap(person=person_instance, swap_shift_start=start_time)
                    if result['success']:
                        if result['available_shifts']:
                            result['available_shifts'].order_by('employee', '-start_date')
                            result['available_shifts'] = [output_shift.json_format()
                                                          for output_shift in result['available_shifts']]
                        elif result['available_people']:
                            available_people = result['available_people']
                            available_people_dict = [{'receiver_employee_id': str(p.user.employee_detail.employee_id),
                                                      'receiver_first_name': str(p.user.first_name),
                                                      'receiver_last_name': str(p.user.last_name)} for p in
                                                     available_people]
                            result['available_people'] = available_people_dict
                    total_result[str(timezone_start_time)] = result
                    store_data = SwapResult(applicant=person_instance,
                                            shift_start=timezone_start_time,
                                            json_data=json.dumps(result))
                    store_data.save()
                else:
                    total_result[str(timezone_start_time)] = {'error': True,
                                                              'error_detail': 'shift is already being swapped'}
            return HttpResponse(json.dumps(total_result), content_type='application/json')
        elif json_data['action'] == 'cancel':
            cancel_shift_start = json_data['data']
            shift_start_time = parse(cancel_shift_start)
            current_user = request.user
            person_instance = Employee.objects.filter(user__exact=current_user)[0]
            status_detail = cancel_swap(person_instance, shift_start_time)
            return HttpResponse(json.dumps(status_detail), content_type='application/json')

    elif request.method == "GET":
        today = datetime.datetime.now().date()
        current_user = request.user
        person_instance = Employee.objects.filter(user__exact=current_user)[0]
        stored_data_query = SwapResult.objects.filter(applicant=person_instance).filter(
            action=False).filter(
            shift_start__gte=today).order_by('-shift_start')
        total_result = {str(stored_data.shift_start): json.loads(stored_data.json_data) for stored_data in
                        stored_data_query}
        return HttpResponse(json.dumps(total_result), content_type='application/json')


@login_required
def swap_request_view(request):
    if request.method == 'POST':
        str_data = request.body
        str_data = str_data.decode('utf-8')
        json_data = json.loads(str_data)
        if json_data['action'] == 'request':
            acceptor_data = json_data['data']

            acceptor_employee_id = int(acceptor_data['acceptor_employee_id'])
            acceptor_employee_detail = EmployeeID.objects.get(pk=acceptor_employee_id)
            acceptor_user = CustomUser.objects.get(employee_detail=acceptor_employee_detail)
            acceptor = Employee.objects.get(user=acceptor_user)

            current_user = request.user
            requester = Employee.objects.filter(user__exact=current_user)[0]
            requester_shift_start = parse(acceptor_data['requester_shift_start'])
            requester_shift = Assign.objects.filter(employee=requester).filter(shift_start=requester_shift_start)

            try:
                requester_swap_result = SwapResult.objects.filter(
                    applicant=requester).get(shift_start=requester_shift_start)
                requester_swap_result.action = True
                requester_swap_result.save()
            except Exception as e:
                status_detail = {'status': False,
                                 'acceptor_error': '',
                                 'requester_error': str(e),
                                 'already_exist': '',
                                 'data_type': json_data['data']['data_type']}
                return HttpResponse(json.dumps(status_detail), content_type='application/json')
            if json_data['data']['data_type'] == 'shift':
                print('json data', json_data['data'])
                acceptor_shift_start = parse(acceptor_data['acceptor_shift_start'])
                acceptor_shift = Assign.objects.filter(employee=acceptor).filter(shift_start=acceptor_shift_start)
                acceptor_error = Assign.assure_one_and_same(acceptor_shift, acceptor_shift_start, acceptor)
                requester_error = Assign.assure_one_and_same(requester_shift, requester_shift_start, requester)
                if not (acceptor_error and requester_error):
                    request_exist = Request.objects.filter(applicant=requester).filter(
                        applicant_schedule=requester_shift[0]).exists()
                    vice_versa_request_exist = Request.objects.filter(applicant=acceptor).filter(
                        applicant_schedule=acceptor_shift[0]).exists()
                    if not (request_exist or vice_versa_request_exist):
                        request_queue = Request(applicant=requester,
                                                receiver=acceptor,
                                                applicant_schedule=requester_shift[0],
                                                receiver_schedule=acceptor_shift[0],
                                                manager=requester.user.group.owner)
                        request_queue.save()
                        status_detail = {'status': True,
                                         'acceptor_error': acceptor_error,
                                         'requester_error': requester_error,
                                         'already_exist': (request_exist or vice_versa_request_exist)}
                    else:
                        status_detail = {'status': False,
                                         'acceptor_error': acceptor_error,
                                         'requester_error': requester_error,
                                         'already_exist': (request_exist or vice_versa_request_exist)}
                else:
                    status_detail = {'status': False,
                                     'acceptor_error': acceptor_error,
                                     'requester_error': requester_error,
                                     'already_exist': ''}
            elif json_data['data']['data_type'] == 'people':
                request_exist = Request.objects.filter(applicant=requester).filter(
                    applicant_schedule=requester_shift[0]).exists()

                if not request_exist:
                    request_queue = Request(applicant=requester,
                                            receiver=acceptor,
                                            applicant_schedule=requester_shift[0],
                                            receiver_schedule=None,
                                            manager=requester.user.group.owner)
                    request_queue.save()
                    status_detail = {'status': True,
                                     'acceptor_error': '',
                                     'requester_error': '',
                                     'already_exist': request_exist}
                else:
                    status_detail = {'status': False,
                                     'acceptor_error': '',
                                     'requester_error': '',
                                     'already_exist': request_exist}
            status_detail['data_type'] = json_data['data']['data_type']
            return HttpResponse(json.dumps(status_detail), content_type='application/json')
        elif json_data['action'] == 'cancel':
            created_timestamp = json_data['data']['created']
            created_timestamp = parse(created_timestamp)
            requester_shift_start = json_data['data']['requester_shift_start']
            requester_shift_start = parse(requester_shift_start)

            current_user = request.user
            requester = Employee.objects.filter(user__exact=current_user)[0]
            try:
                request_instance = Request.objects.filter(applicant=requester).get(created=created_timestamp)
                request_instance.delete()
                error_detail = ''
                status = True
                requester_swap_result = SwapResult.objects.filter(
                    applicant=requester).get(shift_start=requester_shift_start)
                requester_swap_result.action = False
                requester_swap_result.save()
            except Exception as e:
                error_detail = e
                status = False
            status_detail = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(status_detail), content_type='application/json')
        elif json_data['action'] == 'reject':
            created_timestamp = json_data['data']['created']
            created_timestamp = parse(created_timestamp)

            requester_employee_id = int(json_data['data']['requester_employee_id'])
            requester_employee_detail = EmployeeID.objects.get(pk=requester_employee_id)
            requester_user = CustomUser.objects.get(employee_detail=requester_employee_detail)
            requester = Employee.objects.get(user=requester_user)

            swap_request = Request.objects.filter(
                applicant=requester).get(created=created_timestamp)

            swap_request.manager_responded = True
            swap_request.save()
            print('action done')
            return HttpResponse('request rejected')

        elif json_data['action'] == 'finalize':
            created_timestamp = json_data['data']['created']
            created_timestamp = parse(created_timestamp)

            requester_shift_start = json_data['data']['requester_shift_start']
            requester_shift_start = parse(requester_shift_start)

            acceptor_shift_start = json_data['data']['acceptor_shift_start']
            if acceptor_shift_start:
                acceptor_shift_start = parse(acceptor_shift_start)

            acceptor_employee_id = int(json_data['data']['acceptor_employee_id'])
            acceptor_employee_detail = EmployeeID.objects.get(pk=acceptor_employee_id)
            acceptor_user = CustomUser.objects.get(employee_detail=acceptor_employee_detail)
            acceptor = Employee.objects.get(user=acceptor_user)

            requester_employee_id = int(json_data['data']['requester_employee_id'])
            requester_employee_detail = EmployeeID.objects.get(pk=requester_employee_id)
            requester_user = CustomUser.objects.get(employee_detail=requester_employee_detail)
            requester = Employee.objects.get(user=requester_user)

            try:
                status, error_detail = Assign.finalize_swap(requester=requester,
                                                            requester_shift_start=requester_shift_start,
                                                            acceptor=acceptor,
                                                            acceptor_shift_start=acceptor_shift_start,
                                                            request_timestamp=created_timestamp)
            except Exception as e:
                error_detail = str(e)
                status = False
            status_detail = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(status_detail), content_type='application/json')

    elif request.method == 'GET':
        current_user = request.user
        requester = Employee.objects.get(user=current_user)
        current_requests = Request.objects.filter(applicant=requester)
        total_requests = {}
        for processing in current_requests:
            applicant_schedule = processing.applicant_schedule
            receiver_schedule = processing.receiver_schedule
            if receiver_schedule:
                total_requests[str(processing.created)] = {'applicant_shift_start': str(applicant_schedule.shift_start),
                                                           'applicant_shift_end': str(applicant_schedule.shift_end),
                                                           'receiver_shift_start': str(receiver_schedule.shift_start),
                                                           'receiver_shift_end': str(receiver_schedule.shift_end),
                                                           'receiver_employee_id': str(
                                                               processing.receiver.user.employee_detail.employee_id),
                                                           'accept': processing.accept,
                                                           'responded': processing.responded,
                                                           'created': str(processing.created),
                                                           'manager_responded': str(processing.manager_responded)}
            else:
                total_requests[str(processing.created)] = {'applicant_shift_start': str(applicant_schedule.shift_start),
                                                           'applicant_shift_end': str(applicant_schedule.shift_end),
                                                           'receiver_shift_start': '',
                                                           'receiver_shift_end': '',
                                                           'receiver_employee_id': str(
                                                               processing.receiver.user.employee_detail.employee_id),
                                                           'accept': processing.accept,
                                                           'responded': processing.responded,
                                                           'created': str(processing.created),
                                                           'manager_responded': str(processing.manager_responded)
                                                           }
        return HttpResponse(json.dumps(total_requests), content_type='application/json')


@login_required
def receive_request_view(request):
    if request.method == "POST":
        str_data = request.body
        str_data = str_data.decode('utf-8')
        json_data = json.loads(str_data)
        status = True
        error_detail = ''

        try:
            applicant_employee_id = int(json_data['data']['applicant_employee_id'])
            applicant_employee_detail = EmployeeID.objects.get(pk=applicant_employee_id)
            applicant_user = CustomUser.objects.get(employee_detail=applicant_employee_detail)
            applicant = Employee.objects.get(user=applicant_user)
            created_time = json_data['data']['created']
            created_time = parse(created_time)

            # this should be enough to get unique Request object
            # implement requester employee id...
            request_instance = Request.objects.filter(applicant=applicant).get(created=created_time)
            if json_data['action'] == 'accept':
                request_instance.responded = True
                request_instance.accept = True
                request_instance.save()
            elif json_data['action'] == 'reject':
                request_instance.responded = True
                request_instance.save()
        except Exception as e:
            error_detail = str(e)
            status = False

        status_detail = {'status': status, 'error_detail': error_detail}
        return HttpResponse(json.dumps(status_detail), content_type='application/json')

    elif request.method == "GET":
        current_user = request.user
        requester = Employee.objects.get(user=current_user)
        current_requests = Request.objects.filter(receiver=requester).filter(responded=False)
        total_requests = {}
        for processing in current_requests:
            applicant_schedule = processing.applicant_schedule
            receiver_schedule = processing.receiver_schedule
            if receiver_schedule:
                total_requests[str(processing.created)] = {'applicant_shift_start': str(applicant_schedule.shift_start),
                                                           'applicant_shift_end': str(applicant_schedule.shift_end),
                                                           'receiver_shift_start': str(receiver_schedule.shift_start),
                                                           'receiver_shift_end': str(receiver_schedule.shift_end),
                                                           'receiver_employee_id': str(
                                                               processing.receiver.user.employee_detail.employee_id),
                                                           'applicant_employee_id': str(
                                                               processing.applicant.user.employee_detail.employee_id
                                                           ),
                                                           'accept': processing.accept,
                                                           'responded': processing.responded,
                                                           'created': str(processing.created)}
            else:
                total_requests[str(processing.created)] = {'applicant_shift_start': str(applicant_schedule.shift_start),
                                                           'applicant_shift_end': str(applicant_schedule.shift_end),
                                                           'receiver_shift_start': '',
                                                           'receiver_shift_end': '',
                                                           'receiver_employee_id': str(
                                                               processing.receiver.user.employee_detail.employee_id),
                                                           'applicant_employee_id': str(
                                                               processing.applicant.user.employee_detail.employee_id
                                                           ),
                                                           'accept': processing.accept,
                                                           'responded': processing.responded,
                                                           'created': str(processing.created)}

        return HttpResponse(json.dumps(total_requests), content_type='application/json')


@login_required
def group_view(request):
    """this page is to register the group if the user is currently unregistered. Note superuser remains unregistered"""
    if request.method == 'POST':
        if request.POST.get('create_submit'):
            form = GroupCreateForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                name = form.cleaned_data['name']
                group = Group(owner=request.user, name=name, password=password)
                group.save()
                print('group id:', group.id)
                request.user.group = group
                request.user.save()

                # return to join group page
                return HttpResponseRedirect(reverse('profile'))
        elif request.POST.get('join_submit'):
            form = GroupJoinForm(request.POST)
            if form.is_valid():
                group_id = form.cleaned_data['group_id']

                group = Group.objects.get(pk=group_id)

                request.user.group = group
                request.user.save()

                return HttpResponseRedirect(reverse('profile'))

    else:
        if request.user.employee_detail.is_manager:
            # render a group creating form
            form = GroupCreateForm()
            context = {'form': form}
            return render(request, 'project_specific/group_create.html', context=context)
        else:
            # render a join group form
            form = GroupJoinForm()
            context = {'form': form}
            return render(request, 'project_specific/group_join.html', context=context)


@login_required
def vacation_view(request):
    if request.method == 'POST':
        str_data = request.body
        str_data = str_data.decode('utf-8')
        json_data = json.loads(str_data)
        if json_data['action'] == 'request_vacation':
            vacation_date = [parse(date).date() for date in json_data['data']]
            current_user = request.user
            person_instance = get_object_or_404(Employee, user=current_user)
            manager_instance = person_instance.group.owner
            person_schedule = Assign.objects.filter(employee=person_instance)
            exist_vacation = VacationNotification.objects.filter(requester=person_instance)
            exist_vacation_set = set()
            for exist_request in exist_vacation:
                exist_vacation_set.add(exist_request.date)
            unregistered_vacation = set(vacation_date) - exist_vacation_set
            overlap_requests = set(vacation_date).intersection(exist_vacation_set)
            for vacation in unregistered_vacation:
                schedule_conflict = person_schedule.filter(start_date=vacation).exists()
                notification = VacationNotification(requester=person_instance,
                                                    assignee=manager_instance,
                                                    date=vacation,
                                                    schedule_conflict=schedule_conflict)
                notification.save()
            json_overlap_requests = [str(d) for d in list(overlap_requests)]
            json_registered_vacation = [str(d) for d in list(unregistered_vacation)]
            data = {'overlap_requests': json_overlap_requests,
                    'registered_vacation': json_registered_vacation}
            return HttpResponse(json.dumps(data), content_type='application/json')
        elif json_data['action'] == 'cancel':
            status = True
            error_detail = ''
            try:
                vacation_date = parse(json_data['data']['vacation_date'])
                current_user = request.user
                person_instance = get_object_or_404(Employee, user=current_user)
                vacation_instance = VacationNotification.objects.filter(requester=person_instance).get(
                    date=vacation_date)
                vacation_instance.delete()
            except Exception as e:
                status = False
                error_detail = str(e)
            status_detail = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(status_detail), content_type='application/json')

    if request.method == 'GET':
        current_user = request.user
        person_instance = get_object_or_404(Employee, user=current_user)
        today = datetime.datetime.now().date()
        vacation_requests = VacationNotification.objects.filter(requester=person_instance).filter(
            date__gte=today).order_by('-date')
        total_response = {}
        response = {}
        for vacation_request in vacation_requests:
            response[str(vacation_request.date)] = {'Approved': vacation_request.approved,
                                                    'Responded': vacation_request.responded,
                                                    'Delivered': vacation_request.delivered}
        approved_vacation = Vacation.objects.filter(employee=person_instance)
        approved_dates = [str(v.date) for v in approved_vacation]
        total_response['queue'] = response
        total_response['approved'] = approved_dates

        return HttpResponse(json.dumps(total_response), content_type='application/json')


@user_passes_test(lambda u: u.groups.filter(name='Manager').exists())
def schedule_view(request):
    """
    schedule view is for manager only

    :param request:
    :return:
    """
    if request.method == "POST":
        pass
    elif request.method == 'GET':
        if request.GET['action'] == 'single_person':
            start_date = parse(request.GET['date_range[start_date]'])
            end_date = parse(request.GET['date_range[end_date]'])
            employee_id = request.GET['employee_id']
            employee = Employee.get_employee_instance(employee_id)
            employee_schedule = Assign.objects.filter(employee=employee).filter(
                start_date__gte=start_date).filter(start_date__lte=end_date)
            json_employee_schedule = [s.json_format() for s in employee_schedule]

            employee_vacation = Vacation.objects.filter(employee=employee).filter(
                date__gte=start_date).filter(date__lte=end_date)
            json_employee_vacation = [str(v.date) for v in employee_vacation]
            output = {'schedules': json_employee_schedule,
                      'vacations': json_employee_vacation}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif request.GET['action'] == 'all_employees':
            start_date = parse(request.GET['date_range[start_date]'])
            end_date = parse(request.GET['date_range[end_date]'])
            # get employee belonging to manager
            employees = Employee.objects.all().filter(group=request.user.group)
            employee_schedule = Assign.objects.filter(
                employee__in=employees).filter(
                start_date__gte=start_date).filter(start_date__lte=end_date)
            json_employee_schedule = Assign.schedule_sort(employee_schedule)
            return HttpResponse(json.dumps(json_employee_schedule), content_type='application/json')


@user_passes_test(lambda u: u.groups.filter(name='Manager').exists())
def manager_profile_view(request):
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        return render(request, 'project_specific/manager_profile.html')


@user_passes_test(lambda u: u.groups.filter(name='Manager').exists())
def manager_vacation_view(request):
    if request.method == 'POST':
        str_data = request.body
        str_data = str_data.decode('utf-8')
        json_data = json.loads(str_data)
        status = True
        error_detail = ''
        try:
            requester_employee_id = int(json_data['data']['requester_employee_id'])
            requester_employee_detail = EmployeeID.objects.get(pk=requester_employee_id)
            requester_user = CustomUser.objects.get(employee_detail=requester_employee_detail)
            requester = Employee.objects.get(user=requester_user)

            request_date = parse(json_data['data']['request_date'])
            vacation = VacationNotification.objects.filter(expired=False).filter(
                assignee=request.user).filter(requester=requester).get(date=request_date)
            vacation.responded = True
            if json_data['action'] == 'accept':
                vacation.approved = True
                set_vacation = Vacation(date=request_date,
                                        employee=requester,
                                        group=requester.group)
                set_vacation.save()
            elif json_data['action'] == 'reject':
                pass
            vacation.save()
        except Exception as e:
            status = False
            error_detail = str(e)

        output = {'status': status, 'error_detail': error_detail}
        return HttpResponse(json.dumps(output), content_type='application/json')

    elif request.method == 'GET':
        current_user = request.user
        unchecked_vacation = VacationNotification.objects.filter(
            assignee=current_user).filter(approved=False).filter(responded=False)
        for v in unchecked_vacation:
            v.delivered = True
            v.save()
        total_unchecked_list = [v.json_format() for v in unchecked_vacation]
        return HttpResponse(json.dumps(total_unchecked_list), content_type='application/json')


@user_passes_test(lambda u: u.groups.filter(name='Manager').exists())
def manager_request_view(request):
    if request.method == 'POST':
        pass
    elif request.method == "GET":
        current_user = request.user
        unanswered_requests = Request.objects.filter(
            manager=current_user).filter(manager_responded=False).filter(responded=True)
        total_response = [v.json_format() for v in unanswered_requests]
        return HttpResponse(json.dumps(total_response), content_type='application/json')


@user_passes_test(lambda u: u.groups.filter(name='Manager').exists())
def manager_assign_view(request):
    if request.method == "POST":
        current_user = request.user
        str_data = request.body
        str_data = str_data.decode('utf-8')
        json_data = json.loads(str_data)

        get_employee_id = json_data.get('employee_id')
        if get_employee_id:
            employee_id = int(get_employee_id)
            employee_detail = EmployeeID.objects.get(pk=employee_id)
            employee_user = CustomUser.objects.get(employee_detail=employee_detail)
            employee = Employee.objects.get(user=employee_user)

        if json_data['action'] == 'assign_day_shift_based':
            shift_instance = Shift.objects.get(pk=int(json_data['shift_pk']))
            status, status_detail = set_schedule_day(person=employee,
                                                     start_day=parse(json_data['start_date']),
                                                     shift=shift_instance,
                                                     override=json_data['override'])
            output = {'status': status,
                      'status_detail': status_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'assign_day_time_based':
            shift_start_time = parse(json_data['shift_start']).time()
            shift_end_time = parse(json_data['shift_end']).time()
            shift_day = parse(json_data['start_date'])
            shift_start = datetime.datetime.combine(shift_day, shift_start_time)
            shift_end = datetime.datetime.combine(shift_day, shift_end_time)
            status, status_detail = set_schedule_day(person=employee,
                                                     start_day=parse(json_data['start_date']),
                                                     shift_start=shift_start,
                                                     shift_end=shift_end,
                                                     override=json_data['override'])
            output = {'status': status,
                      'status_detail': status_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'assign_schedule':
            schedule_instance = Schedule.objects.get(pk=int(json_data['schedule_pk']))
            status, status_detail = set_schedule(person=employee,
                                                 start_date=parse(json_data['start_date']),
                                                 shift_pattern=schedule_instance,
                                                 repeat=int(json_data['repeat']),
                                                 override=json_data['override'])
            output = {'status': status,
                      'status_detail': status_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'override_assign_schedule':
            employee_data = json_data['employee_data']
            overridable_schedules = employee_data['overridable']
            total_status = []
            total_status_detail = {'overridable': [],
                                   'non_overridable': [],
                                   'holiday': [],
                                   'args': employee_data['args']}
            for o in overridable_schedules:
                start_datetime = parse(o[0])
                shift_type = Shift.objects.get(pk=int(o[2]))
                status, status_detail = set_schedule_day(person=employee,
                                                         start_day=start_datetime.date(),
                                                         shift=shift_type,
                                                         override=True)
                total_status.append(status)
                total_status_detail['overridable'].extend(status_detail['overridable'])
                total_status_detail['non_overridable'].extend(status_detail['non_overridable'])
                total_status_detail['holiday'].extend(status_detail['holiday'])
            output = {'status': all(total_status),
                      'status_detail': total_status_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'group_set_schedule':
            employees_id_list = json_data['employees_id_list']
            employee_user_list = [CustomUser.get_employee_user(eid) for eid in employees_id_list]
            employees_queryset = Employee.objects.filter(
                group=current_user.group).filter(user__in=employee_user_list)
            schedule_instance = Schedule.objects.get(pk=int(json_data['schedule_pk']))
            total_status_detail = group_set_schedule(employees=employees_queryset,
                                                     shift_pattern=schedule_instance,
                                                     start_date=parse(json_data['start_date']),
                                                     workers_per_day=int(json_data['workers_per_day']),
                                                     day_length=int(json_data['day_length']))
            return HttpResponse(json.dumps(total_status_detail), content_type='application/json')
        elif json_data['action'] == 'override_auto_assign':
            employee_data = json_data['employee_data']
            employee_instance = Employee.objects.get(pk=int(json_data['employee_pk']))
            total_status = []
            total_status_detail = {'overridable': [],
                                   'non_overridable': [],
                                   'holiday': [],
                                   'args': employee_data['args']}
            for o in employee_data['overridable']:
                start_datetime = parse(o[0])
                shift_type = Shift.objects.get(pk=int(o[2]))
                status, status_detail = set_schedule_day(person=employee_instance,
                                                         start_day=start_datetime.date(),
                                                         shift=shift_type,
                                                         override=True)
                total_status.append(status)
                total_status_detail['overridable'].extend(status_detail['overridable'])
                total_status_detail['non_overridable'].extend(status_detail['non_overridable'])
                total_status_detail['holiday'].extend(status_detail['holiday'])
            output = {'status': all(total_status),
                      'status_detail': total_status_detail,
                      'employee_name': str(employee_instance)}
            return HttpResponse(json.dumps(output), content_type='application/json')

    elif request.method == 'GET':
        current_user = request.user
        manager_group = current_user.group
        own_employees = Employee.objects.filter(group=manager_group).order_by('person_unit')
        json_own_employees = [e.json_format() for e in own_employees]

        own_shifts = Shift.objects.filter(group=manager_group).order_by('shift_start')
        json_own_shifts = [s.json_format() for s in own_shifts]

        own_schedules = Schedule.objects.filter(group=manager_group).order_by('schedule_name')
        json_own_schedules = [s.json_format() for s in own_schedules]
        return render(request, 'project_specific/manager_assign.html', context={'employees': json_own_employees,
                                                                                'shifts': json_own_shifts,
                                                                                'schedules': json_own_schedules})


@user_passes_test(lambda u: u.groups.filter(name='Manager').exists())
def manager_people_view(request):
    if request.method == "POST":
        current_user = request.user
        str_data = request.body
        str_data = str_data.decode('utf-8')
        json_data = json.loads(str_data)
        status = True
        error_detail = ''
        if json_data['action'] == 'create_unit':
            try:
                new_unit = Unit(unit_choice=json_data['unit_name'],
                                group=current_user.group)
                new_unit.save()
            except Exception as e:
                status = False
                error_detail = str(e)

            output = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'create_position':
            try:
                new_pos = Position(position_choice=json_data['position_name'],
                                   group=current_user.group)
                new_pos.save()
            except Exception as e:
                status = False
                error_detail = str(e)
            output = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'create_employee':
            try:
                employee_id = int(json_data['employee_id'])
                employee_detail = EmployeeID.objects.get(pk=employee_id)
                employee_user = CustomUser.objects.get(employee_detail=employee_detail)

                employee_position = Position.objects.get(pk=int(json_data['position_pk']))
                employee_unit = Unit.objects.get(pk=int(json_data['unit_pk']))

                new_employee = Employee(user=employee_user,
                                        person_position=employee_position,
                                        person_unit=employee_unit,
                                        group=current_user.group,
                                        date_joined=parse(json_data['date_joined']))
                new_employee.save()
                for i in json_data['workday_pk']:
                    workday_instance = Workday.objects.get(day=int(i))
                    new_employee.workday.add(workday_instance)
                new_employee.save()
            except Exception as e:
                status = False
                error_detail = str(e)
            output = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'delete_unit':
            try:
                unit_pk_list = json_data['unit_pks']
                unit_pk_list = [int(p) for p in unit_pk_list]

                unit_list = Unit.objects.filter(pk__in=unit_pk_list)
                unit_list.delete()
            except Exception as e:
                status = False
                error_detail = str(e)
            output = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'delete_position':
            try:
                position_pk_list = json_data['position_pks']
                position_pk_list = [int(p) for p in position_pk_list]

                position_list = Position.objects.filter(pk__in=position_pk_list)
                position_list.delete()
            except Exception as e:
                status = False
                error_detail = str(e)
            output = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'delete_employee':
            try:
                employee_id_list = json_data['employee_ids']
                employee_list = [Employee.get_employee_instance(p) for p in employee_id_list]
                for e in employee_list:
                    e.delete()

            except Exception as e:
                status = False
                error_detail = str(e)
            output = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')

    elif request.method == "GET":
        current_user = request.user
        manager_group = current_user.group
        own_unit = Unit.objects.filter(group=manager_group)
        json_own_unit = [u.json_format() for u in own_unit]

        own_position = Position.objects.filter(group=manager_group)
        json_own_position = [p.json_format() for p in own_position]

        own_employees = Employee.objects.filter(group=manager_group).order_by('person_unit')
        json_own_employees = [e.json_format() for e in own_employees]

        workday_pref = Workday.objects.all()
        json_workday_pref = [w.json_format() for w in workday_pref]

        unregistered_user = CustomUser.objects.filter(is_superuser=False).filter(group=None)
        json_unregistered_user = [u.json_format() for u in unregistered_user]

        action_logs = LogEntry.objects.filter(user=current_user)[:10]
        short_action_logs = json.dumps([[l.object_repr, l.action_flag] for l in action_logs])

        return render(request, 'project_specific/manager_people.html', context={'unit': json_own_unit,
                                                                                'position': json_own_position,
                                                                                'employees': json_own_employees,
                                                                                'users': json_unregistered_user,
                                                                                'workdays': json_workday_pref,
                                                                                'action_logs': short_action_logs})

@user_passes_test(lambda u: u.groups.filter(name='Manager').exists())
def manager_employee_view(request):
    if request.method == "POST":
        str_data = request.body
        str_data = str_data.decode('utf-8')
        json_data = json.loads(str_data)
        status = True
        error_detail = ''
        if json_data['action'] == 'delete_employee_shift':
            try:
                employee = Employee.get_employee_instance(int(json_data['employee_id']))
                employee_shift = Assign.objects.filter(employee=employee).get(shift_start=parse(json_data['shift_start']))
                employee_shift.delete()
            except Exception as e:
                error_detail = str(e)
                status = False
            status_detail = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(status_detail), content_type='application/json')
    if request.method == "GET":
        current_user = request.user
        manager_group = current_user.group
        own_unit = Unit.objects.filter(group=manager_group)
        json_own_unit = [u.json_format() for u in own_unit]

        own_position = Position.objects.filter(group=manager_group)
        json_own_position = [p.json_format() for p in own_position]

        own_employees = Employee.objects.filter(group=manager_group).order_by('person_unit')
        json_own_employees = [e.json_format() for e in own_employees]

        workday_pref = Workday.objects.all()
        json_workday_pref = [w.json_format() for w in workday_pref]

        unregistered_user = CustomUser.objects.filter(is_superuser=False)
        json_unregistered_user = [u.json_format() for u in unregistered_user]

        return render(request, 'project_specific/manager_view.html', context={'unit': json_own_unit,
                                                                                'position': json_own_position,
                                                                                'employees': json_own_employees,
                                                                                'users': json_unregistered_user,
                                                                                'workdays': json_workday_pref})


@user_passes_test(lambda u: u.groups.filter(name='Manager').exists())
def manager_schedule_view(request):
    if request.method == 'POST':
        current_user = request.user
        str_data = request.body
        str_data = str_data.decode('utf-8')
        json_data = json.loads(str_data)
        status = True
        error_detail = ''
        if json_data['action'] == 'create_shift':

            try:
                new_shift = Shift(shift_start=parse(json_data['shift_start_time']),
                                  shift_name=json_data['shift_name'],
                                  shift_duration=datetime.timedelta(hours=int(json_data['shift_dur_hr']),
                                                                    minutes=int(json_data['shift_dur_min'])),
                                  group=current_user.group)
                new_shift.save()
            except Exception as e:
                status = False
                error_detail = str(e)

            output = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'create_schedule':
            try:
                shift_pk = json_data['shift_pk']
                print(shift_pk)
                adding_shifts = []
                for shift in shift_pk:
                    if shift:
                        s = Shift.objects.get(pk=shift)
                        adding_shifts.append(s)
                    else:
                        adding_shifts.append(None)
                print(adding_shifts)
                new_schedule = Schedule(schedule_name=json_data['schedule_name'],
                                        cycle=json_data['cycle'],
                                        day_1=adding_shifts[0],
                                        day_2=adding_shifts[1],
                                        day_3=adding_shifts[2],
                                        group=current_user.group)
                new_schedule.save()
            except Exception as e:
                status = False
                error_detail = str(e)

            output = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'delete_shift':
            try:
                shift_pk_list = json_data['shift_pks']
                shift_pk_list = [int(p) for p in shift_pk_list]

                shift_list = Shift.objects.filter(pk__in=shift_pk_list)
                shift_list.delete()
            except Exception as e:
                status = False
                error_detail = str(e)
            output = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
        elif json_data['action'] == 'delete_schedule':
            try:
                schedule_pk_list = json_data['schedule_pks']
                schedule_pk_list = [int(p) for p in schedule_pk_list]

                schedule_list = Schedule.objects.filter(pk__in=schedule_pk_list)
                schedule_list.delete()
            except Exception as e:
                status = False
                error_detail = str(e)
            output = {'status': status, 'error_detail': error_detail}
            return HttpResponse(json.dumps(output), content_type='application/json')
    elif request.method == "GET":
        current_user = request.user
        manager_group = current_user.group
        own_shift = Shift.objects.filter(group=manager_group)
        json_own_shift = [s.json_format() for s in own_shift]
        own_schedule = Schedule.objects.filter(group=manager_group)
        json_own_schedule = [s.json_format() for s in own_schedule]

        action_logs = LogEntry.objects.filter(user=current_user)[:10]
        short_action_logs = json.dumps([[l.object_repr, l.action_flag] for l in action_logs])
        return render(request, 'project_specific/manager_schedule.html', context={'shifts': json_own_shift,
                                                                                  'schedules': json_own_schedule,
                                                                                  'action_logs': short_action_logs})


def logout_view(request):
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        logout(request)
        return render(request, 'registration/logged_out.html')
