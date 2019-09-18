from django.shortcuts import render
from people.models import Employee


def index(request):
    num_people = Employee.objects.all().count()
    context = {
            'num_people':num_people
            }
    return render(request, 'people/index.html', context=context)