from django.shortcuts import render

# Create your views here.
from schedule.models import Schedule, set_schedule, get_schedule, swap
from schedule.forms import AssignForm, SwapForm, ScheduleForm
from people.models import Individual
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout

@user_passes_test(lambda u: u.is_superuser)
def assign_view(request):
    
    if request.method == 'POST':
        # if it is a post method, then process form data

        form = AssignForm(request.POST)
#        form = AssignForm(request.POST)
        
#        print('#####POST request reached')
#        print('form valid or no', form.is_valid())
#        print(form.errors)

        if form.is_valid():
#            person_name = form.cleaned_data['person_name']
            
            employee_id = form.cleaned_data['employee_id']
            shift_id = form.cleaned_data['shift_pattern']
            start_date = form.cleaned_data['start_date']
            
            
            person_instance = get_object_or_404(Individual, pk=employee_id)
            
            # get info before modifying
            person_instance.get_info()
            shift_pattern = get_object_or_404(Schedule, pk=shift_id)
            shift_pattern.mk_ls()
            
#            status = person_instance.set_schedule(start_date, shift_pattern)
#            person_instance.save()
            
            status = set_schedule(person=person_instance,
                                         start_date = start_date,
                                         shift_pattern = shift_pattern)
            get_schedule(person=person_instance)
            # get info after modifying
#            person_instance.get_info()
            if status:
                # succeed
                messages.add_message(request, 
                                     messages.INFO, 
                                     'you have successfully added shifts')
            else:
                messages.add_message(request, 
                                     messages.INFO, 
                                     'shifts adding not successful')
            return HttpResponseRedirect(reverse('assign_result'))
        else:
            form = AssignForm(initial={'employee_id':0})
            context = {'form':form,
                   }
            return render(request, 'schedule/swap.html',context=context)
    else:
        # if it is GET, create default form
#        print('########get request reached')
#        form = AssignForm(initial={'person_name':'Enter name',
#                                   'employee_id':000000})
        form = AssignForm(initial={'employee_id':0})
        context = {'form':form,
                   }
        return render(request, 'schedule/assign.html',context=context)
    
@user_passes_test(lambda u: u.is_superuser)
def assign_result_view(request):
    if request.method == 'POST':
        if request.POST.get("logout"):
                logout(request)
                return render(request, 'registration/logged_out.html')
    else:
        if request.GET.get("restart"):
            return HttpResponseRedirect(reverse('assign'))
        else:
            return render(request, 'schedule/assign_result.html')

@user_passes_test(lambda u: u.is_superuser)
def swap_result_view(request):
    if request.method == 'POST':
        if request.POST.get("logout"):
                logout(request)
                return render(request, 'registration/logged_out.html')
    else:
        if request.GET.get("restart"):
            return HttpResponseRedirect(reverse('swap'))
        else:
            return render(request, 'schedule/swap_result.html')

@user_passes_test(lambda u: u.is_superuser)
def schedule_view(request):
    if request.method == 'POST':
        # if it is a post method, then process form data
        form = ScheduleForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data['employee_id']
            person_instance = get_object_or_404(Individual, pk=employee_id)
            schedule = get_schedule(person=person_instance)
            display_info = []
            for s in schedule:
                display_info.append('{}, start: {}, end: {}'.format(s.individual.user.first_name+" "+s.individual.user.last_name,
                                    s.shift_start, s.shift_end))
            messages.add_message(request, 
                                 messages.INFO, 
                                 display_info)
            
            return HttpResponseRedirect(reverse('schedule_result'))
        else:
            form = ScheduleForm(initial={'employee_id':0})
            context = {'form':form,
                   }
            return render(request, 'schedule/schedule_view.html',context=context)
    else:
        form = ScheduleForm(initial={'employee_id':0})
        context = {'form':form,
                   }
        return render(request, 'schedule/schedule_view.html',context=context)

    
def schedule_result_view(request):
    if request.method == 'POST':
        if request.POST.get("logout"):
                logout(request)
                return render(request, 'registration/logged_out.html')
    else:
        if request.GET.get("restart"):
            return HttpResponseRedirect(reverse('schedule'))
        else:
            return render(request, 'schedule/schedule_result_view.html')

@user_passes_test(lambda u: u.is_superuser)
def swap_view(request):
    if request.method == 'POST':
        # if it is a post method, then process form data
        form = SwapForm(request.POST)

        if form.is_valid():

            employee_id = form.cleaned_data['employee_id']
            swap_shift_start = form.cleaned_data['swap_shift_start']
            
            person_instance = get_object_or_404(Individual, pk=employee_id)
            result = swap(person=person_instance, swap_shift_start=swap_shift_start)
            # result is dictionary with key 
            if result['success'] == True:
                # pass as list
#                match_info = {}
                display_info = []
                for match in result['available_shifts']:
                    # key of assign object primary key
#                    match_info[match.id] = {'shift_start':match.shift_start,
#                              'shift_end':match.shift_end,
#                              'individual':match.individual.employee_id,
#                              }
                    display_info.append('{}, start: {}, end: {}'.format(match.individual.person_name,
                                        match.shift_start, match.shift_end))
                messages.add_message(request, 
                                     messages.INFO, 
                                     display_info)
                # the datetime objects is now str
                # use datetime.datetime.strptime() to convert str back
                # then use pytz to make it timezone aware (UTC)
                
                
            else:
                messages.add_message(request,
                                     messages.INFO,
                                     'no available shift swaps')
        
            return HttpResponseRedirect(reverse('swap_result'))
        else:
            form = SwapForm(initial={'employee_id':0})
            context = {'form':form,
                   }
            messages.add_message(request, messages.INFO,'please enter valid info')
            return render(request, 'schedule/swap.html',context=context)
    else:

        form = SwapForm(initial={'employee_id':0})
        context = {'form':form,
                   }
        return render(request, 'schedule/swap.html',context=context)