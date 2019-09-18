from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.contrib.auth.hashers import make_password
from .forms import CustomUserCreationForm
from django.contrib.auth.models import Group, Permission
from django.http import HttpResponseRedirect
from user.models import CustomUser


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            is_manager = form.cleaned_data['is_manager']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            password = form.cleaned_data['password2']
            password = make_password(password)
            user = CustomUser(username=email,
                              first_name=first_name,
                              last_name=last_name,
                              is_manager=is_manager,
                              password=password)
            if is_manager:
                user.is_staff = True
            user.save()
            #            print('is manager', is_manager)
            if is_manager:
                # if is manager is true
                manager_group, created = Group.objects.get_or_create(name="Manager")
                if created:
                    permissions = ['view', 'add', 'delete', 'change']
                    models = ['unit', 'position', 'employee', 'shift', 'schedule', 'assign']

                    for model in models:
                        for permission in permissions:
                            name = 'Can {} {}'.format(permission, model)
                            try:
                                model_add_perm = Permission.objects.get(name=name)
                            except Permission.DoesNotExist:
                                print('Permission not found with name:', name)
                                continue
                            manager_group.permissions.add(model_add_perm)
                    # do for view employee
                    name = 'Can {} {}'.format('view', 'user')
                    try:
                        model_add_perm = Permission.objects.get(name=name)
                    except Permission.DoesNotExist:
                        print('Permission not found with name:', name)
                    manager_group.permissions.add(model_add_perm)

                manager_group.user_set.add(user)

            else:
                # if employee
                employee_group, created = Group.objects.get_or_create(name='Employee')
                if created:
                    permissions = ['view']
                    models = ['unit', 'position', 'employee', 'shift', 'schedule', 'assign']

                    for model in models:
                        for permission in permissions:
                            name = 'Can {} {}'.format(permission, model)
                            try:
                                model_add_perm = Permission.objects.get(name=name)
                            except Permission.DoesNotExist:
                                print('Permission not found with name:', name)
                                continue
                            employee_group.permissions.add(model_add_perm)
                employee_group.user_set.add(user)

            return HttpResponseRedirect(reverse('login'))

        return render(request, self.template_name, {'form': form})
