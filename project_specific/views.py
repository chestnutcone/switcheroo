from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from schedule.models import get_schedule, swap, SwapResult, cancel_swap, Request, Assign
from people.models import Employee
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

        if request.POST.get("logout"):
            logout(request)
            return render(request, 'registration/logged_out.html')
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
                return HttpResponseRedirect('/admin/')

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
        if request.POST.get("logout"):
            logout(request)
            return render(request, 'registration/logged_out.html')
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
                result = swap(person=person_instance, swap_shift_start=start_time)
                if result['success']:
                    result['available_shifts'].order_by('employee', '-start_date')
                    result['available_shifts'] = [output_shift.json_format()
                                                  for output_shift in result['available_shifts']]
                total_result[str(timezone_start_time)] = result
                store_data = SwapResult(applicant=person_instance,
                                        shift_start=timezone_start_time,
                                        json_data=json.dumps(result))
                store_data.save()
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
        total_result = {str(stored_data.shift_start): json.loads(stored_data.json_data) for stored_data in stored_data_query}
        return HttpResponse(json.dumps(total_result), content_type='application/json')


@login_required
def swap_request_view(request):
    if request.method == 'POST':
        if request.POST.get("logout"):
            logout(request)
            return render(request, 'registration/logged_out.html')
        str_data = request.body
        str_data = str_data.decode('utf-8')
        json_data = json.loads(str_data)
        if json_data['action'] == 'request':
            acceptor_data = json_data['data']
            acceptor_shift_start = parse(acceptor_data['acceptor_shift_start'])
            acceptor_employee_id = int(acceptor_data['acceptor_employee_id'])
            acceptor_employee_detail = EmployeeID.objects.get(pk=acceptor_employee_id)
            acceptor_user = CustomUser.objects.get(employee_detail=acceptor_employee_detail)
            acceptor = Employee.objects.get(user=acceptor_user)
            acceptor_shift = Assign.objects.filter(employee=acceptor).filter(shift_start=acceptor_shift_start)

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
                status_detail = {'status': True,
                                 'acceptor_error': '',
                                 'requester_error': e,
                                 'already_exist': ''}
                return HttpResponse(json.dumps(status_detail), content_type='application/json')

            acceptor_error = Assign.assure_one_and_same(acceptor_shift, acceptor_shift_start, acceptor)
            requester_error = Assign.assure_one_and_same(requester_shift, requester_shift_start, requester)

            if not (acceptor_error and requester_error):
                request_exist = Request.objects.filter(applicant=requester).filter(
                    applicant_schedule=requester_shift[0]).exists()
                if not request_exist:
                    request_queue = Request(applicant=requester,
                                            receiver=acceptor,
                                            applicant_schedule=requester_shift[0],
                                            receiver_schedule=acceptor_shift[0])
                    request_queue.save()
                    status_detail = {'status': True,
                                     'acceptor_error': acceptor_error,
                                     'requester_error': requester_error,
                                     'already_exist': request_exist}
                else:
                    status_detail = {'status': False,
                                     'acceptor_error': acceptor_error,
                                     'requester_error': requester_error,
                                     'already_exist': request_exist}
                return HttpResponse(json.dumps(status_detail), content_type='application/json')
            else:
                status_detail = {'status': False,
                                 'acceptor_error': acceptor_error,
                                 'requester_error': requester_error,
                                 'already_exist': ''}
                return HttpResponse(json.dumps(status_detail), content_type='application/json')
        elif json_data['action'] == 'cancel':
            print(json_data)
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

    elif request.method == 'GET':
        current_user = request.user
        requester = Employee.objects.get(user=current_user)
        current_requests = Request.objects.filter(applicant=requester)
        total_requests = {}
        for processing in current_requests:
            applicant_schedule = processing.applicant_schedule
            receiver_schedule = processing.receiver_schedule
            total_requests[str(processing.created)] = {'applicant_shift_start': str(applicant_schedule.shift_start),
                                                       'applicant_shift_end': str(applicant_schedule.shift_end),
                                                       'receiver_shift_start': str(receiver_schedule.shift_start),
                                                       'receiver_shift_end': str(receiver_schedule.shift_end),
                                                       'accept': processing.accept,
                                                       'responded': processing.responded,
                                                       'created': str(processing.created)}
        return HttpResponse(json.dumps(total_requests), content_type='application/json')


@login_required
def swap_result_view(request):
    """redirect here after swap_view"""
    if request.method == 'POST':
        if request.POST.get("logout"):
            logout(request)
            return render(request, 'registration/logged_out.html')
        if request.POST.get("swap"):
            ### this is not finished, not sure how to proceed after a user request a swap with another user
            ### Ie if user A choose box 1 to request swap with user B, how will I know which one is selected?
            ### depends on front end?
            index = request.POST['swap_box']
            print(index)

            return HttpResponseRedirect(reverse('swap'))
    else:
        if request.GET.get("home"):
            return HttpResponseRedirect(reverse('profile'))
        else:
            return render(request, 'project_specific/swap_result.html')


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

            vacation_date = [datetime.datetime.strptime(date, "%Y/%m/%d").date() for date in json_data['data']]
            current_user = request.user
            person_instance = get_object_or_404(Employee, user=current_user)
            manager_instance = person_instance.group.owner
            for vacation in vacation_date:
                notification = VacationNotification(requester=person_instance,
                                                    assignee=manager_instance,
                                                    date=vacation)
                notification.save()
            return HttpResponse('registered')
    if request.method == 'GET':
        current_user = request.user
        person_instance = get_object_or_404(Employee, user=current_user)
        today = datetime.datetime.now().date()
        vacation_requests = VacationNotification.objects.filter(requester=person_instance).filter(
            date__gte=today).order_by('-date')
        response = {}
        for vacation_request in vacation_requests:
            response[str(vacation_request.date)] = {'approved': vacation_request.approved,
                                                    'rejected': vacation_request.rejected,
                                                    'delivered': vacation_request.delivered}
        return HttpResponse(json.dumps(response), content_type='application/json')


@user_passes_test(lambda u: u.groups.filter(name='Manager').exists())
def schedule_view(request):
    """
    schedule view is for manager only

    :param request:
    :return:
    """
    if request.method == "POST":
        if request.POST.get("logout"):
            logout(request)
            return render(request, 'registration/logged_out.html')

    else:
        # get employee belonging to manager
        employees = Employee.objects.all().filter(group=request.user.group)
        total_schedule = {'name': request.user.first_name, 'schedules': []}
        for employee in employees:
            try:
                schedule = get_schedule(employee)
                if schedule:
                    dates = []
                    shift_start = []
                    shift_end = []
                    for s in schedule:
                        dates.append(s.start_date.strftime("%Y/%m/%d"))
                        shift_start.append(s.shift_start.strftime("%Y/%m/%d, %H:%M:%S"))
                        shift_end.append(s.shift_end.strftime("%Y/%m/%d, %H:%M:%S"))
                    context = {
                        'dates': dates,
                        'shift_start': shift_start,
                        'shift_end': shift_end,
                        'name': str(employee),
                    }
                    total_schedule['schedules'].append(context)
            except IndexError:
                logger.exception('some error occured in schedule_view')

        return render(request, 'project_specific/manager_schedules_view.html', context=total_schedule)
