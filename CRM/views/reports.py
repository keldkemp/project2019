from django_filters.views import FilterView
from django.shortcuts import render
from CRM.models import Worker, Time
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    RedirectView, TemplateView, UpdateView, CreateView, FormView,
    DetailView, DeleteView)
from rules.contrib.views import PermissionRequiredMixin
from CRM.forms import UserForm, UserUpdateForm
from CRM.filters import Reports
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
import datetime
from CRM.models import Salary, Prize


class List(PermissionRequiredMixin, FilterView):
    model = Worker
    queryset = model.objects.filter(is_superuser=False).order_by('status_id', 'last_name')
    filterset_class = Reports
    template_name = 'CRM/reports/list.html'
    context_object_name = 'workers'
    paginate_by = 25
    permission_required = 'manager'

    def get_permission_object(self):
        self.request.user
