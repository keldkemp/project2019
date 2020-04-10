from django.contrib import admin
from CRM import models
from django.contrib.auth.forms import (
    UserChangeForm, UserCreationForm, UsernameField,
)
from django.contrib.auth.admin import UserAdmin


class TenantUserCreateForm(UserCreationForm):
    class Meta:
        models = models.Worker
        fields = ('username',)
        field_classes = {'username': UsernameField}


class TenantUserChangeForm(UserChangeForm):
    class Meta:
        models = models.Worker
        fields = '__all__'
        field_classes = {'username': UsernameField}


@admin.register(models.Worker)
class TenantUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'patronymic',
                                        'is_admin_user',
                                        'qualifiacation')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    form = TenantUserChangeForm
    add_form = TenantUserCreateForm


@admin.register(models.Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('worker', 'sum_salary', 'date_accruals')


@admin.register(models.Time)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('worker', 'time_of_arrival', 'time_of_leaving', 'time_per_day')


@admin.register(models.EtisUsers)
class EtisUsersAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'password')
