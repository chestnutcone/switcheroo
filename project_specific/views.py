from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
# Create your views here.
from schedule.models import get_schedule
from people.models import Individual
from user.models import Session
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages

from project_specific.forms import SwapForm
from schedule.models import swap

from .forms import SessionCreateForm, SessionJoinForm


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
            # if superuser, skip session join/create
            # superuser is not manager, and will not have session assigned
            return HttpResponseRedirect('/admin/')
        else:
            if not request.user.session:
                # cannot find session id because session doesnt exist yet
                return HttpResponseRedirect(reverse('session'))
    
    #### log into session, row permission
    
        # will throw index error if the user is not registered under Individual
        current_indv = Individual.objects.filter(user__exact=current_user)[0]
            
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
            person_instance = Individual.objects.filter(user__exact=current_user)[0]

            swap_shift_start = form.cleaned_data['swap_shift_start']

            result = swap(person=person_instance, swap_shift_start=swap_shift_start)
            # result is dictionary with key 
            if result['success'] == True:
                if result['available_shifts']:
                    # pass as list
                    display_info = []
                    for match in result['available_shifts']:
                        display_info.append('{}, start: {}, end: {}'.format(match.individual.person_name,
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
        
def session_view(request):
    if request.method == 'POST':
        if request.POST.get('create_submit'):
            form = SessionCreateForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                session = Session(owner=request.user, password=password)
                session.save()
                print('session id:', session.id)
                request.user.session = session
                request.user.save()
                
                # return to join session page
                return HttpResponseRedirect(reverse('profile'))
        elif request.POST.get('join_submit'):
            form = SessionJoinForm(request.POST)
            if form.is_valid():
                session_id = form.cleaned_data['session_id']
                
                session = Session.objects.get(pk=session_id)
                
                request.user.session = session
                request.user.save()
                print('session joined')
                return HttpResponseRedirect(reverse('profile'))
                
    else:
        if request.user.is_manager:
            # render a session creating form
            form = SessionCreateForm()
            context = {'form':form}
            return render(request, 'project_specific/session_create.html', context=context)
        else:
            # render a join session form
            form = SessionJoinForm()
            context = {'form':form}
            return render(request, 'project_specific/session_join.html',context=context)