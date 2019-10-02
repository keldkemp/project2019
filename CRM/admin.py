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
