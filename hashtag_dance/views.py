from django.shortcuts import render

def home(request):
    return render(request, 'hashtag_dance/home.html')