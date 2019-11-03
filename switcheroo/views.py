from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect('/main/')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def main_page_view(request):
    if request.method == "POST":
        pass
    elif request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/main/')
        else:
            return render(request, 'home.html')

def handler500(request):
    import sys, traceback
    ltype, lvalue, ltraceback = sys.exc_info()

    return render(request, 'project_specific/500.html', context={'type':ltype,
                                                'value':lvalue,
                                                'traceback':str(traceback.print_tb(ltraceback))})