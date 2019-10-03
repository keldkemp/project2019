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
