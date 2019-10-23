from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect


def loginView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/main/')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def mainView(request):
    if request.method == "POST":
        pass
    elif request.method == "GET":
        if request.user.is_authenticated:
            return redirect('main/')
        else:
            return render(request, 'home.html')