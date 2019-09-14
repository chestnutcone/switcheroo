from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.contrib.auth.hashers import make_password

from .forms import CustomUserCreationForm
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from user.models import CustomUser

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
#    success_url = reverse_lazy('login')
    template_name = 'signup.html'
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form':form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            is_manager = form.cleaned_data['is_manager']
            email = form.cleaned_data['email']

            password = form.cleaned_data['password2']
            password = make_password(password)
            user = CustomUser(username=username,
                              email=email,
                              is_manager=is_manager,
                              password = password)
            user.save()
#            print('is manager', is_manager)
            if is_manager:
                # if is manager is true
                manager_group = Group.objects.get(name='Manager') 
                manager_group.user_set.add(user)
            else:
                # if employee
                employee_group = Group.objects.get(name='Employee')
                employee_group.user_set.add(user)
            
            return HttpResponseRedirect(reverse('login'))
        
        return render(request, self.template_name, {'form':form})

    
