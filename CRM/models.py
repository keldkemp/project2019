from django.db import models
from itertools import count
from django.contrib.auth import get_user_model
from transliterate import translit
from django.contrib.auth.models import AbstractUser, UserManager
from django.urls import reverse, reverse_lazy
from django.utils import timezone


class Status(models.Model):
    name_status = models.CharField('Статус работника', max_length=150)

    def __str__(self):
        return self.name_status


class Qualifiacation(models.Model):
    name_qualification = models.CharField('Квалификация работника', max_length=150)
    money_index = models.DecimalField('Индекс ЗП', max_digits=15, decimal_places=10)

    def __str__(self):
        return self.name_qualification


class Worker(AbstractUser):
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    patronymic = models.CharField('Отчество', max_length=150, null=True, blank=True)
    phone_number = models.CharField('Телефон', max_length=50, null=True, blank=True)
    email = models.CharField('Email', max_length=255, null=True, blank=True)
    is_admin_user = models.BooleanField('Администратор', default=0)
    is_manager_user = models.BooleanField('Менеджер', default=0)
    is_worker_user = models.BooleanField('Работник', default=0)
    is_first_login = models.BooleanField('Первый вход в систему', default=0)
    status = models.ForeignKey(Status, on_delete=models.PROTECT, verbose_name='Статус работника', null=True)
    qualifiacation = models.ForeignKey(Qualifiacation, on_delete=models.PROTECT, verbose_name='Квалификация', null=True)

    @property
    def is_admin(self) -> bool:
        if self.is_admin_user:
            return True

    @property
    def is_manager(self) -> bool:
        if self.is_manager_user:
            return True

    @property
    def is_worker(self) -> bool:
        if self.is_worker_user:
            return True

    def get_update_first_user_login(self):
        if not self.is_first_login:
            self.is_first_login = True
            self.save()


class Salary(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT, verbose_name='Работник')
    sum_salary = models.DecimalField('Сумма денег за период', max_digits=15, decimal_places=2)
    date_accruals = models.DateField('Дата начисления', default=timezone.now)


class Time(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT, verbose_name='Работник')
    time_of_arrival = models.DateTimeField('Время прихода', default=timezone.now)
    time_of_leaving = models.DateTimeField('Время ухода', null=True)
    time_per_day = models.DecimalField('Время за день', null=True, max_digits=15, decimal_places=10)
