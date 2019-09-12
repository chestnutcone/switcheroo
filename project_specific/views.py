from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
# Create your views here.
from schedule.models import get_schedule
from people.models import Individual
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages

from project_specific.forms import SwapForm
from schedule.models import swap

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
            # hardcoded...
            return HttpResponseRedirect('/admin/')
    
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
                # pass as list
#                match_info = {}
                display_info = []
                for match in result['available_shifts']:
                    display_info.append('{}, start: {}, end: {}'.format(match.individual.person_name,
                                        match.shift_start, match.shift_end))
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
            return render(request, 'schedule/swap.html',context=context)
    else:

        form = SwapForm()
        context = {'form':form,
                   }
        return render(request, 'project_specific/swap.html',context=context)
    
@login_required
def swap_result_view(request):
    if request.method == 'POST':
        if request.POST.get("logout"):
                logout(request)
                return render(request, 'registration/logged_out.html')
    else:
        if request.GET.get("home"):
            return HttpResponseRedirect(reverse('profile'))
        else:
            return render(request, 'project_specific/swap_result.html')