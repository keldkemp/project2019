from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from CRM.models import Worker, Time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from CRM.models import EtisMakes, EtisUsers, EtisMakesInTrem
import time
import os
import random
import string
import threading
import re


BASE_URL_LOGIN = 'https://student.psu.ru/pls/stu_cus_et/stu.login'
BASE_URL_CHANGE_PASSWORD = 'https://student.psu.ru/pls/stu_cus_et/stu.change_pass_form'
BASE_URL_MAKES_IN_TREM = 'https://student.psu.ru/pls/stu_cus_et/stu.signs?p_mode=current&p_term='

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

# Получения оценок во Всех Триместрах. По-идее, должен вызываться только один раз
@csrf_exempt
def get_makes_in_all_trem(request):
    name = request.POST['name']

    user = EtisUsers.objects.get(name=name)

    if not user.is_all_makes():
        time.sleep(1)

    makes_list = EtisMakesInTrem.objects.filter(user_id=user.id).values('discipline', 'tema', 'type_of_work',
                                                                           'type_of_control', 'make', 'passing_score',
                                                                           'max_score', 'date', 'teacher',
                                                                           'trem').order_by('id')

    return JsonResponse({'makes': list(makes_list)})


# Обновление оценок в Текущем Триместре
@csrf_exempt
def update_makes_in_trem(request):
    try:
        cookie = request.POST['cookie']
        cookie = {'session_id': cookie}
        name = request.POST['name']

        trem = get_current_trem(cookie)
        html = get_html_from_cookie(BASE_URL_MAKES_IN_TREM, cookie)

        user = EtisUsers.objects.get(name=name)
        pars_makes_in_trem(html, user, trem)

        makes_in_trem = EtisMakesInTrem.objects.filter(user_id=user.id, trem=trem).values('discipline', 'tema',
                                                                                          'type_of_work', 'type_of_control',
                                                                                          'make', 'passing_score',
                                                                                          'max_score', 'date', 'teacher',
                                                                                          'trem').order_by('id')

        return JsonResponse({'make': list(makes_in_trem)})
    except:
        return HttpResponse(status=400)


# Получение текущего триместра
def get_current_trem(cookie):
    html = get_html_from_cookie('https://student.psu.ru/pls/stu_cus_et/stu.signs?p_mode=current', cookie)

    soup = BeautifulSoup(html.text, 'lxml')
    table = soup.find('div', class_='submenu')
    table = table.findNext('div')
    table = table.find_all('span')
    trem = ''

    for span in table:
        if (span.find('a', class_='dashed')):
            continue
        trem = span.text
        break

    trem = trem.split('\n')

    for tr in trem:
        kek = tr.find('триместр')
        if tr.find('триместр') != -1:
            trem = tr
            break


    return trem


# Занесение в БД информации по оценкам ВО Всех Триместрах
def pars_makes_in_trem_first(html, user, trem):
    soup = BeautifulSoup(html.text, 'lxml')
    table = soup.find('div', class_='span9')

    makes = {}
    table_common = table.find('table', class_='common')

    if table_common is None:
        return

    table = table.find_all('h3')
    i = 0

    if EtisMakesInTrem.objects.all():
        id = EtisMakesInTrem.objects.filter().order_by('-id')[0].id + 1
    else:
        id = 0

    for discipline_in_table in table:
        discipline = discipline_in_table.text
        for make in enumerate(table_common.find_all('td')):
            if (len(makes) == 9):
                EtisMakesInTrem(id=id, discipline=discipline, tema=makes[0], type_of_work=makes[1],
                                type_of_control=makes[2], make=makes[3], passing_score=makes[4], max_score=makes[6],
                                date=makes[7], teacher=makes[8], trem=str(str(trem) + ' триместр'),
                                user_id=user.id).save()

                makes = {}
                i = 0
                id = id + 1
            makes[i] = make[1].text
            i = i + 1
        makes = {}
        i = 0
        table_common = table_common.findNext('table')


