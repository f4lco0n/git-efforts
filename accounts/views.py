from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login,authenticate
from django.contrib.auth.models import auth
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseRedirect
# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username,password=raw_password)
            # login(request,user)
            # user = form.save()
            auth_login(request,user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request,'signup.html',{'form':form})
def login(request):
    if request.method == 'GET':
        nextelement = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        return render(request,'login.html',{'next': nextelement})
    if request.method == 'POST':
        nextelement = request.POST['next']
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            # return redirect('home')
            return redirect(nextelement)
        else:
            messages.info(request,'Invalid credentials')
            return redirect('login')
    else:
        return render(request,'login.html')