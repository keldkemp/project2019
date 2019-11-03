from django.db import models
from itertools import count
from django.contrib.auth import get_user_model
from transliterate import translit
from django.contrib.auth.models import AbstractUser, UserManager
from django.urls import reverse, reverse_lazy
from django.utils import timezone
import datetime
import pytz
from decimal import Decimal


class Status(models.Model):
    name_status = models.CharField('Статус работника', max_length=150)

    def __str__(self):
        return self.name_status


class Qualifiacation(models.Model):
    name_qualification = models.CharField('Квалификация работника', max_length=150)
    money_index = models.DecimalField('Индекс ЗП', max_digits=15, decimal_places=10)

    def get_absolute_url(self):
        return reverse('qualifications:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name_qualification


class Worker(AbstractUser):
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    patronymic = models.CharField('Отчество', max_length=150, null=True)
    phone_number = models.CharField('Телефон', max_length=50, null=True, blank=True)
    email = models.CharField('Email', max_length=255, null=True, blank=True)
    is_admin_user = models.BooleanField('Администратор', default=0)
    is_manager_user = models.BooleanField('Менеджер', default=0)
    is_worker_user = models.BooleanField('Работник', default=0)
    is_first_login = models.BooleanField('Первый вход в систему', default=0)
    is_online = models.BooleanField('Статус на сайте', default=0)
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name='Статус работника', null=True)
    qualifiacation = models.ForeignKey(Qualifiacation, on_delete=models.PROTECT, verbose_name='Квалификация', null=True)

    @property
    def is_admin(self) -> bool:
        if self.is_admin_user:
            return True
        return False

    @property
    def is_manager(self) -> bool:
        if self.is_manager_user:
            return True
        return False

    @property
    def is_worker(self) -> bool:
        if self.is_worker_user:
            return True
        return False

    @property
    def is_online_user(self) -> bool:
        if self.is_online:
            return True
        return False

    @property
    def is_command_status(self) -> bool:
        if self.status_id == 3:
            return True
        return False

    def update_online_status(self):
        if self.is_online_user or self.is_command_status:
            return
        self.is_online = True
        self.status_id = 1
        self.save()
        return

    def update_offline_status(self):
        if not self.is_online_user or self.is_command_status:
            return
        self.is_online = False
        self.status_id = 2
        self.save()
        return

    def update_command_status(self):
        if self.is_command_status:
            return
        self.status_id = 3
        self.save()

    def get_update_first_user_login(self):
        if not self.is_first_login:
            self.is_first_login = True
            self.save()

    def update_time_arrival(self):
        if not Time.objects.filter(time_of_arrival__range=(datetime.date.today(), datetime.date.today()+datetime.timedelta(days=1)), worker_id=self.id).exists():
            Time(worker_id=self.id, time_of_arrival=datetime.datetime.now(pytz.utc)).save()
            if self.is_command_status:
                self.status_id = 1
                self.save()

    def update_time_leaving(self):
        if self.is_command_status:
            return
        if not Time.objects.filter(time_of_arrival__range=(datetime.date.today(), datetime.date.today()+datetime.timedelta(days=1)), worker_id=self.id).exists():
            Time(worker_id=self.id, time_of_arrival=datetime.datetime.now(pytz.utc)).save()
        time = Time.objects.get(time_of_arrival__range=(datetime.date.today(), datetime.date.today()+datetime.timedelta(days=1)), worker_id=self.id)
        time.time_of_leaving = datetime.datetime.now(pytz.utc)
        time.time_per_day = (time.time_of_leaving - time.time_of_arrival).total_seconds() / 3600
        time.save()

    def create_send_to_mission(self, start_date, end_date):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_date = end_date + datetime.timedelta(hours=18)
        start_date = start_date + datetime.timedelta(hours=8)
        if Time.objects.filter(time_of_arrival__range=(datetime.date.today(), datetime.date.today()+datetime.timedelta(days=1)), worker_id=self.id).exists():
            time = Time.objects.get(
                time_of_arrival__range=(datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1)),
                worker_id=self.id)
        else:
            Time(worker_id=self.id, time_of_arrival=start_date, time_of_leaving=end_date).save()
            time = Time.objects.get(worker_id=self.id, time_of_arrival=start_date, time_of_leaving=end_date)
        time.time_of_leaving = end_date
        time.time_per_day = (time.time_of_leaving.day - time.time_of_arrival.day + 1) * 8
        time.save()

    def payment_money(self):
        users = Worker.objects.filter(is_superuser=False)
        for user in users:
            time_for_user = Time.objects.filter(worker_id=user.id)
            all_time_in_month = 0
            for time in time_for_user:
                all_time_in_month = time.time_per_day + all_time_in_month
            qualification = user.qualifiacation.money_index
            money = qualification * all_time_in_month
            Salary(worker_id=user.id, sum_salary=money).save()
        return True

    def generate_username(self, first_name: str, last_name: str, patronymic: str) -> str:
        first_name = first_name[0]
        patronymic = patronymic[0]

        trans_f = translit(first_name, language_code='ru', reversed=True)
        trans_l = translit(last_name, language_code='ru', reversed=True)
        trans_p = translit(patronymic, language_code='ru', reversed=True)

        if trans_l.find("'"):
            trans_l = trans_l.replace("'", '')

        name = f'{trans_l}.{trans_f}{trans_p}'.lower()

        if not Worker.objects.filter(username=name).exists():
            return name

        for idx in range(2, 100, 1):
            name_change = ''.join([name, str(idx)])
            if not Worker.objects.filter(username=name_change).exists():
                return ''.join([name, str(idx)])

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'pk': self.pk})


class Salary(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT, verbose_name='Работник')
    sum_salary = models.DecimalField('Сумма денег за период', max_digits=15, decimal_places=2)
    date_accruals = models.DateField('Дата начисления', default=timezone.now)


class Time(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name='Работник')
    time_of_arrival = models.DateTimeField('Время прихода', default=timezone.now)
    time_of_leaving = models.DateTimeField('Время ухода', null=True)
    time_per_day = models.DecimalField('Время за день', null=True, max_digits=15, decimal_places=10)
