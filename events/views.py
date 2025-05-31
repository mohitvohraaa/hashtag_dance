from django.shortcuts import render
from .models import Event
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def events(request):
    events_list = Event.objects.all().order_by('-date')
    return render(request, 'events/events.html', {'events': events_list})

# Create your views here.
