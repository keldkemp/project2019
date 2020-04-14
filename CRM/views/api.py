from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
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
import random
import string


BASE_URL_LOGIN = 'https://student.psu.ru/pls/stu_cus_et/stu.login'
BASE_URL_CHANGE_PASSWORD = 'https://student.psu.ru/pls/stu_cus_et/stu.change_pass_form'

opts = webdriver.ChromeOptions()
opts.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
opts.add_argument('--headless')
opts.add_argument('--dasable-dev-shm-usage')
opts.add_argument('--no-sandbox')


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


# API ETIS


def get_html_from_cookie(url, cookie):
    session = requests.session()
    response = session.post(url, cookies=cookie)

    return response


@csrf_exempt
def get_new_cookie(request):
    try:
        username = request.POST['username']
        password = request.POST['password']

        cookie = get_cookie(username=username, password=password)

        if len(cookie) == 0:
            return HttpResponse(status=403)  # Неверный пароль

        return JsonResponse({'cookie': list(cookie)})
    except:
        return HttpResponse(status=404)


def get_cookie(username, password):
    session = requests.session()
    data = {'p_username': username.encode('windows-1251'), 'p_password': password}
    r = session.post(BASE_URL_LOGIN, data=data)
    cookie = r.cookies.get_dict()

    return cookie


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
    try:
        browser = webdriver.Chrome(chrome_options=opts, executable_path=os.environ.get("CHROMEDRIVER_PATH"))
        # browser = webdriver.Chrome(chrome_options=opts, executable_path="C:/Users/keldkemp/Desktop/chromedriver.exe")
    except:
        return HttpResponse(status=404)

    try:
        username = request.POST['username']
        name = request.POST['name']
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
    except:
        return HttpResponse(status=401)  # Одно из полей не заполнено

    try:
        user = EtisUsers.objects.get(username=username, name=name)
    except:
        return HttpResponse(status=403)  # Введен неверный пароль

    try:

        browser.get(BASE_URL_LOGIN)

        p_username = browser.find_element_by_id('login')
        p_username.send_keys(username)

        p_password = browser.find_element_by_id('password')
        p_password.send_keys(old_password)

        btm = browser.find_element_by_id('sbmt')
        btm.click()

        time.sleep(3)

        try:
            btm_change = browser.find_element_by_link_text('Смена пароля')
        except:
            return HttpResponse(status=403)  # Введен неверный пароль
        btm_change.click()

        p_old_password = browser.find_element_by_id('old')
        p_old_password.send_keys(old_password)

        p_new_password = browser.find_element_by_id('new')
        p_new_password.send_keys(new_password)

        p_confirm_password = browser.find_element_by_id('confirm')
        p_confirm_password.send_keys(new_password)

        try:
            btm = browser.find_element_by_class_name('button_gray')
        except:
            return HttpResponse(status=402)  # В данный момент пароль изменить нельзя
        btm.click()

        try:
            error = browser.find_element_by_class_name('error')
            return HttpResponse(status=402)  # В данный момент пароль изменить нельзя
        except:
            pass

        browser.close()

        return HttpResponse(status=200)
    except:
        HttpResponse(status=404)  # Неизвестная ошибка


@csrf_exempt
def update_session(request):
    try:
        cookie = request.POST['cookie']
        cookie = {'session_id': cookie}
        name = request.POST['name']
        user = EtisUsers.objects.get(name=name)

        html = get_html_from_cookie('https://student.psu.ru/pls/stu_cus_et/stu.signs?p_mode=session', cookie=cookie)
        parse_session(html.text, user)

        makes = EtisMakes.objects.filter(user_id=user.id).values('discipline', 'make', 'date', 'teacher',
                                                                 'trem').order_by('id')
        return JsonResponse({'makes': list(makes)})
    except:
        return HttpResponse(status=404)


def add_fist_makes(cookie, user):
    html = get_html_from_cookie('https://student.psu.ru/pls/stu_cus_et/stu.signs?p_mode=session', cookie=cookie)
    parse_session(html.text, user)


def get_name_etis(username, password):
    html = get_html('https://student.psu.ru/pls/stu_cus_et/stu.signs?p_mode=session', username=username, password=password)

    soup = BeautifulSoup(html.text, 'lxml')
    name = soup.find('span', style="color: #808080;white-space:nowrap;").text
    name = name.partition('\n')[0]
    return name


def generate_key():
    str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(30))
    key = make_password(str)
    return key


@csrf_exempt
def add_user_etis(request):
    try:
        username = request.POST['username']
        password = request.POST['password']

        name = get_name_etis(username, password)
        cookie = get_cookie(username, password)

        if EtisUsers.objects.filter(username=username, name=name):
            user = EtisUsers.objects.filter(username=username, name=name).values('name', 'id')
            makes = EtisMakes.objects.filter(user_id=user[0]['id']).values('discipline', 'make', 'date', 'teacher', 'trem').order_by('id')
        else:
            if not EtisUsers.objects.filter(id=1).exists():
                EtisUsers(id=1, username=username, name=name).save()
            else:
                user = EtisUsers.objects.filter().order_by('-id')
                EtisUsers(id=user[0].id+1, username=username, name=name).save()
            user = EtisUsers.objects.get(username=username, name=name)
            add_fist_makes(cookie, user)
            makes = EtisMakes.objects.filter(user_id=user.id).values('discipline', 'make', 'date', 'teacher', 'trem').order_by('id')

            user = EtisUsers.objects.filter(username=username, name=name).values('name', 'id')

        return JsonResponse({'user': list(user), 'makes': list(makes), 'cookie': cookie})
    except:
        return HttpResponse(status=404)
