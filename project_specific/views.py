from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
# Create your views here.
from schedule.models import get_schedule
from people.models import Employee
from user.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages

from project_specific.forms import SwapForm
from schedule.models import swap

from .forms import GroupCreateForm, GroupJoinForm


"""this is for the average employee view"""

@login_required
def profile_view(request):
    """main page of employee. Redirect to here after login"""
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
            elif current_user.is_manager:
                # if not superuser and is manager, and has a group, redirect to admin
                return HttpResponseRedirect('/admin/')
                
    #### log into group, row permission
    
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
            context = {'dates':dates,
                       'shift_start':shift_start,
                       'shift_end':shift_end,
                       'name':current_user.first_name}
        except IndexError:
            context = {'name':'Please register user in Employee'}
        return render(request, 'project_specific/profile.html', context=context)

@login_required
def swap_view(request):
    if request.method == 'POST':
        # if it is a post method, then process form data
        form = SwapForm(request.POST)
        if request.POST.get("logout"):
            logout(request)
            return render(request, 'registration/logged_out.html')
        if form.is_valid():
            current_user = request.user
            person_instance = Employee.objects.filter(user__exact=current_user)[0]

            swap_shift_start = form.cleaned_data['swap_shift_start']

            result = swap(person=person_instance, swap_shift_start=swap_shift_start)
            # result is dictionary with key 
            if result['success'] == True:
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
            form = SwapForm()
            context = {'form':form,
                   }
            messages.add_message(request, messages.INFO,'please enter valid info')
            return render(request, 'project_specific/swap.html',context=context)
    else:

        form = SwapForm()
        context = {'form':form,
                   }
        return render(request, 'project_specific/swap.html',context=context)
    
@login_required
def swap_result_view(request):
    """redirect here after swap_view"""
    if request.method == 'POST':
        if request.POST.get("logout"):
            logout(request)
            return render(request, 'registration/logged_out.html')
        if request.POST.get("swap"):
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
                print('group joined')
                return HttpResponseRedirect(reverse('profile'))
                
    else:
        if request.user.is_manager:
            # render a group creating form
            form = GroupCreateForm()
            context = {'form':form}
            return render(request, 'project_specific/group_create.html', context=context)
        else:
            # render a join group form
            form = GroupJoinForm()
            context = {'form':form}
            return render(request, 'project_specific/group_join.html',context=context)