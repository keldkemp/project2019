from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from CRM.models import Worker, Time
from django.http import HttpResponse
import requests
import re
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from CRM.models import EtisMakes, EtisUsers
import time
import os


BASE_URL_LOGIN = 'https://student.psu.ru/pls/stu_cus_et/stu.login'

opts = webdriver.ChromeOptions()
opts.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
opts.add_argument('headless')
browser = webdriver.Chrome(chrome_options=opts, executable_path=os.environ.get("CHROMEDRIVER_PATH"))


@csrf_exempt
def connect(request):
    try:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            user_send = Worker.objects.filter(id=user.id).values("username")
            time_send = Time.objects.filter(worker_id=user.id).values("time_of_arrival", "time_of_leaving").order_by('-pk')
            return JsonResponse({'user': list(user_send), 'time': list(time_send)})
        else:
            return HttpResponse(status=404)
    except:
        return HttpResponse(status=404)


def get_html(url, username, password):
    session = requests.session()
    data = {'p_username': username.encode('windows-1251'), 'p_password': password}
    r = session.post(BASE_URL_LOGIN, data=data)
    if not r.cookies._cookies:
        return 0
    response = session.post(url)

    return response


def parse_session(html, user):
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', class_='common')

    if EtisMakes.objects.filter(user_id=user.id):
        EtisMakes.objects.filter(user_id=user.id).delete()

    if EtisMakes.objects.all():
        id = EtisMakes.objects.filter().order_by('-id')[0].id + 1
    else:
        id = 0

    makes = {}

    for day in table.find_all('tr'):
        if day.find('th', colspan="4"):
            trem = day.text
        for make in enumerate(day.find_all('td')):
            makes[make[0]] = make[1].text
        if makes:
            EtisMakes(id=id, discipline=makes[0], make=makes[1], date=makes[2], teacher=makes[3], trem=trem, user_id=user.id).save()
            id = id + 1
            makes = {}


@csrf_exempt
def update_password(request):
    username = request.POST['username']
    old_password = request.POST['old_password']
    new_password = request.POST['new_password']

    user = EtisUsers.objects.get(username=username, password=old_password)

    try:

        browser.get(BASE_URL_LOGIN)

        p_username = browser.find_element_by_id('login')
        p_username.send_keys(username)

        p_password = browser.find_element_by_id('password')
        p_password.send_keys(old_password)

        btm = browser.find_element_by_id('sbmt')
        btm.click()

        time.sleep(5)

        btm_change = browser.find_element_by_link_text('Смена пароля')
        btm_change.click()

        p_old_password = browser.find_element_by_id('old')
        p_old_password.send_keys(old_password)

        p_new_password = browser.find_element_by_id('new')
        p_new_password.send_keys(new_password)

        p_confirm_password = browser.find_element_by_id('confirm')
        p_confirm_password.send_keys(new_password)

        btm = browser.find_element_by_class_name('button_gray')
        btm.click()

        user.password = new_password
        user.save()

        return HttpResponse(status=200)
    except:
        HttpResponse(status=404)


@csrf_exempt
def update_session(request):
    try:
        username = request.POST['username']
        name = request.POST['name']
        user = EtisUsers.objects.get(username=username, name=name)

        html = get_html('https://student.psu.ru/pls/stu_cus_et/stu.signs?p_mode=session', username=user.username, password=user.password)
        parse_session(html.text, user)

        makes = EtisMakes.objects.filter(user_id=user.id).values('discipline', 'make', 'date', 'teacher',
                                                                 'trem').order_by('id')
        return JsonResponse({'makes': list(makes)})
    except:
        return HttpResponse(status=404)


def add_fist_makes(user):
    html = get_html('https://student.psu.ru/pls/stu_cus_et/stu.signs?p_mode=session', username=user.username, password=user.password)
    parse_session(html.text, user)


def get_name_etis(username, password):
    html = get_html('https://student.psu.ru/pls/stu_cus_et/stu.signs?p_mode=session', username=username, password=password)

    soup = BeautifulSoup(html.text, 'lxml')
    name = soup.find('span', style="color: #808080;white-space:nowrap;").text
    name = name.partition('\n')[0]
    return name


@csrf_exempt
def add_user_etis(request):
    try:
        username = request.POST['username']
        password = request.POST['password']

        if EtisUsers.objects.filter(username=username, password=password):
            user = EtisUsers.objects.filter(username=username, password=password).values('name', 'id')
            user_pas = EtisUsers.objects.get(username=username, password=password)
            user_pas.password = password
            user_pas.save()
            makes = EtisMakes.objects.filter(user_id=user[0]['id']).values('discipline', 'make', 'date', 'teacher', 'trem').order_by('id')
        else:
            name = get_name_etis(username, password)

            if not EtisUsers.objects.filter(id=1).exists():
                EtisUsers(id=1, username=username, password=password, name=name).save()
            else:
                user = EtisUsers.objects.filter().order_by('-id')
                EtisUsers(id=user[0].id+1, username=username, password=password, name=name).save()
            user = EtisUsers.objects.get(username=username, password=password)
            add_fist_makes(user)
            makes = EtisMakes.objects.filter(user_id=user.id).values('discipline', 'make', 'date', 'teacher', 'trem').order_by('id')

        return JsonResponse({'user': list(user), 'makes': list(makes)})
    except:
        return HttpResponse(status=404)
