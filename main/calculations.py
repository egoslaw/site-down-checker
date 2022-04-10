import requests
import json
from datetime import datetime
from constance import config
from proxy_requests.proxy_requests import ProxyRequests

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages

from .models import SiteToCheck
from .models import Data


def send_email(message, email):
    subject = 'Errors on my pages'
    message = message
    from_email = settings.EMAIL_ADDRESS
    to_email = email
    send_mail(
        subject,
        message,
        from_email,
        [to_email],
        fail_silently=False,
    )


def my_cron_job():
    users = User.objects.all()
    for user in users:
        sites = SiteToCheck.objects.filter(user=user)
        output = ''
        for site in sites:
            if 'bad_data' in SiteDownChecker(site, user).status():
                output += f'{site} - ERROR\n'
            elif site.last_status != 200:
                output += f'{site} - last status: {site.last_status}'
        if len(output) > 0:
            send_email(output, user.email)


def modify_email(request):
    response_json = json.dumps(request.POST)
    data = json.loads(response_json)
    user = request.user
    if user.email == data['email']:
        error_message = 'It is your existing email address'
        messages.error(request, error_message)
    else:
        user.email = data['email']
        user.save()
        success_message = f'You changed your email. Every messages will be send to \
                    {request.user.email} until now.'
        messages.success(request, success_message)


class SiteDownChecker:

    def __init__(self, url, user):
        self.url = url
        self.time = 0
        self.error = None
        self.user = user

    def status(self, proxy=False):
        try:
            if proxy:
                r = ProxyRequests(self.url)
            else:
                r = requests.get(self.url, headers={
                    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)'})
            if SiteToCheck.objects.filter(url=self.url, user=self.user).exists():
                self.saveData()
                return self.modify_url_success(proxy, r)

            else:
                return self.create_new_url_success(proxy, r)
        except Exception as e:
            self.error = str(e)
            if not proxy and config.PROXY:
                return self.status(proxy=True)
            if SiteToCheck.objects.filter(url=self.url, user=self.user).exists():
                return self.modify_url_exception(e)
            else:
                return self.create_url_exception()

    def create_url_exception(self):
        data = dict()
        SiteToCheck.objects.create(url=self.url,
                                   user=self.user,
                                   last_status=None,
                                   last_response_time=None,
                                   last_check=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                   bad_data=str(
                                       datetime.now().strftime("%Y-%m-%d %H:%M")) + ': The url is not responding'
                                   )
        data['last_status'] = None
        data['last_response_time'] = None
        data['bad_data'] = 'The url is not responding'
        return data

    def modify_url_exception(self, e):
        data = dict()
        obj = SiteToCheck.objects.get(url=self.url, user=self.user)
        obj.last_status = None
        obj.last_response_time = None
        obj.last_check = datetime.now().strftime("%Y-%m-%d %H:%M")
        if len(obj.bad_data) > 0:
            obj.bad_data += '\n'
        obj.bad_data += str(datetime.now().strftime("%Y-%m-%d %H:%M")) + ': ' + self.error
        obj.save()
        data['bad_data'] = e
        data['last_status'] = None
        data['last_response_time'] = None
        data['last_check'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        data['url'] = self.url
        return data

    def create_new_url_success(self, proxy, r):
        data = dict()
        data['last_status'] = r.status_code if not proxy else r.get_status_code()
        data['last_response_time'] = r.elapsed.total_seconds() if not proxy else self.time
        data['last_check'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        SiteToCheck.objects.create(url=self.url,
                                   user=self.user,
                                   last_status=data['last_status'],
                                   last_response_time=data['last_response_time'],
                                   last_check=data['last_check'])
        return data

    def modify_url_success(self, proxy, r):
        data = dict()
        data['last_status'] = r.status_code if not proxy else r.get_status_code()
        data['last_response_time'] = r.elapsed.total_seconds() if not proxy else self.time
        obj = SiteToCheck.objects.get(url=self.url, user=self.user)
        obj.last_status = data['last_status']
        obj.last_response_time = data['last_response_time']
        if data['last_status'] != 200:
            if len(obj.bad_data) > 0:
                obj.bad_data += '\n'
            obj.bad_data += str(
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M")) + f": last status different than 200: {data['last_status']}"
        obj.last_check = datetime.now().strftime("%Y-%m-%d %H:%M")
        obj.save()
        return data

    def saveData(self):
        obj = SiteToCheck.objects.get(url=self.url, user=self.user)
        url = obj.url
        last_status = obj.last_status
        bad_data = obj.bad_data
        last_response_time = obj.last_response_time
        last_check = obj.last_check
        Data.objects.create(url=self.url,
                            last_status=last_status,
                            last_response_time=last_response_time,
                            last_check=last_check,
                            bad_data =bad_data)

        return obj.last_status
