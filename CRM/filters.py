import django_filters
from django import forms
from django.http import QueryDict
from django_select2.forms import Select2MultipleWidget

from CRM import models


class UsersFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        label='Искать по ФИО',
        lookup_expr='icontains'
    )

    class Meta:
        model = models.Worker
        fields = ('last_name',)
        order_by_field = 'last_name'


class QualificationsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        label='Искать по должности',
        lookup_expr='icontains'
    )

    class Meta:
        model = models.Qualifiacation
        fields = ('name_qualification',)


class Reports(django_filters.FilterSet):
    worker = django_filters.ModelMultipleChoiceFilter(
        label='Работники:',
        field_name='username',
        queryset=models.Worker.objects.filter(is_superuser=False),
        widget=Select2MultipleWidget
    )
    qualification = django_filters.ModelMultipleChoiceFilter(
        label='Должность:',
        field_name='qualifiacation__name_qualification',
        queryset=models.Qualifiacation.objects.all(),
        widget=Select2MultipleWidget
    )
    status = django_filters.ModelMultipleChoiceFilter(
        label='Статус:',
        field_name='status__name_status',
        queryset=models.Status.objects.all(),
        widget=Select2MultipleWidget
    )

