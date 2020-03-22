from math import pi
from django.shortcuts import render,get_object_or_404,redirect,render_to_response
from django.http import HttpResponse, Http404,HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import Repository
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib import messages
import bs4 as bs
from .modules.calculation_logic import CalculationLogic

def home(request):
    if request.method == 'POST':
        if request.POST['url']:
            url = request.POST['url']
            request.session['url'] = url
            return redirect('bokeh')
        else:
            messages.error(request, 'Insert URL')
    return render(request,'base.html')

def about(request):
    return render(request,'about.html')

def favorites(request):
    url = request.session.get('url')
    user = User.objects.get(username=request.user.username)
    repos = user.users.all()
    return render(request, 'favorites.html', {'url': url, 'repos': repos})



def add_url_to_database(request):
    try:
        url = request.session.get('url')
        repo = Repository(url=url, user=request.user)
        repo.save()
        repo.repositorys.add(request.user)
    except IntegrityError as e:
        return render_to_response('base.html')

def bokeh(request):
    if request.method == 'POST':
        add_url_to_database(request)
        return redirect('favorites')

    try:
        repo_id = request.GET.get('repo_id')
        repo = Repository.objects.get(id=repo_id)
        url = repo.url
        request.session['url'] = url
    except:
        url = request.session.get('url')
    print(url)
    cl = CalculationLogic()
    return cl.get_data_from_url(request,url)

def days(request):
    cl = CalculationLogic()
    url = request.session.get('url')
    return cl.show_days_of_the_week(request,url)

def show_user_repo(request):
    cl = CalculationLogic()
    url = request.session.get('url')
    return cl.show_user_repo(request, url)