# Обновление оценок Во Всех триместрах, Запускать именно этот метод!!!
def pars_makes_in_trems_first(cookie, user):
    trem_max_str = get_current_trem(cookie)
    trem_max = int(re.findall('(\d+)', trem_max_str)[0]) + 1

    if EtisMakesInTrem.objects.filter(user_id=user.id):
        EtisMakesInTrem.objects.filter(user_id=user.id).delete()

    for trem_min in range(1, trem_max):
        url = BASE_URL_MAKES_IN_TREM + str(trem_min)
        html = get_html_from_cookie(url, cookie)
        pars_makes_in_trem_first(html, user, trem_min)

    user.is_all_makes_in_trem = True
    user.save()


# Обновление оценок в Текущем Триместре
def pars_makes_in_trem(html, user, trem):
    soup = BeautifulSoup(html.text, 'lxml')
    table = soup.find('div', class_='span9')

    makes = {}
    table_common = table.find('table', class_='common')
    table = table.find_all('h3')
    i = 0

    if EtisMakesInTrem.objects.filter(user_id=user.id, trem=trem):
        EtisMakesInTrem.objects.filter(user_id=user.id, trem=trem).delete()

    if EtisMakesInTrem.objects.all():
        id = EtisMakesInTrem.objects.filter().order_by('-id')[0].id + 1
    else:
        id = 0

    for discipline_in_table in table:
        discipline = discipline_in_table.text
        for make in enumerate(table_common.find_all('td')):
            if (len(makes) == 9):
                EtisMakesInTrem(id=id, discipline=discipline, tema=makes[0], type_of_work=makes[1],
                                type_of_control=makes[2], make=makes[3], passing_score=makes[4], max_score=makes[6],
                                date=makes[7], teacher=makes[8], trem=trem,
                                user_id=user.id).save()
                makes = {}
                i = 0
                id = id + 1
            makes[i] = make[1].text
            i = i + 1
        makes = {}
        i = 0
        table_common = table_common.findNext('table')


# Получение страницы по Куки
def get_html_from_cookie(url, cookie):
    session = requests.session()
    response = session.post(url, cookies=cookie)

    return response


# Получение новой Сессии
@csrf_exempt
def get_new_cookie(request):
    try:
        username = request.POST['username']
        password = request.POST['password']

        cookie = get_cookie(username=username, password=password)

        if len(cookie) == 0:
            return HttpResponse(status=403)  # Неверный пароль

        return JsonResponse({'cookie': cookie})
    except:
        return HttpResponse(status=404)


# Получение Сесси при первом заходе
def get_cookie(username, password):
    session = requests.session()
    data = {'p_username': username.encode('windows-1251'), 'p_password': password}
    r = session.post(BASE_URL_LOGIN, data=data)
    cookie = r.cookies.get_dict()

    return cookie


# Получение страницы по Логину и Паролю
def get_html(url, username, password):
    session = requests.session()
    data = {'p_username': username.encode('windows-1251'), 'p_password': password}
    r = session.post(BASE_URL_LOGIN, data=data)
    if not r.cookies._cookies:
        return 0
    response = session.post(url)

    return response


# Занесение информации по Оценка за Сесию
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


# Смена пароля в ЕТИС
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


# Обновление Оценок за Сесию
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


# Функция вызывается при первой Авторизации в ЕТИС
def add_fist_makes(cookie, user):
    html = get_html_from_cookie('https://student.psu.ru/pls/stu_cus_et/stu.signs?p_mode=session', cookie=cookie)
    threading.Thread(target=pars_makes_in_trems_first, args=(cookie, user)).start()
    parse_session(html.text, user)


# Получение ФИО в ЕТИС
def get_name_etis(username, password):
    html = get_html('https://student.psu.ru/pls/stu_cus_et/stu.signs?p_mode=session', username=username, password=password)

    soup = BeautifulSoup(html.text, 'lxml')
    name = soup.find('span', style="color: #808080;white-space:nowrap;").text
    name = name.partition('\n')[0]
    return name


# Генератор Ключа, Пока не используется
def generate_key():
    str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(30))
    key = make_password(str)
    return key


# Авторизация Пользователя
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
