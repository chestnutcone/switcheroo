from django.shortcuts import render
from schedule.models import Schedule, set_schedule, get_schedule, swap
from schedule.forms import AssignForm, SwapForm, ViewScheduleForm
from people.models import Employee
from user.models import EmployeeID, CustomUser
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout

"""This is for the superuser or manager only"""


@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Manager').exists())
def assign_view(request):
    if request.method == 'POST':
        # if it is a post method, then process form data

        form = AssignForm(request.POST)
        #        print('form valid or no', form.is_valid())
        #        print(form.errors)

        if form.is_valid():
            employee_id = form.cleaned_data['employee_id']
            shift_name = form.cleaned_data['shift_pattern']
            start_date = form.cleaned_data['start_date']
            repeat = form.cleaned_data['repeat']

            employee_detail = get_object_or_404(EmployeeID, pk=employee_id)
            user = CustomUser.objects.get(employee_detail=employee_detail)
            person_instance = Employee.objects.get(user=user)

            # get info before modifying
            person_instance.get_info()
            shift_pattern = Schedule.objects.filter(group=request.user.group).get(schedule_name__exact=shift_name)

            status, not_registered = set_schedule(person=person_instance,
                                                  start_date=start_date,
                                                  shift_pattern=shift_pattern,
                                                  repeat=repeat)
            # print('status', status)
            # get_schedule(person=person_instance)

            if status:
                # succeed
                messages.add_message(request,
                                     messages.INFO,
                                     'you have successfully added shifts')
            else:
                messages.add_message(request,
                                     messages.INFO,
                                     'shifts adding were not all successful')
            return HttpResponseRedirect(reverse('assign_result'))
        else:
            form = AssignForm(initial={'employee_id': 0, 'repeat': 1})
            context = {'form': form,
                       }
            return render(request, 'schedule/swap.html', context=context)
    else:
        # if it is GET, create default form
        form = AssignForm(initial={'employee_id': 0, 'repeat': 1})
        context = {'form': form,
                   }
        return render(request, 'schedule/assign.html', context=context)


@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Manager').exists())
def assign_result_view(request):
    """redirected from assign_view"""
    if request.method == 'POST':
        if request.POST.get("logout"):
            logout(request)
            return render(request, 'registration/logged_out.html')
    else:
        if request.GET.get("restart"):
            return HttpResponseRedirect(reverse('assign'))
        else:
            return render(request, 'schedule/assign_result.html')


@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Manager').exists())
def schedule_view(request):
    if request.method == 'POST':
        # if it is a post method, then process form data
        form = ViewScheduleForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data['employee_id']
            employee_detail = get_object_or_404(EmployeeID, pk=employee_id)
            user = CustomUser.objects.get(employee_detail=employee_detail)
            person_instance = Employee.objects.get(user=user)
            schedule = get_schedule(person=person_instance)
            display_info = []
            for s in schedule:
                display_info.append(
                    '{}, start: {}, end: {}'.format(s.employee.user.first_name + " " + s.employee.user.last_name,
                                                    s.shift_start, s.shift_end))
            messages.add_message(request,
                                 messages.INFO,
                                 display_info)

            return HttpResponseRedirect(reverse('schedule_result'))
        else:
            form = ViewScheduleForm(initial={'employee_id': 0})
            context = {'form': form,
                       }
            return render(request, 'schedule/schedule_view.html', context=context)
    else:
        form = ViewScheduleForm(initial={'employee_id': 0})
        context = {'form': form,
                   }
        return render(request, 'schedule/schedule_view.html', context=context)


@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Manager').exists())
def schedule_result_view(request):
    """redirected from schedule_view"""
    if request.method == 'POST':
        if request.POST.get("logout"):
            logout(request)
            return render(request, 'registration/logged_out.html')
    else:
        if request.GET.get("restart"):
            return HttpResponseRedirect(reverse('schedule'))
        else:
            return render(request, 'schedule/schedule_result_view.html')


@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Manager').exists())
def swap_view(request):
    if request.method == 'POST':
        # if it is a post method, then process form data
        form = SwapForm(request.POST)

        if form.is_valid():

            employee_id = form.cleaned_data['employee_id']
            swap_shift_start = form.cleaned_data['swap_shift_start']

            employee_detail = get_object_or_404(EmployeeID, pk=employee_id)
            user = CustomUser.objects.get(employee_detail=employee_detail)
            person_instance = Employee.objects.get(user=user)
            result = swap(person=person_instance, swap_shift_start=swap_shift_start)
            # result is dictionary with key 

            if result['success']:
                if result['available_shifts']:
                    # pass as list
                    display_info = []
                    for match in result['available_shifts']:
                        display_info.append('{}, start: {}, end: {}'.format(match.employee.person_name,
                                                                            match.shift_start, match.shift_end))
                    messages.add_message(request,
                                         messages.INFO,
                                         display_info)

                elif len(result['free_people']) != 0:
                    display_info = [str(p) for p in result['free_people']]
                    messages.add_message(request,
                                         messages.INFO,
                                         display_info)
            else:
                messages.add_message(request,
                                     messages.INFO,
                                     'no available shift swaps')

            return HttpResponseRedirect(reverse('swap_result'))
        else:
            form = SwapForm(initial={'employee_id': 0})
            context = {'form': form,
                       }
            messages.add_message(request, messages.INFO, 'please enter valid info')
            return render(request, 'schedule/swap.html', context=context)
    else:

        form = SwapForm(initial={'employee_id': 0})
        context = {'form': form,
                   }
        return render(request, 'schedule/swap.html', context=context)


@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Manager').exists())
def swap_result_view(request):
    """redirected from swap view"""
    if request.method == 'POST':
        if request.POST.get("logout"):
            logout(request)
            return render(request, 'registration/logged_out.html')
        if request.POST.get("swap"):
            index = request.POST['swap_box']
            print(index)
            return HttpResponseRedirect(reverse('swap'))
    else:
        if request.GET.get("restart"):
            return HttpResponseRedirect(reverse('swap'))
        else:
            return render(request, 'schedule/swap_result.html')
