import json
from constance import config

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from .forms import SiteToCheckForm, MyUserCreationForm
from .models import SiteToCheck
from .calculations import SiteDownChecker, modify_email
from .models import Data


def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        render(request, 'login.html')
    else:
        # Return an 'invalid login' error message.
        render(request, 'login.html')


def registration_view(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = MyUserCreationForm()
    return render(request, 'register.html', {'form': form})


def index(request):
    if not request.user.is_authenticated:
        return redirect('login/')
    user = request.user
    sites = SiteToCheck.objects.filter(user=user)
    if request.method == 'POST' and 'add_url_submit' in request.POST:
        form = SiteToCheckForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if SiteToCheck.objects.filter(url=cd['url'], user=user).exists():
                messages.error(request, 'The page already exists in database')
            else:
                data = SiteDownChecker(cd['url'], user=user).status()
                success_message_text = f"The page hes been added. \n\nStatus: {data['last_status']}, Response time: \
                {data['last_response_time']}"
                messages.success(request, success_message_text)
            return redirect('/')
        else:
            messages.error(request, 'Please enter the correct URL')
    elif request.method == 'POST' and 'email' in request.POST:
        modify_email(request)
        return redirect('/')
    else:
        form = SiteToCheckForm
        if request.GET.get('check_all_btn'):
            for url in sites:
                SiteDownChecker(url, user).status()
            return redirect('/')
    return render(request, 'index.html', {'form': form, 'sites': sites})


@login_required
def url_details(request, pk):
    url = get_object_or_404(SiteToCheck, pk=pk, user=request.user)
    if request.GET.get('check_btn'):
        # TODO: переделать all_Data
        all_Data = Data.objects.filter(url__exact=url)
        for item in all_Data:
            print(item.url)
        data = SiteDownChecker(url, user=request.user).status()
        success_message_text = f"{url} Status: {data['last_status']}, Response time: {data['last_response_time']}"
        messages.success(request, success_message_text)
        refreshed_url = get_object_or_404(SiteToCheck, pk=pk, user=request.user)
        bad_data = refreshed_url.bad_data.splitlines()
        return render(request, 'details.html', {'url': url, 'bad_data': bad_data, 'all_Data': all_Data})
    else:
        all_Data = Data.objects.filter(url__exact=url)

        bad_data = url.bad_data.splitlines()
        return render(request, 'details.html', {'url': url, 'bad_data': bad_data, 'all_Data': all_Data}, )


@login_required
def url_delete(request, pk):
    url = get_object_or_404(SiteToCheck, pk=pk, user=request.user)
    if request.method == 'GET':
        url.delete()
        message = f'{url.url} was deleted'
        messages.success(request, message)
        return redirect('/')
    return render(request, 'index.html')


@login_required
def url_refresh(request, pk):
    url = get_object_or_404(SiteToCheck, pk=pk, user=request.user)
    if request.method == 'GET':
        data = SiteDownChecker(url.url, user=request.user).status()
        success_message_text = f"{url} Status: {data['last_status']}, Response time: {data['last_response_time']}"
        messages.success(request, success_message_text)
        return redirect('/')
    return render(request, 'index.html')


def modify_settings(request):
    if request.method == 'POST':
        response_json = request.POST
        response_json = json.dumps(response_json)
        data = json.loads(response_json)
        if data['id'] == 'proxy':
            if config.PROXY is True:
                config.PROXY = False
            else:
                config.PROXY = True
    return redirect('/')

# date
# status code
#
