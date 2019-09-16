from django.shortcuts import render

# Create your views here.
from people.models import Position, Unit, Employee
from django.views import generic

def index(request):
    num_people = Employee.objects.all().count()
    context = {
            'num_people':num_people
            }
    return render(request, 'people/index.html', context=context)
    
